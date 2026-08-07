"""LangGraph nodes for the Job Matcher agent.

Rewritten: all 10 positions with 7-dimension profiles serve as RAG knowledge base.
LLM directly scores user profile against each position, then ranks.
Data cached in Redis for instant access.
"""

import json
import logging
from typing import Dict

from app.agents.job_matcher.state import JobMatcherState
from app.agents.job_matcher import db_utils
from app.agents.job_matcher.scorer import MatchScorer
from app.agents.retry import SubModuleTracer
from app.db.neo4j import neo4j_manager

logger = logging.getLogger(__name__)

# Redis key for the 10-position knowledge base
KB_CACHE_KEY = "cache:matching:kb"
KB_CACHE_TTL = 3600


async def _load_knowledge_base():
    """Load 10 positions x 7 dimensions from Redis cache or DB."""
    # Try Redis first
    try:
        from app.db.redis import get_redis
        r = await get_redis()
        raw = await r.get(KB_CACHE_KEY)
        if raw:
            return json.loads(raw)
    except Exception:
        pass

    # Fallback: load from DB
    jobs = await db_utils.get_all_jobs_with_profiles()

    # Write to Redis
    try:
        from app.db.redis import get_redis
        r = await get_redis()
        await r.setex(KB_CACHE_KEY, KB_CACHE_TTL,
                       json.dumps(jobs, ensure_ascii=False, default=str))
        logger.info(f"[Match] KB cached to Redis: {len(jobs)} positions")
    except Exception:
        pass

    return jobs


async def load_user_profile(state: JobMatcherState) -> Dict:
    uid = state["user_id"]

    # If frontend sent profile data, use it directly
    input_profile = state.get("user_profile", {})
    if input_profile and input_profile.get("source") == "frontend":
        radar = input_profile.get("radar_data", [])
        if radar and any(v > 0 for v in radar):
            try:
                await db_utils.save_user_profile(uid, input_profile)
            except Exception:
                pass
            return {"user_profile": input_profile}

    # Otherwise read from database
    profile = await db_utils.get_user_profile(uid)
    if profile:
        pd = profile.get("profile_data", {})
        if isinstance(pd, str):
            try:
                pd = json.loads(pd)
            except Exception:
                pd = {}
        radar = pd.get("radar_data", [])
        if radar and any(v > 0 for v in radar):
            return {"user_profile": pd}
        return {"user_profile": {}, "error": "用户画像数据为空，请先在「职能助手」中完成对话分析"}

    if state.get("user_profile"):
        profile_data = state["user_profile"]
        await db_utils.save_user_profile(uid, profile_data)
        return {"user_profile": profile_data}

    return {"user_profile": {}, "error": "未找到用户画像，请先在「职能助手」中完成对话分析"}


async def retrieve_candidates(state: JobMatcherState) -> Dict:
    """Load ALL 10 positions (7-dim profiles) from Redis cache as knowledge base."""
    jobs = await _load_knowledge_base()
    print(f"[Match] KB loaded: {len(jobs)} positions")
    return {
        "candidate_job_ids": [str(j["id"]) for j in jobs],
        "all_jobs_with_profiles": jobs,
    }


async def load_job_details(state: JobMatcherState) -> Dict:
    """Use pre-loaded knowledge base directly."""
    jobs = state.get("all_jobs_with_profiles", [])
    if not jobs:
        ids = state.get("candidate_job_ids", [])
        if ids:
            details = await db_utils.get_job_details([int(i) for i in ids])
            return {"job_details": details}
        return {"job_details": [], "match_results": []}
    return {"job_details": jobs}


async def neo4j_enrich(state: JobMatcherState) -> Dict:
    """No-op: 7-dim data from job_profiles supersedes Neo4j."""
    jobs = state.get("job_details", [])
    logger.info(f"[Match] KB covers {len(jobs)} jobs, skipping Neo4j")
    return {"neo4j_profiles": []}


async def algorithmic_match(state: JobMatcherState) -> Dict:
    """LLM scores user profile against all 10 positions' 7-dim requirements.

    Builds a prompt with:
    - User's 7-dimension profile (radar scores + details)
    - All 10 positions with their 7-dimension requirements
    Then asks LLM to score and rank.
    """
    import asyncio
    from app.agents.job_matcher.prompts import build_batch_match_prompt
    from langchain_openai import ChatOpenAI
    from app.config import settings

    if state.get("error"):
        return {"match_results": []}

    profile = state.get("user_profile", {})
    jobs = state.get("job_details", [])

    if not jobs:
        return {"match_results": []}

    # Build prompt with user profile + all 10 positions' 7-dim data
    prompt = build_batch_match_prompt(profile, jobs)

    try:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.1,
        )
        resp = await llm.ainvoke(prompt)
        content = resp.content if hasattr(resp, "content") else str(resp)

        # Parse LLM JSON output
        try:
            # Strip markdown code fences if present
            if "```" in content:
                start = content.find("[")
                end = content.rfind("]") + 1
                content = content[start:end]
            results = json.loads(content)
        except json.JSONDecodeError:
            logger.error(f"[Match] LLM returned invalid JSON: {content[:500]}")
            return {"match_results": []}

        # Ensure proper structure
        match_results = []
        for r in results:
            match_results.append({
                "job_id": r.get("job_id"),
                "job_title": r.get("job_title", ""),
                "company": r.get("company", ""),
                "industry": r.get("industry", ""),
                "city": r.get("city", ""),
                "salary_range": r.get("salary_range", ""),
                "total_score": r.get("total_score", 0),
                "scores": r.get("scores", {}),
                "summary": r.get("summary", ""),
                "recommendations": r.get("recommendations", []),
            })

        match_results.sort(key=lambda x: x["total_score"], reverse=True)
        logger.info(f"[Match] LLM scored {len(match_results)} positions: "
                     f"{[(r['job_title'], r['total_score']) for r in match_results]}")
        return {"match_results": match_results}

    except Exception as e:
        logger.error(f"[Match] LLM scoring failed: {e}")

    # Fallback to algorithmic scoring if LLM fails
    scorer = MatchScorer()
    results = []
    for job in jobs:
        profile_data = job.get("profile_data", {})
        dims = profile_data.get("dimensions", {})
        # Build job_requirements from 7-dim data
        job_reqs = _build_job_reqs_from_profile(dims)
        try:
            score_result = scorer.compute_scores(profile, job_reqs, job_info=job)
        except Exception:
            score_result = {
                "total_score": 0, "scores": {},
                "summary": "评分异常", "recommendations": [],
            }
        results.append({
            "job_id": job.get("id"),
            "job_title": job.get("job_title", ""),
            "company": job.get("company", ""),
            "industry": job.get("industry", ""),
            "city": job.get("city", ""),
            "salary_range": job.get("salary_range", ""),
            **score_result,
        })

    results.sort(key=lambda r: r.get("total_score", 0), reverse=True)
    return {"match_results": results}


def _build_job_reqs_from_profile(dimensions: dict) -> dict:
    """Convert 7-dimension profile data to scorer-compatible format.

    Input: {"专业技能": ["item1", "item2", ...], "证书要求": [...], ...}
    Output: {"专业技能": {"expected_score": 70, "requirements": "item1; item2"}, ...}
    """
    DIM_MAP = {
        "专业技能": "专业技能",
        "证书要求": "证书资质",
        "创新能力": "创新能力",
        "学习能力": "学习能力",
        "抗压能力": "抗压能力",
        "沟通能力": "沟通能力",
        "实习能力": "实习/项目经验",
    }
    result = {}
    for src_dim, scorer_dim in DIM_MAP.items():
        items = dimensions.get(src_dim, [])
        result[scorer_dim] = {
            "expected_score": 70,
            "requirements": "; ".join(items[:3]) if items else "",
        }
    return result


async def rank_results(state: JobMatcherState) -> Dict:
    results = state.get("match_results", [])
    ranked = sorted(results, key=lambda r: r.get("total_score", 0), reverse=True)
    return {"ranked_results": ranked}


async def save_report(state: JobMatcherState) -> Dict:
    """Save match results to DB. Errors here must NOT crash the graph."""
    uid = state["user_id"]
    ranked = state.get("ranked_results", [])
    profile = state.get("user_profile", {})

    # Save each match result
    for r in ranked[:5]:
        try:
            await db_utils.save_match_report(
                user_id=uid,
                job_name=r.get("job_title", ""),
                match_score=float(r.get("total_score", 0)),
                report_data=r,
                industry=r.get("industry", ""),
                city=r.get("city", ""),
            )
        except Exception as e:
            logger.warning(f"[Match] save_report failed for {r.get('job_title', '?')}: {e}")

    # Save aggregate record with radar_data for cache-hit check
    try:
        await db_utils.save_match_report(
            user_id=uid,
            job_name="__all__",
            match_score=float(ranked[0].get("total_score", 0)) if ranked else 0,
            report_data={
                "radar_data": profile.get("radar_data", []),
                "matches": ranked,
            },
            industry="",
            city="",
        )
    except Exception as e:
        logger.warning(f"[Match] save aggregate failed: {e}")

    return {"report_id": 0}

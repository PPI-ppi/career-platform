import json
from fastapi import APIRouter, Query, Depends
from sqlalchemy import text
from app.db.mysql import get_db
from app.rag.retrievers import job_retriever
from app.config import settings

router = APIRouter()

JOBS_CACHE_KEY = "cache:jobs:list"
JOBS_CACHE_TTL = 3600  # Redis TTL 兜底，正常靠主动刷新


async def refresh_jobs_cache(db=None):
    """MySQL 写入后调用：立即查 DB 并写回 Redis。"""
    try:
        from app.db.redis import get_redis
        if db is None:
            from app.db.mysql import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                jobs = await _get_jobs_from_db(session)
        else:
            jobs = await _get_jobs_from_db(db)
        r = await get_redis()
        await r.setex(JOBS_CACHE_KEY, JOBS_CACHE_TTL, json.dumps(jobs, ensure_ascii=False, default=str))
    except Exception:
        pass  # Redis 不可用，请求时自动穿透 DB


async def _get_jobs_from_db(db):
    """从 MySQL 查全部岗位。"""
    result = await db.execute(
        text("SELECT id, job_title, company, industry, city, salary_range, company_scale, publish_date, job_description FROM jobs ORDER BY publish_date DESC")
    )
    return [dict(r._mapping) for r in result.fetchall()]


async def _cached_jobs(db):
    """Redis 缓存 → 穿透查 DB。"""
    # 先读 Redis
    try:
        from app.db.redis import get_redis
        r = await get_redis()
        raw = await r.get(JOBS_CACHE_KEY)
        if raw:
            return json.loads(raw)
    except Exception:
        pass  # Redis 挂了走 DB

    # 穿透查 DB
    jobs = await _get_jobs_from_db(db)

    # 写回 Redis
    try:
        from app.db.redis import get_redis
        r = await get_redis()
        await r.setex(JOBS_CACHE_KEY, JOBS_CACHE_TTL, json.dumps(jobs, ensure_ascii=False, default=str))
    except Exception:
        pass

    return jobs


@router.get("")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(200, le=500),
    keyword: str = Query(""),
    industry: str = Query(""),
    city: str = Query(""),
    db=Depends(get_db),
):
    """List jobs. RAG keyword search or cached DB list."""
    if keyword:
        results = job_retriever.search(keyword, top_k=200, industry=industry or None, city=city or None)
        seen = {}
        for r in results:
            title = (r.job_title or "").strip()
            if not title:
                continue
            if title not in seen or r.score > seen[title]["score"]:
                seen[title] = {
                    "id": int(r.id), "job_title": r.job_title, "company": r.company,
                    "industry": r.industry, "city": r.city, "salary_range": r.salary_range,
                    "company_scale": r.metadata.get("company_scale", "") if r.metadata else "",
                    "job_description": r.metadata.get("job_description", "") if r.metadata else "",
                    "score": r.score,
                }
        deduped = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
        return {"success": True, "jobs": deduped[:page_size], "source": "vector"}

    jobs = await _cached_jobs(db)
    return {"success": True, "jobs": jobs, "source": "redis" if settings.DB_BACKEND == "mysql" else "sql"}


@router.get("/search")
async def search_jobs(q: str = Query(""), top_k: int = Query(50)):
    """Semantic job search via RAG with title deduplication."""
    results = job_retriever.search(q, top_k=top_k * 5)  # fetch more for dedup
    seen = {}
    for r in results:
        title = (r.job_title or "").strip()
        if not title:
            continue
        if title not in seen or r.score > seen[title]["score"]:
            seen[title] = {
                "id": int(r.id), "job_title": r.job_title, "company": r.company,
                "industry": r.industry, "city": r.city, "salary_range": r.salary_range,
                "company_scale": r.metadata.get("company_scale", "") if r.metadata else "",
                "score": r.score,
            }
    deduped = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return {"success": True, "jobs": deduped[:top_k]}


@router.get("/hot")
async def hot_jobs(db=Depends(get_db)):
    """Top 10 most recent jobs."""
    result = await db.execute(
        text("SELECT id, job_title, company, industry, city, salary_range, company_scale FROM jobs ORDER BY publish_date DESC LIMIT 10")
    )
    return {"success": True, "jobs": [dict(r._mapping) for r in result.fetchall()]}


@router.get("/{job_id}")
async def get_job_detail(job_id: int, db=Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM jobs WHERE id = :jid"), {"jid": job_id}
    )
    row = result.fetchone()
    if not row:
        return {"success": False, "error": "Job not found"}
    return {"success": True, "job": dict(row._mapping)}

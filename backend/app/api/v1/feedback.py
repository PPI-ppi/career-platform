"""Feedback & Review Center API — LLM-powered feedback based on user profile."""
import json
import logging
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.middleware.auth import get_current_user
from app.db.mysql import AsyncSessionLocal
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

DIM_NAMES = ["专业技能", "创新能力", "学习能力", "实习能力", "抗压能力", "沟通能力", "证书"]

FB_CACHE_TTL = 600  # 10 分钟缓存

FEEDBACK_PROMPT = """你是一个学习反馈顾问。根据用户的七维能力画像，对下面的每个任务生成专属的四段反馈。

用户画像：
{profile_text}

目标岗位：{target_job}

请对以下每个任务生成反馈：

{tasks_text}

每个任务返回四个字段：
- task_id: 任务ID（必须与输入一致）
- problem: 问题定位（指出完成/攻克这个任务时的具体难点和不足，结合用户画像相关维度）
- suggestion: 改进建议（针对该任务的具体学习方法或资源）
- next: 下一步（基于该任务的后续练习或行动）
- weakness: 薄弱分析（这个任务暴露了用户哪个维度的薄弱点，及该薄弱点的具体表现）

输出一个 JSON 数组，不要包含 markdown 代码块：
[{{"task_id": 1, "problem": "...", "suggestion": "...", "next": "...", "weakness": "..."}}]"""


@router.get("")
async def get_feedback(user: dict = Depends(get_current_user)):
    uid = user["user_id"]
    today = date.today()

    cache_key = f"cache:feedback:{uid}"

    # Redis 缓存命中 → 直接返回（10分钟有效）
    try:
        from app.db.redis import get_redis
        r = await get_redis()
        raw = await r.get(cache_key)
        if raw:
            return json.loads(raw)
    except Exception:
        pass

    async with AsyncSessionLocal() as db:
        # === Metrics ===
        total = await db.execute(
            text("SELECT COUNT(*) FROM daily_tasks WHERE user_id = :uid AND status = 'completed'"),
            {"uid": uid})
        total_submissions = total.scalar() or 0

        avg_score = await db.execute(
            text("SELECT AVG(match_score) FROM matching_report WHERE user_id = :uid"),
            {"uid": uid})
        avg_val = avg_score.scalar()
        avg_rating = round(avg_val, 1) if avg_val else 0

        # Active streak
        active_result = await db.execute(
            text("SELECT DISTINCT DATE(created_at) as d FROM daily_tasks "
                 "WHERE user_id = :uid AND status = 'completed' ORDER BY d DESC"),
            {"uid": uid})
        active_days = [row[0] for row in active_result.fetchall()]
        streak = _calc_streak(active_days, today)

        # === Profile & weak dimensions ===
        profile = {}
        weak_dim_names = []
        profile_result = await db.execute(
            text("SELECT profile_data FROM user_profiles WHERE user_id = :uid AND status = 'active'"),
            {"uid": uid})
        profile_row = profile_result.fetchone()
        if profile_row:
            pd = profile_row[0]
            if isinstance(pd, str):
                try: pd = json.loads(pd)
                except Exception: pd = {}
            profile = pd

        radar = profile.get("radar_data", [])
        details = profile.get("dimension_details", {})

        weak_tags = []
        for i, name in enumerate(DIM_NAMES):
            score = radar[i] if i < len(radar) else 0
            detail = details.get(name, {})
            desc = detail.get("desc", "") if isinstance(detail, dict) else ""
            weak_tags.append({
                "text": name, "highlight": score < 75,
                "score": score, "desc": desc[:60] if desc else "",
            })
            if score < 80:
                weak_dim_names.append(name)

        # === Timeline events: task status transitions from task_status_log ===
        events = []

        task_logs = await db.execute(
            text("SELECT task_id, task_title, old_status, new_status, created_at "
                 "FROM task_status_log WHERE user_id = :uid ORDER BY created_at DESC LIMIT 20"),
            {"uid": uid})
        task_rows = task_logs.fetchall()
        for row in task_rows:
            tid, title, old_s, new_s, created = row
            d = _to_date(created)
            wd = _weekday(d)
            st_label = {"pending": "待开始", "in_progress": "进行中", "completed": "已完成"}.get(new_s, new_s)
            events.append({
                "date": str(d), "weekday": wd,
                "title": title or f"任务 {tid}",
                "type": "task",
                "task_id": tid,
                "status": new_s,
                "statusLabel": st_label,
                "problem": f"任务「{title}」状态变更为{st_label}",
                "suggestion": "",
                "next": "",
            })

        events.sort(key=lambda e: e["date"], reverse=True)

        # LLM 反馈单独放（不进时间线，时间线只展示任务状态节点）
        llm_feedback = []
        if weak_dim_names:
            try:
                llm_feedback = await _generate_feedback_events(profile, weak_dim_names, task_rows)
            except Exception as e:
                logger.warning(f"[Feedback] LLM generation failed: {e}")

        # === Trend ===
        trend_data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_result = await db.execute(
                text("SELECT COUNT(*) FROM daily_tasks "
                     "WHERE user_id = :uid AND status = 'completed' AND DATE(created_at) = :d"),
                {"uid": uid, "d": str(d)})
            trend_data.append(day_result.scalar() or 0)

        # Top weak point
        if weak_tags:
            weakest = min(weak_tags, key=lambda t: t["score"])
            weak_label = weakest["text"]
        else:
            weak_label = "待采集"

        target_job = ""
        selected = await db.execute(
            text("SELECT job_data FROM user_selected_job WHERE user_id = :uid"), {"uid": uid})
        sel_row = selected.fetchone()
        if sel_row:
            jd = sel_row[0]
            if isinstance(jd, str):
                try: jd = json.loads(jd)
                except Exception: pass
            target_job = jd.get("job_title", "") if isinstance(jd, dict) else ""

    resp = {
        "success": True,
        "data": {
            "metrics": [
                {"value": str(total_submissions), "label": "总提交次数"},
                {"value": str(avg_rating), "label": "平均匹配评分"},
                {"value": weak_label, "label": "最大薄弱维度"},
                {"value": f"{streak}天", "label": "连续活跃天数"},
            ],
            "weak_tags": weak_tags,
            "trend": trend_data,
            "events": events[:20],
            "llm_feedback": llm_feedback,
            "target_job": target_job,
        },
    }

    # 写 Redis 缓存（10分钟有效）
    try:
        from app.db.redis import get_redis
        r = await get_redis()
        await r.setex(cache_key, FB_CACHE_TTL, json.dumps(resp, ensure_ascii=False, default=str))
    except Exception:
        pass

    return resp


def _to_date(val):
    return val.date() if hasattr(val, "date") else val

def _weekday(d):
    try: return ["周一","周二","周三","周四","周五","周六","周日"][d.weekday()]
    except Exception: return ""

def _calc_streak(days, today):
    if not days: return 0
    s, check = 0, today
    for d in days:
        d = d if isinstance(d, date) else date.fromisoformat(str(d))
        if d == check:
            if s == 0: s = 1
        elif d == check - timedelta(days=1):
            s += 1; check = d
        else:
            break
    return s


async def _generate_feedback_events(profile, weak_dims, task_rows):
    """Use LLM to generate per-task problem/suggestion/next/weakness."""
    from langchain_openai import ChatOpenAI

    # Build profile text
    radar = profile.get("radar_data", [])
    details = profile.get("dimension_details", {})
    lines = []
    for i, name in enumerate(DIM_NAMES):
        score = radar[i] if i < len(radar) else 0
        d = details.get(name, {})
        desc = d.get("desc", "") if isinstance(d, dict) else ""
        lines.append(f"- {name}: {score}/100 {desc}")
    profile_text = "\n".join(lines)

    # Build tasks text from task_status_log rows
    task_lines = []
    for row in task_rows[:10]:
        tid, title, old_s, new_s, created = row
        task_lines.append(f"- task_id={tid}: {title}")
    tasks_text = "\n".join(task_lines) if task_lines else "暂无任务"

    prompt = FEEDBACK_PROMPT.format(
        profile_text=profile_text,
        tasks_text=tasks_text,
        target_job="待定",
    )

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0.3,
    )
    resp = await llm.ainvoke(prompt)
    content = resp.content if hasattr(resp, "content") else str(resp)

    # Parse JSON
    try:
        if "```" in content:
            start = content.find("[")
            end = content.rfind("]") + 1
            content = content[start:end]
        items = json.loads(content)
    except json.JSONDecodeError:
        content = content.strip()
        items = json.loads(content) if content.startswith("[") else []

    events = []
    for item in items:
        events.append({
            "task_id": item.get("task_id"),
            "date": str(date.today()),
            "weekday": _weekday(date.today()),
            "title": item.get("title", "任务反馈"),
            "type": "feedback",
            "status": "active",
            "statusLabel": "需关注",
            "problem": item.get("problem", ""),
            "suggestion": item.get("suggestion", ""),
            "next": item.get("next", ""),
            "weakness": item.get("weakness", ""),
        })

    return events

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

FEEDBACK_PROMPT = """你是一个学习反馈顾问。根据用户的七维能力画像和最近的实训活动，为每个薄弱维度生成具体的反馈。

用户画像：
{profile_text}

近期任务活动：
{activity_text}

目标岗位：{target_job}

请对用户在以下薄弱维度上生成反馈，每个维度一条：

{weak_dims}

每条反馈包含三个字段：
- dimension: 所属维度名称
- problem: 问题定位（一句话指出具体薄弱点，引用画像中的技能缺失或任务中的不足）
- suggestion: 改进建议（具体的行动建议，可引用学习资源）
- next: 下一步（可执行的下一步任务）

输出一个 JSON 数组，不要包含 markdown 代码块：
[{{"dimension": "专业技能", "problem": "...", "suggestion": "...", "next": "..."}}]"""


@router.get("")
async def get_feedback(user: dict = Depends(get_current_user)):
    uid = user["user_id"]
    today = date.today()

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

        # === Timeline events ===
        events = []

        # 1) Status-transition events from daily_tasks
        tasks = await db.execute(
            text("SELECT title, status, description, created_at FROM daily_tasks "
                 "WHERE user_id = :uid ORDER BY created_at DESC LIMIT 12"),
            {"uid": uid})
        task_rows = tasks.fetchall()
        for row in task_rows:
            title, status, desc, created = row
            d = _to_date(created)
            wd = _weekday(d)
            st_label = {"pending": "待开始", "in_progress": "进行中", "completed": "已完成"}.get(status, status)
            events.append({
                "date": str(d), "weekday": wd,
                "title": title,
                "type": "task",
                "status": status,
                "statusLabel": st_label,
                "problem": desc or f"任务「{title}」当前状态：{st_label}",
                "suggestion": "",
                "next": "",
            })

        # 2) Matching events
        matches = await db.execute(
            text("SELECT job_name, match_score, created_at FROM matching_report "
                 "WHERE user_id = :uid ORDER BY created_at DESC LIMIT 5"),
            {"uid": uid})
        for row in matches.fetchall():
            job_name, score, created = row
            d = _to_date(created)
            wd = _weekday(d)
            events.append({
                "date": str(d), "weekday": wd,
                "title": f"人岗匹配 → {job_name}",
                "type": "match",
                "status": "completed",
                "statusLabel": f"{score}分",
                "problem": f"与「{job_name}」匹配度 {score} 分",
                "suggestion": "",
                "next": "",
            })

        events.sort(key=lambda e: e["date"], reverse=True)

        # 3) LLM-generated feedback for weak dimensions
        if weak_dim_names and events:
            try:
                llm_events = await _generate_feedback_events(profile, weak_dim_names, task_rows)
                # Prepend LLM events (they come first as strategic feedback)
                events = llm_events + events
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

    return {
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
            "events": events[:15],
            "target_job": target_job,
        },
    }


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
    """Use LLM to generate problem/suggestion/next for weak dimensions."""
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

    # Build activity text
    act_lines = []
    for row in task_rows[:8]:
        title, status, desc, created = row
        st = {"pending":"待","in_progress":"进行中","completed":"完成"}.get(status, status)
        act_lines.append(f"- [{st}] {title}")
    activity_text = "\n".join(act_lines) if act_lines else "暂无近期活动"

    weak_text = "\n".join(f"- {d}" for d in weak_dims)

    prompt = FEEDBACK_PROMPT.format(
        profile_text=profile_text,
        activity_text=activity_text,
        target_job="待定",
        weak_dims=weak_text,
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
            "date": str(date.today()),
            "weekday": _weekday(date.today()),
            "title": f"{item.get('dimension', '')} — 薄弱点分析",
            "type": "feedback",
            "status": "active",
            "statusLabel": "需关注",
            "problem": item.get("problem", ""),
            "suggestion": item.get("suggestion", ""),
            "next": item.get("next", ""),
            "dimension": item.get("dimension", ""),
        })

    return events

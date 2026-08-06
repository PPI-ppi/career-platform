import json
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy import text
from app.agents.harness import harness
from app.middleware.auth import get_current_user
from app.schemas.resume import ResumeExtractRequest
from app.config import settings
from app.db.mysql import AsyncSessionLocal

router = APIRouter()


async def _save_user_profile(user_id: int, result: dict):
    """Persist radar_data + dimension_details to user_profiles."""
    if not result.get("success") or not result.get("data"):
        return
    data = result["data"]
    radar = data.get("radar_data") or data.get("radar")
    details = data.get("dimension_details") or data.get("details")
    if not radar:
        return
    profile = {
        "radar_data": radar,
        "dimension_details": details or {},
    }
    pd = json.dumps(profile, ensure_ascii=False)
    async with AsyncSessionLocal() as db:
        if settings.DB_BACKEND == "sqlite":
            await db.execute(
                text("INSERT OR REPLACE INTO user_profiles (user_id, profile_data, status, updated_at) "
                     "VALUES (:uid, :pd, 'active', datetime('now'))"),
                {"uid": user_id, "pd": pd},
            )
        else:
            await db.execute(
                text("INSERT INTO user_profiles (user_id, profile_data, status) "
                     "VALUES (:uid, :pd, 'active') "
                     "ON DUPLICATE KEY UPDATE profile_data = :pd2, updated_at = NOW()"),
                {"uid": user_id, "pd": pd, "pd2": pd},
            )
        await db.commit()


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    """Load persisted user profile from MySQL."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT profile_data FROM user_profiles WHERE user_id = :uid AND status = 'active'"),
            {"uid": user["user_id"]},
        )
        row = result.fetchone()
    if not row:
        return {"success": True, "data": None}
    pd = row[0]
    if isinstance(pd, str):
        try:
            pd = json.loads(pd)
        except Exception:
            pd = {}
    return {"success": True, "data": pd}


async def save_upload(upload: UploadFile | None) -> str:
    if not upload or not upload.filename:
        return ""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(upload.filename)[1]
    path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(await upload.read())
    return path


@router.post("/extract")
async def extract_resume(
    input_text: str = Form(""),
    doc: UploadFile = File(None),
    image: UploadFile = File(None),
    user: dict = Depends(get_current_user),
):
    result = await harness.run(
        "resume_analyzer",
        {
            "input_text": input_text,
            "file_path": await save_upload(doc),
            "image_path": await save_upload(image),
            "user_id": user["user_id"],
        },
        user_id=user["user_id"],
    )
    await _save_user_profile(user["user_id"], result)
    return result


@router.post("/supplement")
async def supplement_resume(
    req: ResumeExtractRequest,
    user: dict = Depends(get_current_user),
):
    result = await harness.run(
        "resume_analyzer",
        {
            "input_text": "",
            "supplement_text": req.supplement_text,
            "supplement_count": req.supplement_count,
            "user_profile": req.user_profile,
            "user_id": user["user_id"],
        },
        user_id=user["user_id"],
    )
    await _save_user_profile(user["user_id"], result)
    return result


@router.post("/analyze")
async def analyze_resume(
    req: ResumeExtractRequest,
    user: dict = Depends(get_current_user),
):
    """Force a full analysis with an existing user_profile (completeness forced to 100%)."""
    result = await harness.run(
        "resume_analyzer",
        {
            "input_text": json.dumps(req.user_profile or {}, ensure_ascii=False),
            "user_id": user["user_id"],
        },
        user_id=user["user_id"],
    )
    await _save_user_profile(user["user_id"], result)
    return result


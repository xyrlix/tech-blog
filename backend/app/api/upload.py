"""图片上传 API"""
import uuid, os, aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["上传"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../../../frontend/public/img")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.post("/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "不支持的图片格式")
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.abspath(os.path.join(UPLOAD_DIR, filename))
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(await file.read())
    return {"url": f"/img/{filename}"}

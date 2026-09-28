from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies import get_current_user, request_id
from app.core.config import settings
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.user import User
from app.services.storage_service import photo_storage


router = APIRouter()


@router.post("/ticket-photo", status_code=status.HTTP_201_CREATED)
async def upload_ticket_photo(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    current_request_id: str = Depends(request_id),
):
    del user
    chunks = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > settings.max_upload_size_bytes:
            raise AppError(413, "UPLOAD_TOO_LARGE", "图片不能超过{}MB".format(settings.max_upload_size_mb))
        chunks.append(chunk)
    if total == 0:
        raise AppError(415, "UPLOAD_TYPE_NOT_SUPPORTED", "上传文件为空")
    result = photo_storage.save_image(b"".join(chunks))
    return success_response(result, current_request_id, "图片上传成功")


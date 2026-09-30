from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import request_id
from app.core.responses import success_response
from app.db.session import get_db
from app.services.storage_service import photo_storage


router = APIRouter()


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    current_request_id: str = Depends(request_id),
):
    db.execute(text("SELECT 1"))
    storage_ready = photo_storage.healthcheck()
    return success_response(
        {
            "status": "ok" if storage_ready else "degraded",
            "database": "connected",
            "storage": "connected" if storage_ready else "unavailable",
        },
        current_request_id,
        "服务运行正常",
    )

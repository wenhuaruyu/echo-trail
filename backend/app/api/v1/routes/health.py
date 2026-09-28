from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import request_id
from app.core.responses import success_response
from app.db.session import get_db


router = APIRouter()


@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    current_request_id: str = Depends(request_id),
):
    db.execute(text("SELECT 1"))
    return success_response(
        {"status": "ok", "database": "connected"},
        current_request_id,
        "服务运行正常",
    )


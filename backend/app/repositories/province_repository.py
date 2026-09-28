from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.province import Province


def list_provinces(db: Session) -> List[Province]:
    return list(db.scalars(select(Province).order_by(Province.name)).all())


def get_province(db: Session, province_code: str) -> Optional[Province]:
    return db.get(Province, province_code)


from typing import List, Optional

from pydantic import BaseModel


class ProvinceOut(BaseModel):
    code: str
    name: str
    slogan: Optional[str]
    status: str
    lighting_status: str = "unlit"
    collected_types: List[str] = []
    collected_type_count: int = 0
    ticket_count: int = 0


class ProvinceSummary(BaseModel):
    lit_province_count: int = 0
    ticket_count: int = 0


class ProvinceListOut(BaseModel):
    items: List[ProvinceOut]
    summary: ProvinceSummary


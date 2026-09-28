from typing import Dict, Optional

from app.models.province import Province


def serialize_province(
    province: Province,
    stats: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    payload = {
        "code": province.code,
        "name": province.name,
        "slogan": province.slogan,
        "status": province.status,
        "lighting_status": "unlit",
        "collected_types": [],
        "collected_type_count": 0,
        "ticket_count": 0,
    }
    if stats:
        payload.update(stats)
    return payload

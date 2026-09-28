from typing import Dict

from app.models.province import Province


def serialize_province(province: Province) -> Dict[str, object]:
    return {
        "code": province.code,
        "name": province.name,
        "slogan": province.slogan,
        "status": province.status,
        "lighting_status": "unlit",
        "collected_types": [],
        "collected_type_count": 0,
        "ticket_count": 0,
    }


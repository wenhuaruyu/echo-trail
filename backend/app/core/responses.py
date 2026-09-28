from typing import Any, Dict, Optional


def success_response(
    data: Any,
    request_id: str,
    message: str = "请求成功",
) -> Dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "message": message,
        "request_id": request_id,
    }


def error_response(
    message: str,
    error_code: str,
    request_id: str,
    data: Optional[Any] = None,
) -> Dict[str, Any]:
    return {
        "success": False,
        "data": data,
        "message": message,
        "error_code": error_code,
        "request_id": request_id,
    }


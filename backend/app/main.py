import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.core.responses import error_response
from app.services.storage_service import photo_storage


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="寻声觅迹 ECHO TRAIL 黑客松 MVP 后端",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.message, exc.error_code, request.state.request_id, exc.data),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(
            "请求参数格式错误",
            "REQUEST_INVALID",
            request.state.request_id,
            exc.errors(),
        ),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    del exc
    return JSONResponse(
        status_code=500,
        content=error_response("服务器内部错误", "INTERNAL_ERROR", request.state.request_id),
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount("/media/ticket-photos", StaticFiles(directory=photo_storage.directory), name="ticket-photos")

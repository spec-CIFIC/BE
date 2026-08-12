from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exception.constant.common import CommonErrorCode
from app.exception.exception import CificException


def register_exception_handlers(app) -> None:
    @app.exception_handler(CificException)
    async def cific_handler(request: Request, exc: CificException):
        headers = {"WWW-Authenticate": "Bearer"} if exc.error_code.status == 401 else {}
        return JSONResponse(
            status_code=exc.error_code.status,
            content={"code": exc.error_code.code, "message": exc.error_code.message},
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "code": CommonErrorCode.INVALID_REQUEST.code,
                "message": CommonErrorCode.INVALID_REQUEST.message,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "code": CommonErrorCode.INTERNAL_SERVER_ERROR.code,
                "message": CommonErrorCode.INTERNAL_SERVER_ERROR.message,
            },
        )

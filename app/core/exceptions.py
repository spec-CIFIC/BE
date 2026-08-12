from fastapi import Request
from fastapi.responses import JSONResponse


class CificException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class NotFoundException(CificException):
    pass


class UnauthorizedException(CificException):
    pass


class ExpiredTokenException(UnauthorizedException):
    pass


class InvalidTokenException(UnauthorizedException):
    pass


def register_exception_handlers(app) -> None:
    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_handler(request: Request, exc: UnauthorizedException):
        return JSONResponse(
            status_code=401,
            content={"detail": exc.detail},
            headers={"WWW-Authenticate": "Bearer"},
        )

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.response import error_response


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.detail,
            code=exc.status_code
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    return JSONResponse(
        status_code=422,
        content=error_response(
            message="请求参数验证失败",
            details=exc.errors(),
            code=422
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="服务器内部错误",
            details=str(exc) if __debug__ else None,
            code=500
        )
    )


def setup_exception_handlers(app):
    """设置异常处理器"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

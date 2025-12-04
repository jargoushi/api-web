from fastapi import Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common.response import error_response


# ---------- 自定义业务异常 ----------
class BusinessException(Exception):
    """通用的业务逻辑异常"""

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ---------- 异常处理器 ----------
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.code,
        content=jsonable_encoder(error_response(message=exc.message, code=exc.code))
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response(message=exc.detail, code=exc.status_code))
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        field_path = " -> ".join(str(item) for item in error["loc"])
        error_messages.append(f"字段 '{field_path}' 错误: {error['msg']}")
    final_message = "; ".join(error_messages)

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(error_response(message=final_message, code=422))
    )


async def general_exception_handler(request: Request, exc: Exception):
    message = "服务器内部错误" if not __debug__ else f"服务器内部错误: {str(exc)}"
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response(message=message, code=500))
    )


def setup_exception_handlers(app):
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

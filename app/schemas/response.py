from datetime import datetime
from typing import Generic, TypeVar, Optional, Any

from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """通用API响应模型"""
    success: bool = Field(True, description="请求是否成功")
    code: int = Field(200, description="业务状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")


def success_response(data: T = None, message: str = "操作成功", code: int = 200) -> ApiResponse[T]:
    """创建成功响应"""
    return ApiResponse(
        success=True,
        code=code,
        message=message,
        data=data
    )


def error_response(message: str = "操作失败", code: int = 500, details: Any = None) -> dict:
    """创建错误响应"""
    return {
        "success": False,
        "code": code,
        "message": message,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }

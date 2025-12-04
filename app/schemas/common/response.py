from datetime import datetime
from typing import Generic, TypeVar, Optional

from pydantic import Field
from tortoise.queryset import QuerySet

from app.schemas.common.base import BaseResponseModel
from app.schemas.common.pagination import PageResponse, PageRequest

T = TypeVar('T')


class ApiResponse(BaseResponseModel, Generic[T]):
    """通用API响应模型"""
    success: bool = Field(True, description="请求是否成功")
    code: int = Field(200, description="业务状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")


def success_response(data: T = None, code: int = 200) -> ApiResponse[T]:
    """创建成功响应"""
    return ApiResponse[T](
        success=True,
        code=code,
        data=data
    )


def error_response(message: str = "操作失败", code: int = 500) -> ApiResponse[None]:
    """创建错误响应，统一返回 ApiResponse 对象"""
    return ApiResponse[None](
        success=False,
        code=code,
        message=message,
        data=None
    )


async def paginated_response(
        query: QuerySet,
        params: PageRequest
) -> ApiResponse[PageResponse[T]]:
    """
    创建分页响应的工具函数

    Args:
        query: TortoiseORM 的 QuerySet
        params: 分页参数对象

    Returns:
        包装在 ApiResponse 中的 PageResponse
    """
    total = await query.count()
    items = await query.offset(params.offset).limit(params.size)

    # 计算总页数
    pages = (total + params.size - 1) // params.size

    paginated_data = PageResponse[T](
        total=total,
        page=params.page,
        size=params.size,
        pages=pages,
        items=items
    )

    return success_response(data=paginated_data)

from typing import Generic, TypeVar, List

from pydantic import BaseModel, Field

T = TypeVar('T')


class PageRequest(BaseModel):
    """分页请求参数模型"""
    page: int = Field(1, ge=1, description="当前页码，从1开始")
    size: int = Field(10, ge=1, le=100, description="每页数量，最大100")

    @property
    def offset(self) -> int:
        """计算数据库查询的偏移量"""
        return (self.page - 1) * self.size


class PageResponse(BaseModel, Generic[T]):
    """分页数据模型，不包含外层的 success/message"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
    items: List[T] = Field(..., description="当前页的数据列表")

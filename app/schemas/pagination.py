from typing import Generic, TypeVar, List

from pydantic import Field

from app.schemas.base import BaseRequestModel, BaseResponseModel

T = TypeVar('T')


class PageRequest(BaseRequestModel):
    """分页请求参数模型"""
    page: int = Field(1, ge=1, description="当前页码，从1开始")
    size: int = Field(10, ge=1, le=100, description="每页数量，最大100")

    @property
    def offset(self) -> int:
        """计算数据库查询的偏移量，增加上限保护"""
        offset = (self.page - 1) * self.size
        return min(offset, 100000)  # 限制最大偏移量为100000，避免过大偏移


class PageResponse(BaseResponseModel, Generic[T]):
    """分页数据模型，不包含外层的 success/message"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
    items: List[T] = Field(..., description="当前页的数据列表")

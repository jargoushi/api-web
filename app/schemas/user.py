from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.schemas.pagination import PageRequest
from app.schemas.response import BaseResponseModel


class UserCreateRequest(BaseModel):
    """创建用户的请求模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserUpdateRequest(BaseModel):
    """更新用户的请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    is_active: Optional[bool] = Field(None, description="是否激活")


# 新增查询参数模型
class UserQueryRequest(PageRequest):
    """用户列表查询参数（继承分页参数）"""
    username: Optional[str] = Field(None, description="用户名模糊查询")
    email: Optional[EmailStr] = Field(None, description="邮箱模糊查询")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserResponse(BaseResponseModel):
    """用户信息响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)

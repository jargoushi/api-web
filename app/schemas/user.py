import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

from app.schemas.pagination import PageRequest
from app.schemas.response import BaseResponseModel


class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, max_length=20, description="密码")
    activation_code: str = Field(..., min_length=1, max_length=50, description="激活码")

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """密码复杂度校验"""
        if len(v) < 8:
            raise ValueError("密码长度不能少于8位")
        if len(v) > 20:
            raise ValueError("密码长度不能超过20位")

        # 检查是否包含大小写字母和数字
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError("密码必须包含大小写字母和数字")

        return v


class UserUpdateRequest(BaseModel):
    """更新用户的请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """手机号格式校验"""
        if v is not None:
            # 简单的中国大陆手机号格式校验
            pattern = r'^1[3-9]\d{9}$'
            if not re.match(pattern, v):
                raise ValueError("手机号格式不正确")
        return v


class UserQueryRequest(PageRequest):
    """用户列表查询参数（继承分页参数）"""
    username: Optional[str] = Field(None, description="用户名模糊查询")
    phone: Optional[str] = Field(None, description="手机号模糊查询")
    email: Optional[EmailStr] = Field(None, description="邮箱模糊查询")
    activation_code: Optional[str] = Field(None, description="激活码模糊查询")


class UserResponse(BaseResponseModel):
    """用户信息响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    activation_code: str = Field(..., description="激活码")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

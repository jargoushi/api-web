"""用户相关 Schema"""

import re
from datetime import datetime
from typing import Optional

from pydantic import Field, EmailStr, field_validator, model_validator

from app.schemas.common.base import BaseRequestModel, BaseResponseModel
from app.schemas.common.pagination import PageRequest


class UserRegisterRequest(BaseRequestModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, max_length=20, description="密码")
    activation_code: str = Field(..., min_length=1, max_length=50, description="激活码")

    @classmethod
    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        """用户名校验"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @classmethod
    @field_validator('password')
    def validate_password_complexity(cls, v: str) -> str:
        """密码复杂度校验"""
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError("密码必须包含至少一个大写字母、一个小写字母和一个数字")

        weak_passwords = ['123456', 'password', 'admin123', 'qwerty', 'abc123']
        if v.lower() in weak_passwords:
            raise ValueError("密码过于简单，请使用更复杂的密码")

        return v


class UserUpdateRequest(BaseRequestModel):
    """更新用户的请求模型"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")

    @classmethod
    @field_validator('username')
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """用户名校验"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @classmethod
    @field_validator('phone')
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """手机号格式校验"""
        if v is not None:
            v = re.sub(r'[\s-()]', '', v)
            pattern = r'^1[3-9]\d{9}$'
            if not re.match(pattern, v):
                raise ValueError("手机号格式不正确")
        return v

    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        """确保至少更新一个字段"""
        if not any([self.username, self.phone, self.email]):
            raise ValueError("至少需要提供一个要更新的字段")
        return self


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

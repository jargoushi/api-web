"""账号相关 Schema"""

from datetime import datetime
from typing import Optional, List

from pydantic import Field

from app.schemas.common.base import BaseRequestModel, BaseResponseModel
from app.schemas.common.pagination import PageRequest


# ========== 账号 ==========

class AccountCreateRequest(BaseRequestModel):
    """创建账号请求"""
    name: str = Field(..., description="账号名称", max_length=100)
    platform_account: Optional[str] = Field(None, description="第三方平台账号", max_length=100)
    platform_password: Optional[str] = Field(None, description="第三方平台密码", max_length=100)
    description: Optional[str] = Field(None, description="账号描述", max_length=500)


class AccountUpdateRequest(BaseRequestModel):
    """更新账号请求"""
    id: int = Field(..., description="账号ID")
    name: Optional[str] = Field(None, description="账号名称", max_length=100)
    platform_account: Optional[str] = Field(None, description="第三方平台账号", max_length=100)
    platform_password: Optional[str] = Field(None, description="第三方平台密码", max_length=100)
    description: Optional[str] = Field(None, description="账号描述", max_length=500)


class AccountDeleteRequest(BaseRequestModel):
    """删除账号请求"""
    id: int = Field(..., description="账号ID")


class AccountResponse(BaseResponseModel):
    """账号响应"""
    id: int
    name: str
    platform_account: Optional[str] = None
    platform_password: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class AccountQueryRequest(PageRequest):
    """账号分页查询请求"""
    user_id: Optional[int] = Field(None, description="用户ID（不传则查询所有）")
    name: Optional[str] = Field(None, description="账号名称（模糊搜索）")


# ========== 项目渠道绑定 ==========

class BindingRequest(BaseRequestModel):
    """绑定请求"""
    project_code: int = Field(..., description="项目枚举code")
    channel_codes: List[int] = Field(..., description="渠道枚举code列表")
    browser_id: Optional[str] = Field(None, description="浏览器ID", max_length=100)


class BindingUpdateRequest(BaseRequestModel):
    """更新绑定请求"""
    id: int = Field(..., description="绑定ID")
    channel_codes: Optional[List[int]] = Field(None, description="渠道枚举code列表")
    browser_id: Optional[str] = Field(None, description="浏览器ID", max_length=100)


class BindingDeleteRequest(BaseRequestModel):
    """解绑请求"""
    id: int = Field(..., description="绑定ID")


class BindingResponse(BaseResponseModel):
    """绑定响应"""
    id: int
    project_code: int
    project_name: str
    channel_codes: List[int]
    channel_names: List[str]
    browser_id: Optional[str] = None

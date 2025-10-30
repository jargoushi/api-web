# 认证相关数据验证模式
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=100, description="密码")


class LoginResponse(BaseModel):
    """用户登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    expire_time: str = Field(..., description="过期时间（ISO格式）")
    user: dict = Field(..., description="用户信息")
    device_info: dict = Field(..., description="设备信息")


class LogoutRequest(BaseModel):
    """用户注销请求"""
    # 注销通常只需要token，在中间件中获取
    pass


class RefreshTokenRequest(BaseModel):
    """刷新token请求"""
    # 通常从Authorization头获取token
    pass


class RefreshTokenResponse(BaseModel):
    """刷新token响应"""
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    expire_time: str = Field(..., description="过期时间（ISO格式）")
    device_info: dict = Field(..., description="设备信息")


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: int = Field(..., description="会话ID")
    device_info: dict = Field(..., description="设备信息")
    is_current: bool = Field(..., description="是否为当前会话")


class SessionsResponse(BaseModel):
    """会话列表响应"""
    sessions: list[SessionInfo] = Field(..., description="会话列表")
    total: int = Field(..., description="总会话数")


class UserProfileResponse(BaseModel):
    """用户档案响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    activation_code: str = Field(..., description="激活码")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1, max_length=100, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=50, description="新密码")


class AuthResponse(BaseModel):
    """通用认证响应"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")
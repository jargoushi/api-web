from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=100, description="密码")


class RefreshTokenResponse(BaseModel):
    """刷新token响应"""
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    expire_time: str = Field(..., description="过期时间（ISO格式）")
    device_info: dict = Field(..., description="设备信息")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1, max_length=100, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=50, description="新密码")
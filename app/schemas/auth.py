from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=100, description="密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    new_password: str = Field(..., min_length=8, max_length=20, description="新密码")

    @field_validator('new_password')
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        """新密码复杂度校验"""
        # 检查是否包含大小写字母和数字
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError("密码必须包含至少一个大写字母、一个小写字母和一个数字")

        # 检查是否包含常见的弱密码
        weak_passwords = ['123456', 'password', 'admin123', 'qwerty', 'abc123']
        if v.lower() in weak_passwords:
            raise ValueError("密码过于简单，请使用更复杂的密码")

        return v

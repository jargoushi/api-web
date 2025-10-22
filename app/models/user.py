from tortoise import fields
from tortoise.models import Model

from app.util.password import hash_password, verify_password


class User(Model):
    """
    用户模型
    """
    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password_hash = fields.CharField(max_length=255, description="密码哈希")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class PydanticMeta:
        # 默认排除密码哈希字段
        exclude = ["password_hash"]

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return verify_password(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """获取密码哈希"""
        return hash_password(password)

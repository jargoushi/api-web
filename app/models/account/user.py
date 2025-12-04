from tortoise import fields

from app.models.base import BaseModel


class User(BaseModel):
    """
    用户模型
    """
    # 基础字段 (id, created_at, updated_at) 继承自 BaseModel
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password = fields.CharField(max_length=128, description="密码")
    phone = fields.CharField(max_length=20, null=True, unique=True, description="手机号")
    email = fields.CharField(max_length=100, null=True, unique=True, description="邮箱")
    activation_code = fields.CharField(max_length=50, description="激活码")

    class PydanticMeta:
        # 默认排除密码字段
        exclude = ["password"]


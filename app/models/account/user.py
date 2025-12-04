from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    用户模型
    """
    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password = fields.CharField(max_length=128, description="密码")
    phone = fields.CharField(max_length=20, null=True, unique=True, description="手机号")
    email = fields.CharField(max_length=100, null=True, unique=True, description="邮箱")
    activation_code = fields.CharField(max_length=50, description="激活码")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class PydanticMeta:
        # 默认排除密码字段
        exclude = ["password"]

    
from tortoise.fields import IntField, CharField, DatetimeField, BooleanField
from tortoise.models import Model


class User(Model):
    """用户模型"""
    id = IntField(pk=True, description="用户ID")
    username = CharField(max_length=50, unique=True, description="用户名")
    email = CharField(max_length=100, unique=True, description="邮箱")
    hashed_password = CharField(max_length=255, description="密码哈希")
    is_active = BooleanField(default=True, description="是否激活")
    created_at = DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "users"
        table_description = "用户表"

"""
基础模型
所有业务模型的父类，统一管理公共字段
"""
from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    """
    基础模型类

    所有业务模型都应该继承此类，自动包含：
    - id: 主键ID
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    id = fields.BigIntField(pk=True, description="主键ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True  # 标记为抽象类，不会创建对应的数据库表

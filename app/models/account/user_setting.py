"""用户配置模型"""

from tortoise import fields

from app.models.base import BaseModel


class UserSetting(BaseModel):
    """
    用户配置表

    存储用户的个性化配置，每个用户每个配置项只有一条记录
    """

    user_id = fields.BigIntField(description="用户ID", index=True)
    setting_key = fields.IntField(description="配置项编码")
    setting_value = fields.JSONField(description="配置值")

    class Meta:
        table = "user_settings"
        unique_together = [("user_id", "setting_key")]
        description = "用户配置表"

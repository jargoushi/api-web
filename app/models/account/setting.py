"""统一配置模型

合并 UserSetting 和 AccountSetting，通过 owner_type 区分
"""

from tortoise import fields

from app.models.base import BaseModel


class Setting(BaseModel):
    """
    统一配置表

    通过 owner_type 区分用户配置(1)和账号配置(2)
    """

    owner_type = fields.SmallIntField(description="所属类型 1:用户 2:账号")
    owner_id = fields.BigIntField(description="所属ID（用户ID或账号ID）", index=True)
    setting_key = fields.IntField(description="配置项编码")
    setting_value = fields.JSONField(description="配置值")

    class Meta:
        table = "settings"
        unique_together = [("owner_type", "owner_id", "setting_key")]
        description = "配置表"

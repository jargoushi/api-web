"""账号相关模型

包含：
- Account: 账号
- AccountProjectChannel: 账号项目渠道绑定
"""

from tortoise import fields

from app.models.base import BaseModel


class Account(BaseModel):
    """账号模型"""

    user_id = fields.BigIntField(description="所属用户ID")
    name = fields.CharField(max_length=100, description="账号名称")
    platform_account = fields.CharField(max_length=100, null=True, description="第三方平台账号")
    platform_password = fields.CharField(max_length=100, null=True, description="第三方平台密码")
    description = fields.CharField(max_length=500, null=True, description="账号描述")
    deleted_at = fields.DatetimeField(null=True, description="软删除时间")

    class Meta:
        table = "accounts"


class AccountProjectChannel(BaseModel):
    """账号项目渠道绑定模型"""

    account_id = fields.BigIntField(description="账号ID")
    project_code = fields.IntField(description="项目枚举code")
    channel_code = fields.IntField(description="渠道枚举code")
    browser_id = fields.CharField(max_length=100, null=True, description="比特浏览器ID")

    class Meta:
        table = "account_project_channels"
        unique_together = [("account_id", "project_code", "channel_code")]


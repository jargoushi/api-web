from tortoise import fields

from app.models.base import BaseModel
from app.enums.common.channel import ChannelEnum


class MonitorConfig(BaseModel):
    """监控配置模型"""
    user_id = fields.IntField(description="所属用户ID")
    channel_code = fields.IntField(description="渠道编码")
    target_url = fields.CharField(max_length=512, description="监控目标链接")
    target_external_id = fields.CharField(max_length=128, null=True, description="平台唯一ID")
    account_name = fields.CharField(max_length=128, null=True, description="账号名称快照")
    account_avatar = fields.CharField(max_length=512, null=True, description="账号头像URL")
    is_active = fields.IntField(default=1, description="是否启用监控")
    last_run_at = fields.DatetimeField(null=True, description="上次任务执行时间")
    last_run_status = fields.IntField(null=True, description="上次执行结果")
    deleted_at = fields.DatetimeField(null=True, description="删除时间")

    class Meta:
        table = "monitor_configs"
        ordering = ["-created_at"]

    @property
    def channel_enum(self) -> ChannelEnum:
        """获取渠道枚举"""
        return ChannelEnum.from_code(self.channel_code)

    @property
    def channel_name(self) -> str:
        """获取渠道名称"""
        return self.channel_enum.desc

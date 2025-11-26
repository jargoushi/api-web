from tortoise import fields
from tortoise.models import Model

from app.enums.channel_enum import ChannelEnum
from app.util.time_util import get_utc_now


class MonitorConfig(Model):
    """监控配置模型"""
    id = fields.IntField(pk=True, description="主键ID")
    user_id = fields.IntField(description="所属用户ID")
    channel_code = fields.IntField(description="渠道编码")
    target_url = fields.CharField(max_length=512, description="监控目标链接")
    target_external_id = fields.CharField(max_length=128, null=True, description="平台唯一ID")
    account_name = fields.CharField(max_length=128, null=True, description="账号名称快照")
    account_avatar = fields.CharField(max_length=512, null=True, description="账号头像URL")
    is_active = fields.IntField(default=1, description="是否启用监控")
    last_run_at = fields.DatetimeField(null=True, description="上次任务执行时间")
    last_run_status = fields.IntField(null=True, description="上次执行结果")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
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

    def soft_delete(self):
        """软删除"""
        self.deleted_at = get_utc_now()

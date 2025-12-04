import datetime

from tortoise import fields
from tortoise.models import Model

from app.core.config import settings
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum
from app.util.time_util import get_utc_now, normalize_datetime, is_expired


class ActivationCode(Model):
    """
    激活码模型
    """
    id = fields.IntField(pk=True, description="激活码ID")
    activation_code = fields.CharField(max_length=50, unique=True, description="激活码")
    distributed_at = fields.DatetimeField(null=True, description="分发时间")
    activated_at = fields.DatetimeField(null=True, description="激活时间")
    expire_time = fields.DatetimeField(null=True, description="过期时间")
    type = fields.IntField(description="激活码类型")
    status = fields.IntField(default=ActivationCodeStatusEnum.UNUSED.code, description="是否已使用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "activation_codes"
        ordering = ["-created_at"]

    @property
    def type_enum(self) -> ActivationTypeEnum:
        """获取类型枚举"""
        return ActivationTypeEnum.from_code(self.type)

    @property
    def type_name(self) -> str:
        """获取类型名称"""
        return self.type_enum.desc

    @property
    def status_enum(self) -> ActivationCodeStatusEnum:
        """获取状态枚举"""
        return ActivationCodeStatusEnum.from_code(self.status)

    @property
    def status_name(self) -> str:
        """获取状态名称"""
        return self.status_enum.desc

    def calculate_expire_time(self, activated_time: datetime = None) -> datetime:
        """
        计算过期时间

        Args:
            activated_time: 激活时间，如果为None则使用当前实例的activated_at

        Returns:
            计算后的过期时间
        """
        if activated_time is None:
            activated_time = self.activated_at

        if not activated_time:
            raise ValueError("激活时间不能为空")

        return self.type_enum.get_expire_time_from(
            activated_time,
            settings.ACTIVATION_GRACE_HOURS
        )

    def distribute(self):
        """分发激活码，设置分发时间和状态"""
        self.distributed_at = get_utc_now()
        self.status = ActivationCodeStatusEnum.DISTRIBUTED.code

    def activate(self):
        """激活激活码，设置激活时间和过期时间"""
        self.activated_at = get_utc_now()
        self.expire_time = self.calculate_expire_time(self.activated_at)
        self.status = ActivationCodeStatusEnum.ACTIVATED.code

    def invalidate(self):
        """作废激活码，设置状态为已作废"""
        self.status = ActivationCodeStatusEnum.INVALID.code

    @property
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if not self.expire_time:  # 未激活的没有过期时间
            return False

        # 使用统一的时间工具函数
        expire_time = normalize_datetime(self.expire_time)
        return is_expired(expire_time)

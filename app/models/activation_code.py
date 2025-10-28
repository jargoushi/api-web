from datetime import datetime, timedelta

from tortoise import fields
from tortoise.models import Model

from app.enums.activation_code_enum import ActivationTypeEnum
from app.enums.activation_code_status_enum import ActivationCodeStatusEnum


class ActivationCode(Model):
    """
    激活码模型
    """
    id = fields.IntField(pk=True, description="激活码ID")
    activation_code = fields.CharField(max_length=50, unique=True, description="激活码")
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

    @classmethod
    def get_expire_time_by_type(cls, code_type: int) -> datetime:
        """根据类型获取过期时间"""
        type_enum = ActivationTypeEnum.from_code(code_type)
        return type_enum.get_expire_time()

    @classmethod
    def get_type_name(cls, code_type: int) -> str:
        """获取类型名称"""
        type_enum = ActivationTypeEnum.from_code(code_type)
        return type_enum.desc

    @classmethod
    def get_status_name(cls, status: int) -> str:
        """获取状态名称"""
        status_enum = ActivationCodeStatusEnum.from_code(status)
        return status_enum.desc

    # 添加属性方法
    @property
    def actual_expire_time(self) -> datetime:
        """获取实际过期时间（激活时间 + 有效天数 + 1小时宽裕）"""
        if self.activated_at:
            type_enum = self.type_enum
            return self.activated_at + timedelta(days=type_enum.valid_days, hours=1)
        return None

    @property
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if not self.activated_at:
            return False
        return datetime.now() > self.actual_expire_time

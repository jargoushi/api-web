from tortoise import fields

from app.models.base import BaseModel
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum
from app.util.time_util import normalize_datetime, is_expired


class ActivationCode(BaseModel):
    """
    激活码模型

    纯数据模型，只包含字段定义和简单的属性访问器
    业务逻辑由 Service 层处理
    """
    activation_code = fields.CharField(max_length=50, unique=True, description="激活码")
    distributed_at = fields.DatetimeField(null=True, description="分发时间")
    activated_at = fields.DatetimeField(null=True, description="激活时间")
    expire_time = fields.DatetimeField(null=True, description="过期时间")
    type = fields.IntField(description="激活码类型")
    status = fields.IntField(default=ActivationCodeStatusEnum.UNUSED.code, description="激活码状态")

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

    @property
    def is_expired(self) -> bool:
        """
        检查是否已过期

        Returns:
            bool: True 表示已过期，False 表示未过期或未激活
        """
        if not self.expire_time:  # 未激活的没有过期时间
            return False

        # 使用统一的时间工具函数
        expire_time = normalize_datetime(self.expire_time)
        return is_expired(expire_time)

# 用户会话模型
from tortoise.fields import IntField, CharField, DatetimeField, TextField, BooleanField

from app.models.base import BaseModel
from app.util.time_util import normalize_datetime, is_expired


class UserSession(BaseModel):
    """
    用户会话模型

    纯数据模型，只包含字段定义和简单的属性访问器
    业务逻辑由 Service 层处理
    """
    user_id = IntField(description="用户ID，关联用户表")
    token = CharField(max_length=512, unique=True, description="JWT Token")
    device_id = CharField(max_length=64, description="设备指纹")
    device_name = CharField(max_length=255, null=True, description="设备名称（可选）")
    user_agent = TextField(null=True, description="用户代理字符串")
    ip_address = CharField(max_length=45, description="IP地址（支持IPv6）")
    is_active = BooleanField(default=True, description="会话是否活跃")
    last_accessed_at = DatetimeField(auto_now=True, description="最后访问时间")
    expires_at = DatetimeField(description="过期时间")

    class Meta:
        table = "user_sessions"
        table_description = "用户会话表"
        # 确保每个用户只能有一个活跃会话（单设备登录）
        unique_together = [("user_id", "is_active")]

    def __str__(self) -> str:
        return f"UserSession(user_id={self.user_id}, device_id={self.device_id[:8]}...)"

    @property
    def is_expired(self) -> bool:
        """
        检查会话是否已过期

        Returns:
            bool: True 表示已过期，False 表示未过期
        """
        expires_at = normalize_datetime(self.expires_at)
        return is_expired(expires_at)

    @property
    def should_cleanup(self) -> bool:
        """
        检查是否应该清理此会话

        Returns:
            bool: True 表示应该清理，False 表示不需要清理
        """
        return not self.is_active or self.is_expired

    def get_device_info(self) -> dict:
        """
        获取设备信息摘要

        Returns:
            dict: 设备信息字典
        """
        return {
            "device_id": self.device_id,
            "device_name": self.device_name or "未知设备",
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active and not self.is_expired
        }

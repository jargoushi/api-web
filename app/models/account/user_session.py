# 用户会话模型
from datetime import timedelta, datetime
from typing import Optional
from tortoise.models import Model
from tortoise.fields import IntField, CharField, DatetimeField, TextField, BooleanField

from app.util.time_util import get_utc_now, normalize_datetime, is_expired


class UserSession(Model):
    """用户会话模型 - 管理用户登录设备和token"""

    id = IntField(pk=True, description="会话ID")
    user_id = IntField(description="用户ID，关联用户表")
    token = CharField(max_length=512, unique=True, description="JWT Token")
    device_id = CharField(max_length=64, description="设备指纹")
    device_name = CharField(max_length=255, null=True, description="设备名称（可选）")
    user_agent = TextField(null=True, description="用户代理字符串")
    ip_address = CharField(max_length=45, description="IP地址（支持IPv6）")
    is_active = BooleanField(default=True, description="会话是否活跃")
    created_at = DatetimeField(auto_now_add=True, description="创建时间")
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
        """检查会话是否已过期"""
        # 使用统一的时间工具函数
        expires_at = normalize_datetime(self.expires_at)
        return is_expired(expires_at)

    @property
    def should_cleanup(self) -> bool:
        """检查是否应该清理此会话"""
        return not self.is_active or self.is_expired

    @classmethod
    async def create_session(cls, user_id: int, token: str, device_id: str,
                           device_name: Optional[str] = None,
                           user_agent: Optional[str] = None,
                           ip_address: Optional[str] = None,
                           expires_at: Optional[datetime] = None) -> "UserSession":
        """
        创建用户会话，并确保单设备登录

        Args:
            user_id (int): 用户ID
            token (str): JWT Token
            device_id (str): 设备指纹
            device_name (str, optional): 设备名称
            user_agent (str, optional): 用户代理
            ip_address (str, optional): IP地址
            expires_at (datetime, optional): 过期时间，默认为当前时间+24小时

        Returns:
            UserSession: 创建的会话对象

        Raises:
            Exception: 数据库操作异常
        """
        # 确保有过期时间
        if not expires_at:
            expires_at = get_utc_now() + timedelta(days=1)

        # 标准化过期时间（确保是naive UTC时间）
        expires_at = normalize_datetime(expires_at)

        # 使用事务确保原子性操作
        from tortoise import transactions
        async with transactions.in_transaction():
            # 1. 先删除该用户的所有会话（避免唯一约束冲突）
            await cls.filter(user_id=user_id).delete()

            # 2. 创建新会话
            session = await cls.create(
                user_id=user_id,
                token=token,
                device_id=device_id,
                device_name=device_name,
                user_agent=user_agent,
                ip_address=ip_address or "unknown",
                expires_at=expires_at,
                is_active=True
            )

        return session

    @classmethod
    async def get_active_session(cls, user_id: int) -> Optional["UserSession"]:
        """获取用户的活跃会话"""
        session = await cls.get_or_none(
            user_id=user_id,
            is_active=True
        ).prefetch_related()

        # 检查会话是否过期
        if session and session.is_expired:
            session.is_active = False
            await session.save()
            return None

        return session

    @classmethod
    async def get_session_by_token(cls, token: str) -> Optional["UserSession"]:
        """根据token获取会话"""
        session = await cls.get_or_none(token=token)

        # 检查会话状态和过期时间
        if session:
            if not session.is_active or session.is_expired:
                # 自动清理无效会话
                await session.delete()
                return None

            # 更新最后访问时间
            session.last_accessed_at = get_utc_now()
            await session.save()

        return session

    @classmethod
    async def revoke_session(cls, token: str) -> bool:
        """撤销指定会话"""
        session = await cls.get_or_none(token=token)
        if session:
            session.is_active = False
            await session.save()
            return True
        return False

    @classmethod
    async def revoke_user_sessions(cls, user_id: int, exclude_token: Optional[str] = None) -> int:
        """撤销用户的所有会话（可选排除指定token）"""
        query = cls.filter(user_id=user_id, is_active=True)
        if exclude_token:
            query = query.exclude(token=exclude_token)

        # 批量更新为非活跃状态
        count = await query.count()
        await query.update(is_active=False)
        return count

    @classmethod
    async def cleanup_expired_sessions(cls) -> int:
        """清理所有过期的会话"""
        # 使用统一的时间工具函数
        expired_time = get_utc_now()
        count = await cls.filter(
            expires_at__lt=expired_time
        ).delete()

        # 同时清理非活跃的会话（保留7天）
        cleanup_threshold = expired_time - timedelta(days=7)
        inactive_count = await cls.filter(
            is_active=False,
            created_at__lt=cleanup_threshold
        ).delete()

        return count + inactive_count

    async def extend_session(self, minutes: int = 30) -> bool:
        """延长会话时间"""
        self.expires_at = get_utc_now() + timedelta(minutes=minutes)
        await self.save()
        return True

    async def get_device_info(self) -> dict:
        """获取设备信息摘要"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name or "未知设备",
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active and not self.is_expired
        }
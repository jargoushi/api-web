"""
用户会话仓储类
封装用户会话相关的所有数据访问操作
"""
from typing import Optional, List
from datetime import datetime, timedelta

from app.repositories.base import BaseRepository
from app.models.account.user_session import UserSession
from app.util.time_util import get_utc_now, normalize_datetime


class UserSessionRepository(BaseRepository[UserSession]):
    """
    用户会话仓储类

    提供用户会话相关的数据访问方法
    """

    def __init__(self):
        """初始化用户会话仓储"""
        super().__init__(UserSession)

    async def find_by_token(self, token: str) -> Optional[UserSession]:
        """
        根据 token 查询会话

        Args:
            token: JWT Token

        Returns:
            会话实例，如果不存在则返回 None
        """
        return await self.get_or_none(token=token)

    async def find_active_session(self, user_id: int) -> Optional[UserSession]:
        """
        查询用户的活跃会话

        Args:
            user_id: 用户 ID

        Returns:
            会话实例，如果不存在则返回 None
        """
        return await self.get_or_none(user_id=user_id, is_active=True)

    async def find_user_sessions(
        self,
        user_id: int,
        is_active: Optional[bool] = None
    ) -> List[UserSession]:
        """
        查询用户的所有会话

        Args:
            user_id: 用户 ID
            is_active: 是否活跃（可选）

        Returns:
            会话列表
        """
        filters = {"user_id": user_id}
        if is_active is not None:
            filters["is_active"] = is_active

        return await self.find_all(**filters)

    async def delete_user_sessions(self, user_id: int, exclude_token: Optional[str] = None) -> int:
        """
        删除用户的所有会话

        Args:
            user_id: 用户 ID
            exclude_token: 要排除的 token（可选）

        Returns:
            删除的数量
        """
        query = self.model.filter(user_id=user_id)
        if exclude_token:
            query = query.exclude(token=exclude_token)

        count = await query.count()
        await query.delete()
        return count

    async def deactivate_user_sessions(
        self,
        user_id: int,
        exclude_token: Optional[str] = None
    ) -> int:
        """
        停用用户的所有活跃会话

        Args:
            user_id: 用户 ID
            exclude_token: 要排除的 token（可选）

        Returns:
            更新的数量
        """
        query = self.model.filter(user_id=user_id, is_active=True)
        if exclude_token:
            query = query.exclude(token=exclude_token)

        count = await query.count()
        await query.update(is_active=False)
        return count

    async def find_expired_sessions(self, before_time: datetime) -> List[UserSession]:
        """
        查询过期的会话

        Args:
            before_time: 过期时间点

        Returns:
            过期会话列表
        """
        return await self.model.filter(expires_at__lt=before_time).all()

    async def delete_expired_sessions(self, before_time: datetime) -> int:
        """
        删除过期的会话

        Args:
            before_time: 过期时间点

        Returns:
            删除的数量
        """
        count = await self.model.filter(expires_at__lt=before_time).count()
        await self.model.filter(expires_at__lt=before_time).delete()
        return count

    async def delete_inactive_sessions(self, before_time: datetime) -> int:
        """
        删除非活跃的旧会话

        Args:
            before_time: 时间点

        Returns:
            删除的数量
        """
        count = await self.model.filter(
            is_active=False,
            created_at__lt=before_time
        ).count()
        await self.model.filter(
            is_active=False,
            created_at__lt=before_time
        ).delete()
        return count

    async def create_session(
        self,
        user_id: int,
        token: str,
        device_id: str,
        device_name: Optional[str],
        user_agent: Optional[str],
        ip_address: str,
        expire_minutes: int,
        is_active: bool = True
    ) -> UserSession:
        """
        创建用户会话

        Args:
            user_id: 用户ID
            token: JWT Token
            device_id: 设备指纹
            device_name: 设备名称
            user_agent: 用户代理
            ip_address: IP地址
            expire_minutes: 过期分钟数
            is_active: 是否活跃

        Returns:
            创建的会话实例
        """
        expires_at = get_utc_now() + timedelta(minutes=expire_minutes)
        expires_at = normalize_datetime(expires_at)

        return await self.create(
            user_id=user_id,
            token=token,
            device_id=device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            is_active=is_active
        )

    async def deactivate_session(self, session: UserSession) -> UserSession:
        """
        停用会话

        Args:
            session: 会话实例

        Returns:
            更新后的会话实例
        """
        session.is_active = False
        await session.save()
        return session

    async def update_last_accessed_time(self, session: UserSession) -> UserSession:
        """
        更新会话最后访问时间

        Args:
            session: 会话实例

        Returns:
            更新后的会话实例
        """
        session.last_accessed_at = get_utc_now()
        await session.save()
        return session

    async def extend_session_time(self, session: UserSession, minutes: int) -> UserSession:
        """
        延长会话过期时间

        Args:
            session: 会话实例
            minutes: 延长的分钟数

        Returns:
            更新后的会话实例
        """
        session.expires_at = get_utc_now() + timedelta(minutes=minutes)
        await session.save()
        return session

    async def delete_session(self, session: UserSession) -> bool:
        """
        删除用户会话

        Args:
            session: 会话实例

        Returns:
            是否删除成功
        """
        return await self.delete(session)


# 创建单例实例
user_session_repository = UserSessionRepository()

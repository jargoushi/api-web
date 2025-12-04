"""
用户会话服务类
"""
from typing import Optional

from app.core.logging import log
from app.repositories.account import UserSessionRepository
from app.models.account.user_session import UserSession


class UserSessionService:
    """用户会话服务类"""

    def __init__(self, repository: UserSessionRepository = None):
        """
        初始化服务

        Args:
            repository: 用户会话仓储实例
        """
        self.repository = repository or UserSessionRepository()

    async def create_session(
        self,
        user_id: int,
        token: str,
        device_id: str,
        expire_minutes: int,
        device_name: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """
        创建用户会话，并确保单设备登录

        Args:
            user_id: 用户ID
            token: JWT Token
            device_id: 设备指纹
            expire_minutes: 过期分钟数
            device_name: 设备名称（可选）
            user_agent: 用户代理（可选）
            ip_address: IP地址（可选）

        Returns:
            创建的会话对象
        """
        await self.repository.delete_user_sessions(user_id)

        session = await self.repository.create_session(
            user_id=user_id,
            token=token,
            device_id=device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address or "unknown",
            expire_minutes=expire_minutes,
            is_active=True
        )

        return session

    async def get_active_session(self, user_id: int) -> Optional[UserSession]:
        """
        获取用户的活跃会话

        Args:
            user_id: 用户ID

        Returns:
            会话实例，如果不存在或已过期则返回 None
        """
        session = await self.repository.find_active_session(user_id)

        # 检查会话是否过期
        if session and session.is_expired:
            await self.repository.deactivate_session(session)
            return None

        return session

    async def get_session_by_token(self, token: str) -> Optional[UserSession]:
        """
        根据token获取会话

        Args:
            token: JWT Token

        Returns:
            会话实例，如果不存在或无效则返回 None
        """
        session = await self.repository.find_by_token(token)

        # 检查会话状态和过期时间
        if session:
            if not session.is_active or session.is_expired:
                await self.repository.delete_session(session)
                return None

            await self.repository.update_last_accessed_time(session)

        return session

    async def revoke_session(self, token: str) -> bool:
        """
        撤销指定会话

        Args:
            token: JWT Token

        Returns:
            是否成功撤销
        """
        session = await self.repository.find_by_token(token)
        if session:
            await self.repository.deactivate_session(session)
            return True
        return False

    async def revoke_user_sessions(
        self,
        user_id: int,
        exclude_token: Optional[str] = None
    ) -> int:
        """
        撤销用户的所有会话（可选排除指定token）

        Args:
            user_id: 用户ID
            exclude_token: 要排除的token（可选）

        Returns:
            撤销的会话数量
        """
        return await self.repository.deactivate_user_sessions(user_id, exclude_token)

    async def cleanup_expired_sessions(self) -> int:
        """
        清理所有过期的会话

        Returns:
            清理的会话数量
        """
        from app.util.time_util import get_utc_now
        from datetime import timedelta

        expired_time = get_utc_now()
        count = await self.repository.delete_expired_sessions(expired_time)

        cleanup_threshold = expired_time - timedelta(days=7)
        inactive_count = await self.repository.delete_inactive_sessions(cleanup_threshold)

        total = count + inactive_count
        if total > 0:
            log.info(f"清理了 {total} 个过期或非活跃会话")

        return total

    async def extend_session(self, session: UserSession, minutes: int = 30) -> bool:
        """
        延长会话时间

        Args:
            session: 会话实例
            minutes: 延长的分钟数

        Returns:
            是否成功延长
        """
        await self.repository.extend_session_time(session, minutes)
        return True

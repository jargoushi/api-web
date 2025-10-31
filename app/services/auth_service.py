from datetime import timedelta

from fastapi import Request

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.user import User
from app.models.user_session import UserSession
from app.util.device import get_client_ip, generate_device_name
from app.util.jwt import create_user_token, blacklist_user_token, get_jwt_manager
from app.util.password import verify_password, hash_password
# 密码复杂度验证已移至 pydantic schema 中进行
from app.util.time_util import get_utc_now


class AuthService:
    """认证相关服务类"""

    @staticmethod
    async def authenticate_user(username: str, password: str) -> User:
        """
        验证用户身份

        Args:
            username (str): 用户名
            password (str): 明文密码

        Returns:
            User: 验证成功返回用户对象

        Raises:
            BusinessException: 验证失败抛出异常
        """
        user = await User.get_or_none(username=username)
        if not user:
            raise BusinessException(message="用户名或密码错误", code=401)

        # 验证密码
        if not verify_password(password, user.password):
            raise BusinessException(message="用户名或密码错误", code=401)

        # 检查激活码是否过期
        from app.models.activation_code import ActivationCode
        if user.activation_code:
            activation_code_obj = await ActivationCode.get_or_none(activation_code=user.activation_code)
            if activation_code_obj and activation_code_obj.is_expired:
                raise BusinessException(message="激活码已过期，请重新激活", code=401)

        return user

    @staticmethod
    async def login_user(username: str, password: str, request: Request) -> str:
        """
        用户登录

        Args:
            username (str): 用户名
            password (str): 密码
            request (Request): FastAPI请求对象

        Returns:
            str: token

        Raises:
            BusinessException: 登录失败抛出异常
        """
        # 1. 验证用户身份
        user = await AuthService.authenticate_user(username, password)

        # 2. 生成token
        token_info = create_user_token(user.id, request)
        access_token = token_info["access_token"]
        device_id = token_info["device_id"]

        # 3. 获取设备信息（使用新的工具函数）
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = get_client_ip(request)
        device_name = generate_device_name(user_agent)

        # 4. 计算过期时间
        jwt_manager = get_jwt_manager()
        expires_at = get_utc_now() + timedelta(minutes=jwt_manager.expire_minutes)

        # 5. 创建用户会话（实现单设备登录）
        await UserSession.create_session(
            user_id=user.id,
            token=access_token,
            device_id=device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )

        log.info(f"用户 {username} 登录成功，设备: {device_name}")
        return access_token

    @staticmethod
    async def logout_user(token: str) -> None:
        """
        用户注销

        Args:
            token (str): JWT Token

        Raises:
            BusinessException: 注销失败抛出异常
        """
        # 1. 撤销用户会话
        session = await UserSession.get_session_by_token(token)
        if session:
            await session.delete()

        # 2. 将token加入黑名单
        blacklist_user_token(token)

    @staticmethod
    async def logout_all_devices(user_id: int) -> None:
        """
        注销用户的所有设备

        Args:
            user_id (int): 用户ID

        Returns:
            int: 被注销的设备数量
        """
        # 1. 撤销用户所有会话
        await UserSession.revoke_user_sessions(user_id)

    @staticmethod
    async def change_password(user: User, new_password: str) -> bool:
        """
        修改用户密码
        密码复杂度验证已在schema中完成
        """
        # 1. 更新密码（schema已验证复杂度）
        user.password = hash_password(new_password)
        await user.save()

        # 2. 注销所有其他设备（强制重新登录）
        await AuthService.logout_all_devices(user.id)

        log.info(f"用户 {user.username} 修改密码成功")
        return True

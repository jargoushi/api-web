from datetime import timedelta
from typing import Dict, Any

from fastapi import Request

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.auth import RefreshTokenResponse
from app.util.jwt import create_user_token, blacklist_user_token, get_jwt_manager
from app.util.password import verify_password
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

        # 3. 获取设备信息
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = AuthService._get_client_ip(request)
        device_name = AuthService._generate_device_name(user_agent)

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
    async def logout_all_devices(user_id: int) -> int:
        """
        注销用户的所有设备

        Args:
            user_id (int): 用户ID

        Returns:
            int: 被注销的设备数量
        """
        # 1. 撤销用户所有会话
        count = await UserSession.revoke_user_sessions(user_id)

        log.info(f"用户ID {user_id} 注销了所有设备，共 {count} 个设备")
        return count


    @staticmethod
    async def get_user_sessions(user_id: int) -> list:
        """
        获取用户的活跃会话列表

        Args:
            user_id (int): 用户ID

        Returns:
            list: 会话信息列表
        """
        # 获取用户的所有活跃会话
        sessions = await UserSession.filter(
            user_id=user_id,
            is_active=True
        ).order_by("-last_accessed_at")

        session_list = []
        for session in sessions:
            device_info = await session.get_device_info()
            session_list.append({
                "session_id": session.id,
                "device_info": device_info,
                "is_current": False
            })

        return session_list

    @staticmethod
    async def refresh_token(token: str, request: Request, user_id: int) -> Dict[str, Any]:
        """
        刷新token（依赖中间件验证用户身份）

        Args:
            token (str): 原token
            request (Request): 请求对象
            user_id (int): 从中间件获取的用户ID

        Returns:
            Dict[str, Any]: 新的token信息
        """
        # 1. 生成新token
        new_token_info = create_user_token(user_id, request)
        new_access_token = new_token_info["access_token"]
        new_device_id = new_token_info["device_id"]

        # 2. 获取设备信息
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = AuthService._get_client_ip(request)
        device_name = AuthService._generate_device_name(user_agent)

        # 3. 计算过期时间
        jwt_manager = get_jwt_manager()
        expires_at = get_utc_now() + timedelta(minutes=jwt_manager.expire_minutes)

        # 4. 创建新会话
        new_session = await UserSession.create_session(
            user_id=user_id,
            token=new_access_token,
            device_id=new_device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )

        # 5. 将旧token加入黑名单
        blacklist_user_token(token)

        # 6. 返回新token信息
        refresh_info = RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=new_token_info["expires_in"],
            expire_time=new_token_info["expire_time"],
            device_info=await new_session.get_device_info()
        )

        log.info(f"用户ID {user_id} 刷新token成功")
        return refresh_info

    @staticmethod
    async def change_password(user: User, old_password: str, new_password: str) -> bool:
        """
        修改用户密码

        Args:
            user (User): 用户对象
            old_password (str): 旧密码
            new_password (str): 新密码

        Returns:
            bool: 修改成功返回True

        Raises:
            BusinessException: 修改失败抛出异常
        """
        # 1. 验证旧密码
        if not verify_password(old_password, user.password):
            raise BusinessException(message="旧密码错误", code=400)

        # 2. 验证新密码复杂度
        if len(new_password) < 8 or len(new_password) > 20:
            raise BusinessException(message="密码长度必须在8-20位之间", code=400)

        has_upper = any(c.isupper() for c in new_password)
        has_lower = any(c.islower() for c in new_password)
        has_digit = any(c.isdigit() for c in new_password)

        if not (has_upper and has_lower and has_digit):
            raise BusinessException(
                message="密码必须包含至少一个大写字母、一个小写字母和一个数字",
                code=400
            )

        # 3. 更新密码
        from app.util.password import hash_password
        hashed_password = hash_password(new_password)
        user.password = hashed_password
        await user.save()

        # 4. 注销所有其他设备（强制重新登录）
        await AuthService.logout_all_devices(user.id)

        log.info(f"用户 {user.username} 修改密码成功")
        return True

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """获取客户端IP地址"""
        # 考虑代理情况
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        client_ip = forwarded_for.split(',')[0].strip() if forwarded_for else real_ip or request.client.host
        return client_ip or "unknown"

    @staticmethod
    def _generate_device_name(user_agent: str) -> str:
        """根据User-Agent生成设备名称"""
        user_agent_lower = user_agent.lower()

        if "mobile" in user_agent_lower or "android" in user_agent_lower:
            if "iphone" in user_agent_lower:
                return "iPhone"
            elif "ipad" in user_agent_lower:
                return "iPad"
            elif "android" in user_agent_lower:
                return "Android设备"
            else:
                return "移动设备"
        elif "windows" in user_agent_lower:
            return "Windows电脑"
        elif "mac" in user_agent_lower:
            return "Mac电脑"
        elif "linux" in user_agent_lower:
            return "Linux电脑"
        else:
            return "未知设备"

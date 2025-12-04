from fastapi import Request

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.account.user import User
from app.repositories.account import UserRepository, ActivationCodeRepository
from app.services.account.user_session_service import UserSessionService
from app.util.device import get_client_ip, generate_device_name
from app.util.jwt import create_user_token, blacklist_user_token, get_jwt_manager
from app.util.password import verify_password, hash_password


class AuthService:
    """认证相关服务类"""

    def __init__(
        self,
        user_repository: UserRepository = None,
        session_service: UserSessionService = None,
        activation_repository: ActivationCodeRepository = None
    ):
        """
        初始化服务

        Args:
            user_repository: 用户仓储实例
            session_service: 会话服务实例
            activation_repository: 激活码仓储实例
        """
        self.user_repository = user_repository or UserRepository()
        self.session_service = session_service or UserSessionService()
        self.activation_repository = activation_repository or ActivationCodeRepository()

    async def authenticate_user(self, username: str, password: str) -> User:
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
        user = await self.user_repository.find_by_username(username)
        if not user:
            raise BusinessException(message="用户名或密码错误", code=401)

        # 验证密码
        if not verify_password(password, user.password):
            raise BusinessException(message="用户名或密码错误", code=401)

        # 检查激活码是否过期
        if user.activation_code:
            activation_code_obj = await self.activation_repository.find_by_code(user.activation_code)
            if activation_code_obj and activation_code_obj.is_expired:
                raise BusinessException(message="激活码已过期，请重新激活", code=401)

        return user

    async def login_user(self, username: str, password: str, request: Request) -> str:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码
            request: FastAPI请求对象

        Returns:
            token字符串

        Raises:
            BusinessException: 登录失败抛出异常
        """
        # 1. 验证用户身份
        user = await self.authenticate_user(username, password)

        # 2. 生成token
        token_info = create_user_token(user.id, request)
        access_token = token_info["access_token"]
        device_id = token_info["device_id"]

        # 3. 获取设备信息
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = get_client_ip(request)
        device_name = generate_device_name(user_agent)

        # 4. 创建新会话（会自动删除旧会话）
        jwt_manager = get_jwt_manager()
        await self.session_service.create_session(
            user_id=user.id,
            token=access_token,
            device_id=device_id,
            expire_minutes=jwt_manager.expire_minutes,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address
        )

        log.info(f"用户 {username} 登录成功，设备: {device_name}")
        return access_token

    async def logout_user(self, token: str) -> None:
        """
        用户注销

        Args:
            token: JWT Token

        Raises:
            BusinessException: 注销失败抛出异常
        """
        # 1. 撤销用户会话
        await self.session_service.revoke_session(token)

        # 2. 将token加入黑名单
        blacklist_user_token(token)

    async def logout_all_devices(self, user_id: int) -> None:
        """
        注销用户的所有设备

        Args:
            user_id: 用户ID

        Returns:
            被注销的设备数量
        """
        # 撤销用户所有会话
        await self.session_service.revoke_user_sessions(user_id)

    async def change_password(self, user: User, new_password: str) -> bool:
        """
        修改用户密码
        密码复杂度验证已在schema中完成
        """
        # 1. 更新密码（schema已验证复杂度）
        user.password = hash_password(new_password)
        await self.user_repository.update(user)

        # 2. 注销所有其他设备（强制重新登录）
        await self.logout_all_devices(user.id)

        log.info(f"用户 {user.username} 修改密码成功")
        return True

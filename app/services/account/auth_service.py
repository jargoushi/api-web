from fastapi import Request

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.account.user import User
from app.repositories.account.user_repository import user_repository
from app.repositories.account.activation_repository import activation_repository
from app.util.jwt import jwt_manager
from app.util.password import verify_password, hash_password


class AuthService:
    """认证相关服务类"""

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
        user = await user_repository.find_by_username(username)
        if not user:
            raise BusinessException(message="用户名或密码错误", code=401)

        # 验证密码
        if not verify_password(password, user.password):
            raise BusinessException(message="用户名或密码错误", code=401)

        # 检查激活码是否过期
        if user.activation_code:
            activation_code_obj = await activation_repository.find_by_code(user.activation_code)
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
        token_info = jwt_manager.create_access_token(user.id)
        access_token = token_info["access_token"]

        log.info(f"用户 {username} 登录成功")
        return access_token

    async def logout_user(self, token: str) -> None:
        """
        用户注销（无状态JWT无需服务端处理，客户端丢弃token即可）

        Args:
            token: JWT Token
        """
        log.info("用户注销成功")

    async def change_password(self, user: User, new_password: str) -> bool:
        """
        修改用户密码

        Args:
            user: 用户实例
            new_password: 新密码（密码复杂度验证已在schema中完成）

        Returns:
            是否修改成功
        """
        # 更新密码（schema已验证复杂度）
        user.password = hash_password(new_password)
        await user_repository.update(user)

        log.info(f"用户 {user.username} 修改密码成功")
        return True


# 创建服务实例
auth_service = AuthService()

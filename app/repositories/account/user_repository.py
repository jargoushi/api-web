"""
用户仓储类
封装用户相关的所有数据访问操作
"""
from typing import Optional, List

from app.repositories.base import BaseRepository
from app.models.account.user import User


class UserRepository(BaseRepository[User]):
    """
    用户仓储类

    提供用户相关的数据访问方法
    """

    def __init__(self):
        """初始化用户仓储"""
        super().__init__(User)

    async def find_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名查询

        Args:
            username: 用户名

        Returns:
            用户实例，如果不存在则返回 None
        """
        return await self.get_or_none(username=username)

    async def find_by_phone(self, phone: str) -> Optional[User]:
        """
        根据手机号查询

        Args:
            phone: 手机号

        Returns:
            用户实例，如果不存在则返回 None
        """
        return await self.get_or_none(phone=phone)

    async def find_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱查询

        Args:
            email: 邮箱

        Returns:
            用户实例，如果不存在则返回 None
        """
        return await self.get_or_none(email=email)

    async def find_by_activation_code(self, activation_code: str) -> Optional[User]:
        """
        根据激活码查询用户

        Args:
            activation_code: 激活码

        Returns:
            用户实例，如果不存在则返回 None
        """
        return await self.get_or_none(activation_code=activation_code)

    async def username_exists(self, username: str) -> bool:
        """
        检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            是否存在
        """
        return await self.exists(username=username)

    async def phone_exists(self, phone: str) -> bool:
        """
        检查手机号是否存在

        Args:
            phone: 手机号

        Returns:
            是否存在
        """
        return await self.exists(phone=phone)

    async def email_exists(self, email: str) -> bool:
        """
        检查邮箱是否存在

        Args:
            email: 邮箱

        Returns:
            是否存在
        """
        return await self.exists(email=email)

    async def create_user(
        self,
        username: str,
        password: str,
        activation_code: str,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> User:
        """
        创建用户

        Args:
            username: 用户名
            password: 密码（已哈希）
            activation_code: 激活码
            phone: 手机号（可选）
            email: 邮箱（可选）

        Returns:
            创建的用户实例
        """
        return await self.create(
            username=username,
            password=password,
            activation_code=activation_code,
            phone=phone,
            email=email
        )

    def find_with_filters(
        self,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        activation_code: Optional[str] = None
    ):
        """
        根据条件查询用户列表（返回 QuerySet，用于分页）

        Args:
            username: 用户名（模糊查询）
            phone: 手机号（模糊查询）
            email: 邮箱（模糊查询）
            activation_code: 激活码（模糊查询）

        Returns:
            用户查询集（QuerySet）
        """
        query = self.model.all()

        if username:
            query = query.filter(username__icontains=username)

        if phone:
            query = query.filter(phone__icontains=phone)

        if email:
            query = query.filter(email__icontains=email)

        if activation_code:
            query = query.filter(activation_code__icontains=activation_code)

        return query.order_by("-created_at")

    async def update_user(self, user: User, **update_data) -> User:
        """
        更新用户信息

        Args:
            user: 用户实例
            **update_data: 要更新的字段

        Returns:
            更新后的用户实例
        """
        return await self.update(user, **update_data)


# 创建单例实例
user_repository = UserRepository()

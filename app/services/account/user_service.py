from typing import Optional, List

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.repositories.account.user_repository import user_repository
from app.schemas.account.user import UserRegisterRequest, UserUpdateRequest, UserResponse, UserQueryRequest
from app.services.account.activation_service import activation_service
from app.util.transaction import transactional
from app.util.password import hash_password


class UserService:
    """用户服务类"""

    @transactional
    async def register_user(self, user_data: UserRegisterRequest) -> UserResponse:
        """
        用户注册（使用事务装饰器）

        整个方法在事务中执行，确保用户创建和激活码激活的原子性
        """
        log.info(f"用户注册：{user_data.username}")

        # 1. 验证激活码是否为已分发状态
        await activation_service.get_distributed_activation_code(user_data.activation_code)

        # 2. 检查用户名唯一性
        is_conflict = await self.check_username_unique(user_data.username)
        if is_conflict:
            raise BusinessException(message="用户名已存在", code=400)

        # 3. 创建用户（事务内操作）
        hashed_password = hash_password(user_data.password)
        user_obj = await user_repository.create_user(
            username=user_data.username,
            password=hashed_password,
            activation_code=user_data.activation_code
        )

        # 4. 激活激活码（事务内操作）
        await activation_service.activate_activation_code(user_data.activation_code)
        log.info(f"用户 {user_data.username} 注册成功，激活码 {user_data.activation_code} 已激活")

        return UserResponse.model_validate(user_obj, from_attributes=True)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户响应

        Raises:
            BusinessException: 用户不存在
        """
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise BusinessException(message="用户不存在", code=404)

        return UserResponse.model_validate(user, from_attributes=True)

    async def update_user(self, user_id: int, user_data: UserUpdateRequest) -> UserResponse:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            user_data: 用户更新请求

        Returns:
            用户响应

        Raises:
            BusinessException: 用户不存在或字段冲突
        """
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise BusinessException(message="用户不存在", code=404)

        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return UserResponse.model_validate(user, from_attributes=True)

        # 检查唯一性约束（仅对非空字段）
        is_conflict = await self.check_user_fields_unique(
            user_id=user_id,
            username=update_data.get("username"),
            phone=update_data.get("phone"),
            email=update_data.get("email")
        )

        if is_conflict:
            raise BusinessException(message="用户名、手机号或邮箱已被使用", code=400)

        await user_repository.update_user(user, **update_data)

        return UserResponse.model_validate(user, from_attributes=True)

    def get_user_list(self, params: UserQueryRequest):
        """
        获取用户查询集（用于分页）

        Args:
            params: 用户查询请求

        Returns:
            用户查询集（QuerySet）
        """
        return user_repository.find_with_filters(
            username=params.username,
            phone=params.phone,
            email=params.email,
            activation_code=params.activation_code
        )

    async def check_username_unique(self, username: str) -> bool:
        """
        检查用户名是否已存在

        Args:
            username (str): 待检查的用户名

        Returns:
            bool: True 表示已存在（不唯一），False 表示可用（唯一）
        """
        return await user_repository.username_exists(username)

    async def check_user_fields_unique(
        self,
        user_id: int,
        username: str = None,
        phone: str = None,
        email: str = None
    ) -> bool:
        """
        检查用户名、手机号或邮箱是否被其他用户使用（仅检查非空字段）

        使用 OR 逻辑：只要任一字段被其他用户占用就返回 True

        Args:
            user_id (int): 当前用户的ID，用于排除自身
            username (str, optional): 待检查的用户名
            phone (str, optional): 待检查的手机号
            email (str, optional): 待检查的邮箱

        Returns:
            bool: True 表示已存在（不唯一），False 表示可用（唯一）
        """
        from tortoise.expressions import Q

        if not username and not phone and not email:
            return False

        # 构建 OR 条件
        conditions = Q()
        if username:
            conditions |= Q(username=username)
        if phone:
            conditions |= Q(phone=phone)
        if email:
            conditions |= Q(email=email)

        # 构建查询，排除当前用户
        query = user_repository.get_queryset()
        if user_id is not None:
            query = query.exclude(id=user_id)

        return await query.filter(conditions).exists()



# 创建服务实例
user_service = UserService()

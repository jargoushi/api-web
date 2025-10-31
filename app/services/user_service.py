from typing import Optional

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserUpdateRequest, UserResponse, UserQueryRequest
from app.services.activation_code_service import ActivationCodeService
from app.util.transaction import transactional
from app.util.password import hash_password


class UserService:
    @staticmethod
    @transactional
    async def register_user(user_data: UserRegisterRequest) -> UserResponse:
        """
        用户注册（使用事务装饰器）

        整个方法在事务中执行，确保用户创建和激活码激活的原子性
        """
        log.info(f"用户注册：{user_data.username}")

        # 1. 验证激活码是否为已分发状态
        await ActivationCodeService.get_distributed_activation_code(user_data.activation_code)

        # 2. 检查用户名唯一性
        is_conflict = await UserService.check_username_unique(user_data.username)
        if is_conflict:
            raise BusinessException(message="用户名已存在", code=400)

        # 3. 创建用户（事务内操作）
        # 对密码进行哈希处理
        hashed_password = hash_password(user_data.password)
        user_dict = user_data.model_dump(exclude={"password"})
        user_obj = await User.create(**user_dict, password=hashed_password)

        # 4. 激活激活码（事务内操作）
        await ActivationCodeService.activate_activation_code(user_data.activation_code)
        log.info(f"用户 {user_data.username} 注册成功，激活码 {user_data.activation_code} 已激活")

        return UserResponse.model_validate(user_obj, from_attributes=True)

    @staticmethod
    async def get_user_by_id(user_id: int) -> UserResponse:
        """根据ID获取用户"""
        user = await User.get_or_none(id=user_id)
        if not user:
            raise BusinessException(message="用户不存在", code=404)

        return UserResponse.model_validate(user, from_attributes=True)

    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdateRequest) -> UserResponse:
        """更新用户信息"""
        user = await User.get_or_none(id=user_id)
        if not user:
            raise BusinessException(message="用户不存在", code=404)

        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return UserResponse.model_validate(user, from_attributes=True)

        # 检查唯一性约束（仅对非空字段）
        is_conflict = await UserService.check_user_fields_unique(
            user_id=user_id,
            username=update_data.get("username"),
            phone=update_data.get("phone"),
            email=update_data.get("email")
        )

        if is_conflict:
            raise BusinessException(message="用户名、手机号或邮箱已被使用", code=400)

        # 如果没有冲突，执行更新
        await user.update_from_dict(update_data)
        await user.save()

        return UserResponse.model_validate(user, from_attributes=True)

    @staticmethod
    def get_user_queryset(params: UserQueryRequest):
        """获取用户查询集（支持条件过滤+分页）"""
        query = User.all()  # 基础查询

        # 动态添加过滤条件
        if params.username:
            query = query.filter(username__icontains=params.username)
        if params.phone:
            query = query.filter(phone__icontains=params.phone)
        if params.email:
            query = query.filter(email__icontains=params.email)
        if params.activation_code:
            query = query.filter(activation_code__icontains=params.activation_code)

        # 保持原排序：按创建时间倒序
        return query.order_by("-created_at")

    @staticmethod
    async def check_username_unique(username: str) -> bool:
        """
        检查用户名是否已存在

        Args:
            username (str): 待检查的用户名

        Returns:
            bool: True 表示已存在（不唯一），False 表示可用（唯一）
        """
        return await User.filter(username=username).exists()

    @staticmethod
    async def check_user_fields_unique(user_id: int, username: str = None, phone: str = None,
                                       email: str = None) -> bool:
        """
        检查用户名、手机号或邮箱是否被其他用户使用（仅检查非空字段）

        Args:
            user_id (int): 当前用户的ID，用于排除自身
            username (str, optional): 待检查的用户名
            phone (str, optional): 待检查的手机号
            email (str, optional): 待检查的邮箱

        Returns:
            bool: True 表示已存在（不唯一），False 表示可用（唯一）
        """
        if not username and not phone and not email:
            return False

        # 构建查询条件
        query = User.all()

        if user_id is not None:
            query = query.exclude(id=user_id)

        # 如果提供了用户名，则加入查询条件
        if username:
            query = query.filter(username=username)

        # 如果提供了手机号，则加入查询条件
        if phone:
            query = query.filter(phone=phone)

        # 如果提供了邮箱，则加入查询条件
        if email:
            query = query.filter(email=email)

        return await query.exists()

    
from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserUpdateRequest, UserResponse, UserQueryRequest


class UserService:
    @staticmethod
    async def create_user(user_data: UserCreateRequest) -> UserResponse:
        """创建用户"""
        log.info(f"创建用户：{user_data}")

        is_conflict = await UserService.check_username_or_email_unique(
            user_id=None,  # 表示这是一个新用户，需要和所有已存在用户比较
            username=user_data.username,
            email=user_data.email
        )

        if is_conflict:
            raise BusinessException(message="用户名或邮箱已存在", code=400)

        # 如果没有冲突，创建用户
        user_dict = user_data.model_dump(exclude={"password"})
        user_obj = await User.create(**user_dict, password_hash=User.get_password_hash(user_data.password))

        return UserResponse.model_validate(user_obj, from_attributes=True)

    @staticmethod
    async def get_user_by_id(user_id: int) -> UserResponse:
        """根据ID获取用户"""
        user = await User.get_or_none(id=user_id, is_active=True)
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

        is_conflict = await UserService.check_username_or_email_unique(
            user_id=user_id,  # 传入当前用户ID，用于排除自身
            username=update_data.get("username"),
            email=update_data.get("email")
        )

        if is_conflict:
            raise BusinessException(message="用户名或邮箱已被使用", code=400)

        # 如果没有冲突，执行更新
        await user.update_from_dict(update_data)
        await user.save()

        return UserResponse.model_validate(user, from_attributes=True)

    @staticmethod
    def get_user_queryset(params: UserQueryRequest):  # 新增 params 参数
        """获取用户查询集（支持条件过滤+分页）"""
        query = User.filter(is_active=True)  # 基础条件：只查询激活用户

        # 动态添加过滤条件
        if params.username:
            # 模糊查询（不区分大小写，根据数据库类型调整语法）
            query = query.filter(username__icontains=params.username)
        if params.email:
            query = query.filter(email__icontains=params.email)
        if params.is_active is not None:  # 注意：布尔值可能为False，不能用 if params.is_active
            query = query.filter(is_active=params.is_active)

        # 保持原排序：按创建时间倒序
        return query.order_by("-created_at")

    @staticmethod
    async def check_username_or_email_unique(user_id: int, username: str = None, email: str = None) -> bool:
        """
        检查用户名或邮箱是否被其他用户使用

        Args:
            user_id (int): 当前用户的ID，用于排除自身。创建用户时传入 None。
            username (str, optional): 待检查的用户名
            email (str, optional): 待检查的邮箱

        Returns:
            bool: True 表示已存在（不唯一），False 表示可用（唯一）
        """
        if not username and not email:
            return False

        # 构建查询条件
        query = User.filter(is_active=True)

        if user_id is not None:
            query = query.exclude(id=user_id)

        # 如果提供了用户名，则加入查询条件
        if username:
            query = query.filter(username=username)

        # 如果提供了邮箱，则加入查询条件
        if email:
            query = query.filter(email=email)

        return await query.exists()

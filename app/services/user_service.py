from datetime import timedelta
from typing import Optional, Dict, Any

from fastapi import Request
from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.user import UserRegisterRequest, UserUpdateRequest, UserResponse, UserQueryRequest
from app.services.activation_code_service import ActivationCodeService
from app.util.transaction import transactional
from app.util.password import hash_password, verify_password
from app.util.jwt import create_user_token, blacklist_user_token, get_jwt_manager
from app.util.time_util import get_utc_now


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
    async def login_user(username: str, password: str, request: Request) -> Dict[str, Any]:
        """
        用户登录

        Args:
            username (str): 用户名
            password (str): 密码
            request (Request): FastAPI请求对象

        Returns:
            Dict[str, Any]: 登录成功信息，包含token和用户信息

        Raises:
            BusinessException: 登录失败抛出异常
        """
        # 1. 验证用户身份
        user = await UserService.authenticate_user(username, password)

        # 2. 生成token
        token_info = create_user_token(user.id, request)
        access_token = token_info["access_token"]
        device_id = token_info["device_id"]

        # 3. 获取设备信息
        user_agent = request.headers.get("User-Agent", "Unknown")
        ip_address = UserService._get_client_ip(request)
        device_name = UserService._generate_device_name(user_agent)

        # 4. 计算过期时间
        jwt_manager = get_jwt_manager()
        expires_at = get_utc_now() + timedelta(minutes=jwt_manager.expire_minutes)

        # 5. 创建用户会话（实现单设备登录）
        session = await UserSession.create_session(
            user_id=user.id,
            token=access_token,
            device_id=device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )

        # 6. 返回登录信息
        login_info = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": token_info["expires_in"],
            "expire_time": token_info["expire_time"],
            "user": UserResponse.model_validate(user, from_attributes=True),
            "device_info": await session.get_device_info()
        }

        log.info(f"用户 {username} 登录成功，设备: {device_name}")
        return login_info

    @staticmethod
    async def logout_user(token: str, user_id: int) -> bool:
        """
        用户注销

        Args:
            token (str): JWT Token
            user_id (int): 用户ID

        Returns:
            bool: 注销成功返回True

        Raises:
            BusinessException: 注销失败抛出异常
        """
        try:
            # 1. 撤销用户会话
            session = await UserSession.get_session_by_token(token)
            if session:
                await session.delete()

            # 2. 将token加入黑名单
            blacklist_user_token(token)

            log.info(f"用户ID {user_id} 注销成功")
            return True

        except Exception as e:
            log.error(f"用户注销失败: {str(e)}")
            raise BusinessException(message="注销失败", code=500)

    @staticmethod
    async def logout_all_devices(user_id: int) -> int:
        """
        注销用户的所有设备

        Args:
            user_id (int): 用户ID

        Returns:
            int: 被注销的设备数量
        """
        try:
            # 1. 撤销用户所有会话
            count = await UserSession.revoke_user_sessions(user_id)

            log.info(f"用户ID {user_id} 注销了所有设备，共 {count} 个设备")
            return count

        except Exception as e:
            log.error(f"批量注销失败: {str(e)}")
            raise BusinessException(message="批量注销失败", code=500)

    @staticmethod
    async def get_user_sessions(user_id: int) -> list:
        """
        获取用户的活跃会话列表

        Args:
            user_id (int): 用户ID

        Returns:
            list: 会话信息列表
        """
        try:
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
                    "is_current": False  # 默认不是当前会话
                })

            return session_list

        except Exception as e:
            log.error(f"获取会话列表失败: {str(e)}")
            raise BusinessException(message="获取会话列表失败", code=500)

    @staticmethod
    async def refresh_token(token: str, request: Request) -> Dict[str, Any]:
        """
        刷新token

        Args:
            token (str): 原token
            request (Request): 请求对象

        Returns:
            Dict[str, Any]: 新的token信息

        Raises:
            BusinessException: 刷新失败抛出异常
        """
        try:
            # 1. 验证原token并获取用户信息
            jwt_manager = get_jwt_manager()
            payload = jwt_manager.verify_token(token)
            user_id = payload["user_id"]

            # 2. 获取用户信息
            user = await User.get_or_none(id=user_id)
            if not user:
                raise BusinessException(message="用户不存在", code=401)

            # 3. 检查激活码状态
            from app.models.activation_code import ActivationCode
            if user.activation_code:
                activation_code_obj = await ActivationCode.get_or_none(activation_code=user.activation_code)
                if activation_code_obj and activation_code_obj.is_expired:
                    raise BusinessException(message="激活码已过期，请重新激活", code=401)

            # 4. 生成新token
            new_token_info = create_user_token(user_id, request)
            new_access_token = new_token_info["access_token"]
            new_device_id = new_token_info["device_id"]

            # 5. 获取设备信息
            user_agent = request.headers.get("User-Agent", "Unknown")
            ip_address = UserService._get_client_ip(request)
            device_name = UserService._generate_device_name(user_agent)

            # 6. 计算过期时间
            expires_at = get_utc_now() + timedelta(minutes=jwt_manager.expire_minutes)

            # 7. 创建新会话
            new_session = await UserSession.create_session(
                user_id=user_id,
                token=new_access_token,
                device_id=new_device_id,
                device_name=device_name,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=expires_at
            )

            # 8. 将旧token加入黑名单
            blacklist_user_token(token)

            # 9. 返回新token信息
            refresh_info = {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": new_token_info["expires_in"],
                "expire_time": new_token_info["expire_time"],
                "device_info": await new_session.get_device_info()
            }

            log.info(f"用户 {user.username} 刷新token成功")
            return refresh_info

        except BusinessException:
            raise
        except Exception as e:
            log.error(f"刷新token失败: {str(e)}")
            raise BusinessException(message="刷新token失败", code=500)

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

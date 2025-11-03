"""
认证上下文工具
统一处理认证数据访问，简化路由代码
支持直接调用和FastAPI依赖注入两种使用方式
"""

from typing import Tuple

from fastapi import Request

from app.core.exceptions import BusinessException
from app.models.user import User
from app.models.user_session import UserSession


def get_current_user(request: Request) -> User:
    """
    获取当前登录用户（支持直接调用和依赖注入）

    Args:
        request: FastAPI请求对象

    Returns:
        User: 当前用户对象

    Raises:
        BusinessException: 用户未登录时抛出异常

    使用方式:
        # 直接调用
        user = get_current_user(request)

        # 依赖注入
        async def endpoint(user: User = Depends(get_current_user)):
            pass
    """
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)
    return user


def get_current_user_id(request: Request) -> int:
    """
    获取当前登录用户ID（支持直接调用和依赖注入）

    Args:
        request: FastAPI请求对象

    Returns:
        int: 当前用户ID

    Raises:
        BusinessException: 用户未登录时抛出异常

    使用方式:
        # 直接调用
        user_id = get_current_user_id(request)

        # 依赖注入
        async def endpoint(user_id: int = Depends(get_current_user_id)):
            pass
    """
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise BusinessException(message="用户未登录", code=401)
    return user_id


def get_current_session(request: Request) -> UserSession:
    """
    获取当前用户会话（支持直接调用和依赖注入）

    Args:
        request: FastAPI请求对象

    Returns:
        UserSession: 当前会话对象

    Raises:
        BusinessException: 会话无效时抛出异常

    使用方式:
        # 直接调用
        session = get_current_session(request)

        # 依赖注入
        async def endpoint(session: UserSession = Depends(get_current_session)):
            pass
    """
    session = getattr(request.state, 'session', None)
    if not session:
        raise BusinessException(message="会话无效", code=401)
    return session


def get_current_device_id(request: Request) -> str:
    """
    获取当前设备ID（支持直接调用和依赖注入）

    Args:
        request: FastAPI请求对象

    Returns:
        str: 设备ID

    Raises:
        BusinessException: 设备信息无效时抛出异常

    使用方式:
        # 直接调用
        device_id = get_current_device_id(request)

        # 依赖注入
        async def endpoint(device_id: str = Depends(get_current_device_id)):
            pass
    """
    device_id = getattr(request.state, 'device_id', None)
    if not device_id:
        raise BusinessException(message="设备信息无效", code=401)
    return device_id


def require_auth(request: Request) -> Tuple[User, UserSession]:
    """
    获取认证所需的用户和会话信息

    Args:
        request: FastAPI请求对象

    Returns:
        Tuple[User, UserSession]: (用户对象, 会话对象)

    Raises:
        BusinessException: 认证信息无效时抛出异常

    使用方式:
        # 直接调用
        user, session = require_auth(request)
    """
    user = get_current_user(request)
    session = get_current_session(request)
    return user, session


def get_auth_info(request: Request) -> dict:
    """
    获取完整的认证信息

    Args:
        request: FastAPI请求对象

    Returns:
        dict: 包含用户、会话、设备ID的认证信息

    Raises:
        BusinessException: 认证信息无效时抛出异常

    使用方式:
        # 直接调用
        auth_info = get_auth_info(request)
        user = auth_info["user"]
        session = auth_info["session"]
        device_id = auth_info["device_id"]
    """
    user = get_current_user(request)
    session = get_current_session(request)
    device_id = get_current_device_id(request)

    return {
        "user": user,
        "session": session,
        "device_id": device_id
    }
"""
认证上下文工具
统一处理认证数据访问，简化路由代码
"""

from typing import Tuple

from fastapi import Request

from app.core.exceptions import BusinessException
from app.models.user import User
from app.models.user_session import UserSession


def get_current_user(request: Request) -> User:
    """
    获取当前登录用户

    Args:
        request: FastAPI请求对象

    Returns:
        User: 当前用户对象

    Raises:
        BusinessException: 用户未登录时抛出异常
    """
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)
    return user


def get_current_user_id(request: Request) -> int:
    """
    获取当前登录用户的ID

    Args:
        request: FastAPI请求对象

    Returns:
        int: 当前用户ID

    Raises:
        BusinessException: 用户未登录时抛出异常
    """
    user = get_current_user(request)
    return user.id


def get_current_session(request: Request) -> UserSession:
    """
    获取当前用户会话

    Args:
        request: FastAPI请求对象

    Returns:
        UserSession: 当前会话对象

    Raises:
        BusinessException: 会话无效时抛出异常
    """
    session = getattr(request.state, 'session', None)
    if not session:
        raise BusinessException(message="会话无效", code=401)
    return session


def get_current_device_id(request: Request) -> str:
    """
    获取当前设备ID

    Args:
        request: FastAPI请求对象

    Returns:
        str: 设备ID

    Raises:
        BusinessException: 设备信息无效时抛出异常
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
    """
    user = get_current_user(request)
    session = get_current_session(request)
    device_id = get_current_device_id(request)

    return {
        "user": user,
        "session": session,
        "device_id": device_id
    }


# 依赖注入函数，用于FastAPI路由
def get_current_user_dep(request: Request) -> User:
    """
    依赖注入函数，获取当前用户
    使用方式: @router.post("/example", dependencies=[Depends(get_current_user_dep)])
    """
    return get_current_user(request)


def get_current_user_id_dep(request: Request) -> int:
    """
    依赖注入函数，获取当前用户ID
    使用方式:
    async def some_endpoint(user_id: int = Depends(get_current_user_id_dep)):
        ...
    """
    return get_current_user_id(request)


def get_current_session_dep(request: Request) -> UserSession:
    """
    依赖注入函数，获取当前会话
    """
    return get_current_session(request)
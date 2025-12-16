"""
认证上下文工具
统一处理认证数据访问，简化路由代码
支持直接调用和FastAPI依赖注入两种使用方式
"""

from fastapi import Request

from app.core.exceptions import BusinessException
from app.models.account.user import User


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


def get_current_token(request: Request) -> str:
    """
    获取当前token（支持直接调用和依赖注入）

    Args:
        request: FastAPI请求对象

    Returns:
        str: 当前token

    Raises:
        BusinessException: token无效时抛出异常

    使用方式:
        # 直接调用
        token = get_current_token(request)

        # 依赖注入
        async def endpoint(token: str = Depends(get_current_token)):
            pass
    """
    token = getattr(request.state, 'token', None)
    if not token:
        raise BusinessException(message="token无效", code=401)
    return token

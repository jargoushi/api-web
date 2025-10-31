from fastapi import APIRouter, Request

from app.core.exceptions import BusinessException
from app.schemas.auth import (
    LoginRequest, ChangePasswordRequest
)
from app.schemas.response import ApiResponse, success_response
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=ApiResponse[str], summary="用户登录")
async def login_user(login_data: LoginRequest, request: Request):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    登录成功后返回JWT token和用户信息
    """
    access_token = await AuthService.login_user(
        username=login_data.username,
        password=login_data.password,
        request=request
    )
    return success_response(data=access_token)


@router.post("/logout", response_model=ApiResponse[bool], summary="用户注销")
async def logout_user(request: Request):
    """
    用户注销
    """
    # 从中间件获取用户和token信息（已验证）
    current_user = getattr(request.state, 'user', None)
    current_session = getattr(request.state, 'session', None)

    if current_user and current_session:
        await AuthService.logout_user(current_session.token)

    return success_response(data=True)


@router.post("/logout-all", summary="注销所有设备")
async def logout_all_devices(request: Request):
    """
    注销用户的所有设备
    """
    # 从中间件获取用户信息（已验证）
    current_user = getattr(request.state, 'user', None)

    if current_user:
        await AuthService.logout_all_devices(current_user.id)

    return success_response(data=True)


@router.get("/profile", summary="获取用户档案")
async def get_user_profile(request: Request):
    """
    获取当前用户的详细信息
    """
    # 从中间件获取用户信息（已验证）
    current_user = getattr(request.state, 'user', None)

    if not current_user:
        raise BusinessException(message="用户未登录", code=401)

    # 直接返回用户数据字典
    profile = {
        "id": current_user.id,
        "username": current_user.username,
        "phone": current_user.phone,
        "email": current_user.email,
        "activation_code": current_user.activation_code,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat()
    }

    return success_response(data=profile)


@router.get("/sessions", summary="获取会话列表")
async def get_user_sessions(request: Request):
    """
    获取当前用户的所有活跃会话
    """
    # 从中间件获取用户信息（已验证）
    current_user = getattr(request.state, 'user', None)
    if not current_user:
        raise BusinessException(message="用户未登录", code=401)

    sessions = await AuthService.get_user_sessions(current_user.id)

    # 标记当前会话
    current_device_id = getattr(request.state, 'device_id', None)
    for session in sessions:
        if session["device_info"]["device_id"] == current_device_id:
            session["is_current"] = True
            break

    # 直接返回简化的数据结构
    return success_response(data={
        "sessions": sessions,
        "total": len(sessions)
    })


@router.post("/refresh-token", summary="刷新访问令牌")
async def refresh_access_token(request: Request):
    """
    刷新访问令牌
    """
    # 从中间件获取用户和会话信息（已验证）
    current_user = getattr(request.state, 'user', None)
    current_session = getattr(request.state, 'session', None)

    if not current_user or not current_session:
        raise BusinessException(message="用户未登录", code=401)

    # 调用刷新服务，传入用户ID
    refresh_info = await AuthService.refresh_token(current_session.token, request, current_user.id)
    return success_response(data=refresh_info)


@router.post("/change-password", response_model=ApiResponse[bool], summary="修改密码")
async def change_password(password_data: ChangePasswordRequest, request: Request):
    """
    修改用户密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（8-20位，必须包含大小写字母和数字）
    """
    # 从中间件获取用户信息（已验证）
    current_user = getattr(request.state, 'user', None)
    if not current_user:
        raise BusinessException(message="用户未登录", code=401)

    await AuthService.change_password(
        user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )

    return success_response(data=True)


@router.get("/check-auth", summary="检查认证状态")
async def check_authentication(request: Request):
    """
    检查当前token的认证状态
    """
    # 从中间件获取用户信息和会话信息（已验证）
    current_user = getattr(request.state, 'user', None)
    session = getattr(request.state, 'session', None)

    if not current_user:
        raise BusinessException(message="用户未登录", code=401)

    # 直接返回认证状态数据
    return success_response(data={
        "success": True,
        "message": "认证有效",
        "user_id": current_user.id,
        "username": current_user.username,
        "session_info": await session.get_device_info() if session else None
    })

from fastapi import APIRouter, Depends, Request
from typing import Optional

from app.core.exceptions import BusinessException
from app.schemas.pagination import PageResponse
from app.schemas.response import ApiResponse, success_response, paginated_response
from app.schemas.user import UserResponse, UserRegisterRequest, UserUpdateRequest, UserQueryRequest
from app.schemas.auth import (
    LoginRequest, LoginResponse, LogoutRequest, RefreshTokenRequest,
    RefreshTokenResponse, SessionsResponse, UserProfileResponse,
    ChangePasswordRequest, AuthResponse
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=ApiResponse[UserResponse], summary="用户注册")
async def register_user(user_data: UserRegisterRequest):
    """
    用户注册（需要用户名、密码和激活码）

    - **username**: 用户名（必填，2-50位）
    - **password**: 密码（必填，8-20位，必须包含大小写字母和数字）
    - **activation_code**: 激活码（必填）
    """
    user = await UserService.register_user(user_data)
    return success_response(data=user)


@router.get("/{user_id}", response_model=ApiResponse[UserResponse], summary="获取用户信息")
async def get_user(user_id: int):
    """
    根据 ID 获取用户信息
    """
    user = await UserService.get_user_by_id(user_id)
    return success_response(data=user)


@router.put("/{user_id}", response_model=ApiResponse[UserResponse], summary="更新用户信息")
async def update_user(user_id: int, user_data: UserUpdateRequest):
    """
    更新用户信息（支持更新用户名、手机号、邮箱）

    - **username**: 用户名（可选，2-50位）
    - **phone**: 手机号（可选，中国大陆格式）
    - **email**: 邮箱（可选）
    """
    user = await UserService.update_user(user_id, user_data)
    return success_response(data=user)


@router.post("/pageList", response_model=ApiResponse[PageResponse[UserResponse]], summary="分页获取用户列表")
async def get_paginated_users(params: UserQueryRequest = Depends()):
    """
    获取用户列表（分页+条件查询）
    - **page**: 页码，从1开始，默认为1
    - **size**: 每页数量，默认为10，最大100
    - **username**: 用户名模糊匹配（可选）
    - **phone**: 手机号模糊匹配（可选）
    - **email**: 邮箱模糊匹配（可选）
    - **activation_code**: 激活码模糊匹配（可选）
    """
    query = UserService.get_user_queryset(params)
    return await paginated_response(query, params)


# ======================== 认证相关接口 ========================

@router.post("/login", response_model=ApiResponse[LoginResponse], summary="用户登录")
async def login_user(login_data: LoginRequest, request: Request):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    登录成功后返回JWT token和用户信息
    """
    login_info = await UserService.login_user(
        username=login_data.username,
        password=login_data.password,
        request=request
    )
    return success_response(data=login_info, message="登录成功")


@router.post("/logout", response_model=ApiResponse[AuthResponse], summary="用户注销")
async def logout_user(request: Request):
    """
    用户注销

    需要在请求头中提供有效的Authorization token
    """
    # 从中间件获取用户信息
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)

    # 获取token
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise BusinessException(message="缺少认证token", code=401)

    from app.util.jwt import get_jwt_manager
    jwt_manager = get_jwt_manager()
    token = jwt_manager.extract_token_from_header(authorization)
    if not token:
        raise BusinessException(message="无效的token格式", code=401)

    await UserService.logout_user(token, user.id)
    return success_response(
        data={"success": True},
        message="注销成功"
    )


@router.post("/logout-all", response_model=ApiResponse[AuthResponse], summary="注销所有设备")
async def logout_all_devices(request: Request):
    """
    注销用户的所有设备

    需要在请求头中提供有效的Authorization token
    """
    # 从中间件获取用户信息
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)

    count = await UserService.logout_all_devices(user.id)
    return success_response(
        data={"success": True, "logged_out_count": count},
        message=f"已注销 {count} 个设备"
    )


@router.get("/profile", response_model=ApiResponse[UserProfileResponse], summary="获取用户档案")
async def get_user_profile(request: Request):
    """
    获取当前用户的详细信息

    需要在请求头中提供有效的Authorization token
    """
    # 从中间件获取用户信息
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)

    profile = UserProfileResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        email=user.email,
        activation_code=user.activation_code,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )

    return success_response(data=profile, message="获取用户档案成功")


@router.get("/sessions", response_model=ApiResponse[SessionsResponse], summary="获取会话列表")
async def get_user_sessions(request: Request):
    """
    获取当前用户的所有活跃会话

    需要在请求头中提供有效的Authorization token
    """
    # 从中间件获取用户信息
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)

    sessions = await UserService.get_user_sessions(user.id)

    # 标记当前会话
    current_device_id = getattr(request.state, 'device_id', None)
    for session in sessions:
        if session["device_info"]["device_id"] == current_device_id:
            session["is_current"] = True
            break

    sessions_response = SessionsResponse(
        sessions=sessions,
        total=len(sessions)
    )

    return success_response(data=sessions_response, message="获取会话列表成功")


@router.post("/refresh-token", response_model=ApiResponse[RefreshTokenResponse], summary="刷新访问令牌")
async def refresh_access_token(request: Request):
    """
    刷新JWT访问令牌

    需要在请求头中提供有效的Authorization token
    """
    # 获取当前token
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise BusinessException(message="缺少认证token", code=401)

    from app.util.jwt import get_jwt_manager
    jwt_manager = get_jwt_manager()
    token = jwt_manager.extract_token_from_header(authorization)
    if not token:
        raise BusinessException(message="无效的token格式", code=401)

    refresh_info = await UserService.refresh_token(token, request)
    return success_response(data=refresh_info, message="Token刷新成功")


@router.post("/change-password", response_model=ApiResponse[AuthResponse], summary="修改密码")
async def change_password(password_data: ChangePasswordRequest, request: Request):
    """
    修改用户密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（8-20位，必须包含大小写字母和数字）

    需要在请求头中提供有效的Authorization token
    """
    # 从中间件获取用户信息
    user = getattr(request.state, 'user', None)
    if not user:
        raise BusinessException(message="用户未登录", code=401)

    # 验证旧密码
    from app.util.password import verify_password
    if not verify_password(password_data.old_password, user.password):
        raise BusinessException(message="旧密码错误", code=400)

    # 验证新密码复杂度
    new_password = password_data.new_password
    if len(new_password) < 8 or len(new_password) > 20:
        raise BusinessException(message="密码长度必须在8-20位之间", code=400)

    has_upper = any(c.isupper() for c in new_password)
    has_lower = any(c.islower() for c in new_password)
    has_digit = any(c.isdigit() for c in new_password)

    if not (has_upper and has_lower and has_digit):
        raise BusinessException(
            message="密码必须包含至少一个大写字母、一个小写字母和一个数字",
            code=400
        )

    # 更新密码
    from app.util.password import hash_password
    hashed_password = hash_password(new_password)
    user.password = hashed_password
    await user.save()

    # 注销所有其他设备（强制重新登录）
    await UserService.logout_all_devices(user.id)

    return success_response(
        data={"success": True},
        message="密码修改成功，请重新登录"
    )


@router.get("/check-auth", response_model=ApiResponse[AuthResponse], summary="检查认证状态")
async def check_authentication(request: Request):
    """
    检查当前token的认证状态

    需要在请求头中提供有效的Authorization token
    """
    # 从中间件获取用户信息
    user = getattr(request.state, 'user', None)
    session = getattr(request.state, 'session', None)

    if not user or not session:
        raise BusinessException(message="认证失效", code=401)

    return success_response(
        data={
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "session_info": await session.get_device_info()
        },
        message="认证有效"
    )

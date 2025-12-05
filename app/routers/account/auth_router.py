from fastapi import APIRouter, Request, Depends

from app.schemas.account.auth import LoginRequest, ChangePasswordRequest
from app.schemas.common.response import ApiResponse, success_response
from app.services.account.auth_service import auth_service
from app.util.auth_context import (
    get_current_user, get_current_user_id, get_current_session
)

router = APIRouter()


@router.post("/login", response_model=ApiResponse[str], summary="用户登录")
async def login_user(login_data: LoginRequest, request: Request):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    登录成功后返回JWT token和用户信息
    """
    access_token = await auth_service.login_user(
        username=login_data.username,
        password=login_data.password,
        request=request
    )
    return success_response(data=access_token)


@router.post("/logout", summary="用户注销")
async def logout_user(session=Depends(get_current_session)):
    """
    用户注销
    """
    await auth_service.logout_user(session.token)
    return success_response(data=True)


@router.post("/logout-all", summary="注销所有设备")
async def logout_all_devices(user_id: int = Depends(get_current_user_id)):
    """
    注销用户的所有设备
    """
    await auth_service.logout_all_devices(user_id)
    return success_response(data=True)


@router.get("/profile", summary="获取用户档案")
async def get_user_profile(user=Depends(get_current_user)):
    """
    获取当前用户的基本信息
    """
    # 返回简化的用户信息
    profile = {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email
    }

    return success_response(data=profile)


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: ChangePasswordRequest,
    user=Depends(get_current_user)
):
    """
    修改用户密码

    - **new_password**: 新密码（8-20位，必须包含大小写字母和数字）
    """
    await auth_service.change_password(
        user=user,
        new_password=password_data.new_password
    )

    return success_response(data=True)

from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.account.auth import LoginRequest, ChangePasswordRequest
from app.schemas.common.response import ApiResponse, success_response
from app.services.account.auth_service import auth_service
from app.util.auth_context import get_current_user, oauth2_scheme

router = APIRouter()


@router.post("/login", summary="用户登录")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    """
    用户登录（支持 OAuth2 表单格式）

    - **username**: 用户名
    - **password**: 密码
    """
    access_token = await auth_service.login_user(
        username=form_data.username,
        password=form_data.password,
        request=request
    )
    # OAuth2 标准返回格式
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", summary="用户注销")
async def logout_user(token: str = Depends(oauth2_scheme)):
    """用户注销"""
    await auth_service.logout_user(token)
    return success_response(data=True)


@router.get("/profile", summary="获取用户档案")
async def get_user_profile(user=Depends(get_current_user)):
    """获取当前用户的基本信息"""
    return success_response(data={
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "email": user.email
    })


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: ChangePasswordRequest,
    user=Depends(get_current_user)
):
    """
    修改用户密码

    - **new_password**: 新密码（8-20位，必须包含大小写字母和数字）
    """
    await auth_service.change_password(user=user, new_password=password_data.new_password)
    return success_response(data=True)

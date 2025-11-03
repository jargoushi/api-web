from fastapi import APIRouter, Depends

from app.schemas.pagination import PageResponse
from app.schemas.response import ApiResponse, success_response, paginated_response
from app.schemas.user import UserResponse, UserRegisterRequest, UserUpdateRequest, UserQueryRequest
from app.services.user_service import UserService
from app.util.auth_context import get_current_user_id

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


@router.get("/", response_model=ApiResponse[UserResponse], summary="获取用户信息")
async def get_user(user_id: int = Depends(get_current_user_id)):
    """
    根据 ID 获取用户信息
    """
    user = await UserService.get_user_by_id(user_id)
    return success_response(data=user)


@router.put("/{user_id}", response_model=ApiResponse[UserResponse], summary="更新用户信息")
async def update_user(user_data: UserUpdateRequest, user_id: int = Depends(get_current_user_id)):
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

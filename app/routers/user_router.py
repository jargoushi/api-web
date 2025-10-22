from fastapi import APIRouter, Depends

from app.schemas.pagination import PageResponse
from app.schemas.response import ApiResponse, success_response, paginated_response
from app.schemas.user import UserResponse, UserCreateRequest, UserUpdateRequest, UserQueryRequest
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=ApiResponse[UserResponse], summary="创建用户")
async def create_user(user_data: UserCreateRequest):
    """
    创建一个新用户
    """
    await UserService.create_user(user_data)
    return success_response()


@router.get("/{user_id}", response_model=ApiResponse[UserResponse], summary="获取单个用户")
async def get_user(user_id: int):
    """
    根据 ID 获取单个用户信息
    """
    user = await UserService.get_user_by_id(user_id)
    return success_response(data=user)


@router.put("/{user_id}", response_model=ApiResponse[UserResponse], summary="更新用户")
async def update_user(user_id: int, user_data: UserUpdateRequest):
    """
    更新用户信息
    """
    await UserService.update_user(user_id, user_data)
    return success_response()


@router.post("/pageList", response_model=ApiResponse[PageResponse[UserResponse]], summary="分页获取用户列表")
async def get_paginated_users(params: UserQueryRequest = Depends()):
    """
    获取用户列表（分页+条件查询）
    - **page**: 页码，从1开始，默认为1
    - **size**: 每页数量，默认为10，最大100
    - **username**: 用户名模糊匹配（可选）
    - **email**: 邮箱模糊匹配（可选）
    - **is_active**: 是否激活（可选）
    """
    query = UserService.get_user_queryset(params)
    return await paginated_response(query, params)

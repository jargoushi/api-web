"""账号管理路由"""

from typing import List

from fastapi import APIRouter, Depends

from app.schemas.common.pagination import PageResponse
from app.schemas.common.response import ApiResponse, success_response, paginated_response
from app.schemas.account.account import (
    AccountResponse, AccountCreateRequest, AccountUpdateRequest, AccountDeleteRequest,
    AccountQueryRequest,
    BindingResponse, BindingRequest, BindingUpdateRequest, BindingDeleteRequest
)
from app.schemas.account.setting import SettingUpdateRequest, AllSettingsResponse, SettingResponse
from app.services.account.account_service import account_service
from app.services.account.setting_service import setting_service
from app.util.auth_context import get_current_user_id

router = APIRouter()


# ========== 账号管理 ==========

@router.post("/pageList", response_model=ApiResponse[PageResponse[AccountResponse]], summary="账号分页列表")
async def get_accounts(params: AccountQueryRequest):
    """
    分页获取账号列表

    - **user_id**: 用户ID（不传则查询所有）
    - **name**: 账号名称（模糊搜索）
    """
    query = account_service.get_account_queryset(params)
    return await paginated_response(query, params)


@router.post("/create", response_model=ApiResponse[AccountResponse], summary="创建账号")
async def create_account(request: AccountCreateRequest, user_id: int = Depends(get_current_user_id)):
    """创建新账号"""
    account = await account_service.create_account(user_id, request)
    return success_response(data=account)


@router.post("/update", response_model=ApiResponse[AccountResponse], summary="更新账号")
async def update_account(request: AccountUpdateRequest):
    """更新账号信息"""
    account = await account_service.update_account(request)
    return success_response(data=account)


@router.post("/delete", response_model=ApiResponse, summary="删除账号")
async def delete_account(request: AccountDeleteRequest):
    """删除账号"""
    await account_service.delete_account(request.id)
    return success_response()


# ========== 项目渠道绑定 ==========

@router.get("/{account_id}/binddings", response_model=ApiResponse[List[BindingResponse]], summary="绑定列表")
async def get_bindings(account_id: int):
    """获取账号的所有项目渠道绑定"""
    bindings = await account_service.get_bindings(account_id)
    return success_response(data=bindings)


@router.post("/{account_id}/binddings/bindding", response_model=ApiResponse[BindingResponse], summary="绑定")
async def bindding(account_id: int, request: BindingRequest):
    """绑定项目渠道"""
    binding = await account_service.bindding(account_id, request)
    return success_response(data=binding)


@router.post("/binddings/update", response_model=ApiResponse[BindingResponse], summary="更新绑定")
async def update_binding(request: BindingUpdateRequest):
    """更新绑定（渠道列表、浏览器ID）"""
    binding = await account_service.update_binding(request)
    return success_response(data=binding)


@router.post("/binddings/unbind", response_model=ApiResponse, summary="解绑")
async def unbind(request: BindingDeleteRequest):
    """解除绑定"""
    await account_service.unbind(request.id)
    return success_response()


# ========== 账号配置 ==========

@router.get("/{account_id}/settings", response_model=ApiResponse[AllSettingsResponse], summary="账号配置")
async def get_account_settings(account_id: int, user_id: int = Depends(get_current_user_id)):
    """获取账号的配置（含继承）"""
    settings = await setting_service.get_account_all_settings(account_id, user_id)
    return success_response(data=settings)


@router.post("/{account_id}/settings/update", response_model=ApiResponse[SettingResponse], summary="更新账号配置")
async def update_account_setting(
    account_id: int, request: SettingUpdateRequest, user_id: int = Depends(get_current_user_id)
):
    """更新账号的配置项"""
    setting = await setting_service.update_account_setting(account_id, request)
    return success_response(data=setting)


@router.post("/{account_id}/settings/reset", response_model=ApiResponse[SettingResponse], summary="重置账号配置")
async def reset_account_setting(account_id: int, setting_key: int, user_id: int = Depends(get_current_user_id)):
    """重置账号配置（恢复继承用户配置）"""
    setting = await setting_service.reset_account_setting(account_id, setting_key)
    return success_response(data=setting)

"""用户配置路由"""

from fastapi import APIRouter, Depends

from app.schemas.common.response import ApiResponse, success_response
from app.schemas.account.setting import (
    SettingUpdateRequest,
    SettingResponse,
    SettingGroupResponse,
    AllSettingsResponse
)
from app.services.account.setting_service import setting_service
from app.util.auth_context import get_current_user_id

router = APIRouter()


@router.get("/", response_model=ApiResponse[AllSettingsResponse], summary="获取所有配置")
async def get_all_settings(user_id: int = Depends(get_current_user_id)):
    """
    获取用户所有配置（合并默认值，按分组组织）
    """
    result = await setting_service.get_all_settings(user_id)
    return success_response(data=result)


@router.get("/{setting_key}", response_model=ApiResponse[SettingResponse], summary="获取单个配置")
async def get_setting(setting_key: int, user_id: int = Depends(get_current_user_id)):
    """
    获取单个配置项

    - **setting_key**: 配置项编码
    """
    result = await setting_service.get_setting(user_id, setting_key)
    return success_response(data=result)


@router.post("/update", response_model=ApiResponse[SettingResponse], summary="更新配置")
async def update_setting(
    request: SettingUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    更新配置项

    - **setting_key**: 配置项编码
    - **setting_value**: 配置值（类型需与配置项定义一致）
    """
    result = await setting_service.update_setting(user_id, request)
    return success_response(data=result)


@router.post("/{setting_key}/reset", response_model=ApiResponse[SettingResponse], summary="重置配置")
async def reset_setting(setting_key: int, user_id: int = Depends(get_current_user_id)):
    """
    重置配置为默认值

    - **setting_key**: 配置项编码
    """
    result = await setting_service.reset_setting(user_id, setting_key)
    return success_response(data=result)


@router.get("/group/{group_code}", response_model=ApiResponse[SettingGroupResponse], summary="按分组获取配置")
async def get_settings_by_group(group_code: int, user_id: int = Depends(get_current_user_id)):
    """
    按分组获取配置

    - **group_code**: 分组编码（1:通用设置 2:通知设置 3:高级设置）
    """
    result = await setting_service.get_settings_by_group(user_id, group_code)
    return success_response(data=result)

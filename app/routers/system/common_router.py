"""公共路由"""

from typing import List

from fastapi import APIRouter

from app.enums.common.channel import ChannelEnum
from app.enums.common.project import ProjectEnum
from app.enums.settings.groups import SettingGroupEnum
from app.schemas.common.common import (
    EnumResponse, SettingsMetadataResponse, SettingGroupMetadata, SettingItemMetadata
)
from app.schemas.common.response import ApiResponse, success_response

router = APIRouter()


@router.get("/channels",
            response_model=ApiResponse[List[EnumResponse]],
            summary="获取所有可用渠道列表")
async def get_channels():
    """获取所有可用的渠道列表"""
    channels = ChannelEnum.get_all()
    return success_response(data=channels)


@router.get("/projects",
            response_model=ApiResponse[List[EnumResponse]],
            summary="获取所有项目列表")
async def get_projects():
    """获取所有可用项目列表"""
    projects = ProjectEnum.get_all()
    return success_response(data=projects)


@router.get("/settings/metadata",
            response_model=ApiResponse[SettingsMetadataResponse],
            summary="获取配置元数据")
async def get_settings_metadata():
    """
    获取配置分组和配置项元数据，供前端渲染设置页面

    返回所有配置分组及其下的配置项，包含类型、默认值、选项等信息
    """
    groups = []
    for group in SettingGroupEnum:
        settings = []
        for setting in group.get_settings():
            settings.append(SettingItemMetadata(
                code=setting.code,
                name=setting.desc,
                type=setting.value_type,
                default=setting.default,
                options=setting.options,
                required=setting.required
            ))
        groups.append(SettingGroupMetadata(
            code=group.code,
            name=group.desc,
            icon=group.icon,
            settings=settings
        ))

    return success_response(data=SettingsMetadataResponse(groups=groups))

"""公共路由"""

from typing import List

from fastapi import APIRouter

from app.enums.common.channel import ChannelEnum
from app.enums.common.project import ProjectEnum
from app.schemas.common.common import EnumResponse
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

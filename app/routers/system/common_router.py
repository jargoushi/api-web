from typing import List

from fastapi import APIRouter

from app.enums.common.channel import ChannelEnum
from app.schemas.common.common import ChannelResponse
from app.schemas.common.response import ApiResponse, success_response

router = APIRouter()


@router.get("/channels",
            response_model=ApiResponse[List[ChannelResponse]],
            summary="获取所有可用渠道列表")
async def get_channels():
    """
    获取所有可用的渠道列表

    返回所有支持的渠道配置，包括：
    - 抖音
    - YouTube
    """
    channels = ChannelEnum.get_all_channels()
    return success_response(data=channels)

"""公共响应模型"""

from pydantic import Field

from app.schemas.common.base import BaseResponseModel


class ChannelResponse(BaseResponseModel):
    """渠道信息响应"""
    code: int = Field(..., description="渠道编码")
    desc: str = Field(..., description="渠道中文描述")

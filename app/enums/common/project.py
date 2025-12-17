"""项目枚举"""

from typing import List

from app.enums.base import BaseCodeEnum
from app.enums.common.channel import ChannelEnum


class ProjectEnum(BaseCodeEnum):
    """项目枚举

    每个项目定义其支持的渠道列表。
    """
    AI_LANDSCAPE = (1, "AI风景号", [ChannelEnum.BILIBILI, ChannelEnum.DOUYIN, ChannelEnum.WECHAT_VIDEO])

    def __new__(cls, code: int, desc: str, channels: List[ChannelEnum]):
        obj = object.__new__(cls)
        obj.code = code
        obj.desc = desc
        obj._channels = channels
        return obj

    @property
    def channels(self) -> List[ChannelEnum]:
        """获取该项目支持的渠道列表"""
        return self._channels

    def to_dict(self):
        """序列化为字典"""
        return {
            "code": self.code,
            "desc": self.desc,
            "channels": [ch.to_dict() for ch in self._channels]
        }

from enum import Enum
from typing import List, Dict


class ChannelEnum(Enum):
    """渠道枚举"""
    XIAOHONGSHU = (1, "小红书")
    BILIBILI = (2, "哔哩哔哩")
    YOUTUBE = (3, "YouTube")
    WECHAT_OFFICIAL = (4, "微信公众号")
    WECHAT_VIDEO = (5, "微信视频号")

    def __new__(cls, code: int, desc: str):
        obj = object.__new__(cls)

        obj.code = code  # 渠道编码
        obj.desc = desc  # 渠道中文描述
        return obj

    @classmethod
    def from_code(cls, code: int) -> "ChannelEnum":
        """根据编码获取枚举成员"""
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的渠道编码: {code}")

    def to_dict(self) -> Dict[str, any]:
        """序列化为字典"""
        return {
            "code": self.code,
            "desc": self.desc
        }

    @classmethod
    def get_all_channels(cls) -> List[Dict[str, any]]:
        """获取所有渠道列表"""
        return [member.to_dict() for member in cls]

from app.enums.base import BaseCodeEnum


class ChannelEnum(BaseCodeEnum):
    """渠道枚举"""
    DOUYIN = (1, "抖音")
    YOUTUBE = (2, "YouTube")
    BILIBILI = (3, "哔哩哔哩")
    WECHAT_VIDEO = (4, "视频号")

from app.enums.base import BaseCodeEnum


class ChannelEnum(BaseCodeEnum):
    """渠道枚举"""
    XIAOHONGSHU = (1, "小红书")
    BILIBILI = (2, "哔哩哔哩")
    YOUTUBE = (3, "YouTube")
    WECHAT_OFFICIAL = (4, "微信公众号")
    WECHAT_VIDEO = (5, "微信视频号")

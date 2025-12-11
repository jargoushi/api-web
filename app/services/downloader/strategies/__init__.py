"""下载策略模块"""

from app.services.downloader.strategies.base import BaseDownloadStrategy
from app.services.downloader.strategies.xiaohongshu import XiaohongshuStrategy
from app.services.downloader.strategies.bilibili import BilibiliStrategy
from app.services.downloader.strategies.youtube import YoutubeStrategy
from app.services.downloader.strategies.wechat_official import WechatOfficialStrategy
from app.services.downloader.strategies.wechat_video import WechatVideoStrategy

__all__ = [
    "BaseDownloadStrategy",
    "XiaohongshuStrategy",
    "BilibiliStrategy",
    "YoutubeStrategy",
    "WechatOfficialStrategy",
    "WechatVideoStrategy",
]

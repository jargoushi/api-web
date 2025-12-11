"""下载策略模块"""

from app.services.downloader.strategies.base import BaseDownloadStrategy
from app.services.downloader.strategies.douyin import DouyinStrategy
from app.services.downloader.strategies.youtube import YoutubeStrategy

__all__ = [
    "BaseDownloadStrategy",
    "DouyinStrategy",
    "YoutubeStrategy",
]

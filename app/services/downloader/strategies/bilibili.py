"""哔哩哔哩下载策略"""

from app.core.exceptions import BusinessException
from app.services.downloader.strategies.base import BaseDownloadStrategy


class BilibiliStrategy(BaseDownloadStrategy):
    """哔哩哔哩下载策略"""

    url_patterns = ["bilibili.com", "b23.tv"]

    async def download(self, url: str) -> str:
        # TODO: 实现下载逻辑
        raise BusinessException(message="B站下载功能待实现")

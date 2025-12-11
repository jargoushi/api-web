"""抖音下载策略"""

from app.core.exceptions import BusinessException
from app.services.downloader.strategies.base import BaseDownloadStrategy


class DouyinStrategy(BaseDownloadStrategy):
    """抖音下载策略"""

    url_patterns = ["douyin.com", "iesdouyin.com"]

    async def download(self, url: str) -> str:
        # TODO: 实现下载逻辑
        raise BusinessException(message="抖音下载功能待实现")

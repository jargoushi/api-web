"""小红书下载策略"""

from app.core.exceptions import BusinessException
from app.services.downloader.strategies.base import BaseDownloadStrategy


class XiaohongshuStrategy(BaseDownloadStrategy):
    """小红书下载策略"""

    url_patterns = ["xiaohongshu.com", "xhslink.com", "xhs.cn"]

    async def download(self, url: str) -> str:
        # TODO: 实现下载逻辑
        raise BusinessException(message="小红书下载功能待实现")

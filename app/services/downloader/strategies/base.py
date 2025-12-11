"""下载策略基类"""

from abc import ABC, abstractmethod
from typing import List


class BaseDownloadStrategy(ABC):
    """下载策略基类"""

    # URL 匹配模式
    url_patterns: List[str] = []

    @classmethod
    def can_handle(cls, url: str) -> bool:
        """判断是否能处理该 URL"""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in cls.url_patterns)

    @abstractmethod
    async def download(self, url: str) -> str:
        """
        下载视频

        Args:
            url: 视频 URL

        Returns:
            下载后的绝对路径

        Raises:
            BusinessException: 下载失败时抛出
        """
        pass

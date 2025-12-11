"""策略注册表"""

from typing import List, Optional, Type
from app.services.downloader.strategies.base import BaseDownloadStrategy
from app.services.downloader.strategies.douyin import DouyinStrategy
from app.services.downloader.strategies.youtube import YoutubeStrategy


class StrategyRegistry:
    """策略注册表，根据 URL 自动选择策略"""

    _strategies: List[Type[BaseDownloadStrategy]] = [
        DouyinStrategy,
        YoutubeStrategy,
    ]

    @classmethod
    def get_strategy(cls, url: str) -> Optional[BaseDownloadStrategy]:
        """根据 URL 获取匹配的策略实例"""
        for strategy_class in cls._strategies:
            if strategy_class.can_handle(url):
                return strategy_class()
        return None

    @classmethod
    def get_supported_patterns(cls) -> List[str]:
        """获取支持的 URL 模式列表"""
        patterns = []
        for s in cls._strategies:
            patterns.extend(s.url_patterns)
        return patterns

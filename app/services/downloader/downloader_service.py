"""下载服务"""

from typing import Callable, Optional

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.services.downloader.strategy_registry import StrategyRegistry


# 进度回调类型
ProgressCallback = Callable[[int, int], None]


async def download(
    url: str,
    user_id: int,
    on_progress: Optional[ProgressCallback] = None
) -> str:
    """
    下载视频

    Args:
        url: 视频 URL
        user_id: 用户 ID（用于获取下载配置）
        on_progress: 进度回调 (downloaded_bytes, total_bytes)

    Returns:
        下载后的文件绝对路径

    Raises:
        BusinessException: 下载失败时抛出

    Example:
        from app.services.downloader import download

        path = await download(
            url="https://www.youtube.com/watch?v=xxx",
            user_id=1
        )
    """
    log.info(f"开始下载: {url}")

    strategy = StrategyRegistry.get_strategy(url)

    if strategy is None:
        patterns = ", ".join(StrategyRegistry.get_supported_patterns())
        raise BusinessException(message=f"不支持的URL，支持的域名: {patterns}")

    path = await strategy.download(url, user_id, on_progress)

    log.info(f"下载完成: {path}")
    return path

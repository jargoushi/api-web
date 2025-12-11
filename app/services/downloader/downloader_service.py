"""下载服务"""

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.services.downloader.strategy_registry import StrategyRegistry


async def download(url: str) -> str:
    """
    下载视频

    Args:
        url: 视频 URL

    Returns:
        下载后的绝对路径

    Raises:
        BusinessException: 下载失败时抛出

    Example:
        from app.services.downloader import download

        path = await download("https://www.xiaohongshu.com/explore/xxx")
    """
    log.info(f"开始下载: {url}")

    strategy = StrategyRegistry.get_strategy(url)

    if strategy is None:
        patterns = ", ".join(StrategyRegistry.get_supported_patterns())
        raise BusinessException(message=f"不支持的URL，支持的域名: {patterns}")

    path = await strategy.download(url)

    log.info(f"下载完成: {path}")
    return path

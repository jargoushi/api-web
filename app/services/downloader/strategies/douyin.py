"""抖音下载策略"""

from typing import Optional

from app.services.downloader.download_config import DownloadConfig
from app.services.downloader.strategies.base import BaseDownloadStrategy, ProgressCallback
from app.util import yt_dlp_util


class DouyinStrategy(BaseDownloadStrategy):
    """
    抖音下载策略

    使用 yt-dlp 下载抖音视频。
    """

    url_patterns = ["douyin.com", "iesdouyin.com"]

    async def _do_download(
        self,
        url: str,
        config: DownloadConfig,
        on_progress: Optional[ProgressCallback],
        context: dict
    ) -> str:
        """使用 yt-dlp 工具类下载"""
        return await yt_dlp_util.download(
            url=url,
            output_dir=config.download_path,
            proxy=config.proxy,
            on_progress=on_progress,
            extra_opts={
                # 抖音特有配置
                "format": "best",
            }
        )

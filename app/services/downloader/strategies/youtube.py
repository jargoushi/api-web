"""YouTube下载策略"""

from typing import Optional

from app.services.downloader.download_config import DownloadConfig
from app.services.downloader.strategies.base import BaseDownloadStrategy, ProgressCallback
from app.util import yt_dlp_util


class YoutubeStrategy(BaseDownloadStrategy):
    """
    YouTube下载策略

    使用 yt-dlp 下载 YouTube 视频。
    """

    url_patterns = ["youtube.com", "youtu.be"]

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
                # YouTube 特有配置：优先选择最佳 mp4 格式
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
            }
        )

"""
下载模块

使用方式：
    from app.services.downloader import download

    path = await download("https://www.xiaohongshu.com/explore/xxx")
"""

from app.services.downloader.downloader_service import download

__all__ = ["download"]

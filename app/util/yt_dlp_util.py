"""yt-dlp 下载工具类

封装 yt-dlp 的调用细节，提供简洁 API 供下载策略使用。
"""

import asyncio
from pathlib import Path
from typing import Callable, Dict, Optional

import yt_dlp

from app.core.exceptions import BusinessException
from app.core.logging import log


# 进度回调类型: (已下载字节数, 总字节数)
ProgressCallback = Callable[[int, int], None]


async def download(
    url: str,
    output_dir: str,
    proxy: Optional[str] = None,
    cookies_file: Optional[str] = None,
    on_progress: Optional[ProgressCallback] = None,
    extra_opts: Optional[Dict] = None
) -> str:
    """
    使用 yt-dlp 下载视频

    Args:
        url: 视频 URL
        output_dir: 输出目录
        proxy: 代理地址（可选）
        on_progress: 进度回调 (downloaded_bytes, total_bytes)
        extra_opts: 额外的 yt-dlp 配置（可选）

    Returns:
        下载后的文件绝对路径

    Raises:
        BusinessException: 下载失败时抛出

    Example:
        from app.util import yt_dlp_util

        path = await yt_dlp_util.download(
            url="https://www.youtube.com/watch?v=xxx",
            output_dir="./downloads",
            proxy="http://127.0.0.1:7890"
        )
    """
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 构建配置
    ydl_opts = _build_opts(output_dir, proxy, cookies_file, on_progress)

    # 合并额外配置
    if extra_opts:
        ydl_opts.update(extra_opts)

    # 在线程池中执行下载
    try:
        return await asyncio.to_thread(_execute_download, url, ydl_opts)
    except Exception as e:
        log.error(f"yt-dlp 下载失败: {url}, 错误: {e}")
        raise BusinessException(message=f"下载失败: {str(e)}")


def _build_opts(
    output_dir: str,
    proxy: Optional[str],
    cookies_file: Optional[str],
    on_progress: Optional[ProgressCallback]
) -> Dict:
    """构建 yt-dlp 配置"""
    opts = {
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "format": "best",
        "quiet": True,
        "no_warnings": True,
    }

    if proxy:
        opts["proxy"] = proxy

    # 如果提供了 cookies 文件则使用
    if cookies_file:
        opts["cookiefile"] = cookies_file

    if on_progress:
        opts["progress_hooks"] = [_create_progress_hook(on_progress)]

    return opts


def _create_progress_hook(on_progress: ProgressCallback):
    """创建进度回调钩子"""
    def hook(d):
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total > 0:
                on_progress(downloaded, total)
    return hook


def _execute_download(url: str, ydl_opts: Dict) -> str:
    """执行下载（同步方法）"""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        log.info(f"yt-dlp 下载完成: {filepath}")
        return filepath

"""微信视频号下载策略"""

from app.core.exceptions import BusinessException
from app.services.downloader.strategies.base import BaseDownloadStrategy


class WechatVideoStrategy(BaseDownloadStrategy):
    """微信视频号下载策略"""

    url_patterns = ["channels.weixin.qq.com", "finder.video.qq.com"]

    async def download(self, url: str) -> str:
        # TODO: 实现下载逻辑
        raise BusinessException(message="微信视频号下载功能待实现")

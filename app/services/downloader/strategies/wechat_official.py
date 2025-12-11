"""微信公众号下载策略"""

from app.core.exceptions import BusinessException
from app.services.downloader.strategies.base import BaseDownloadStrategy


class WechatOfficialStrategy(BaseDownloadStrategy):
    """微信公众号下载策略"""

    url_patterns = ["mp.weixin.qq.com"]

    async def download(self, url: str) -> str:
        # TODO: 实现下载逻辑
        raise BusinessException(message="微信公众号下载功能待实现")

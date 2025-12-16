"""下载策略基类 - 模板方法模式"""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from app.core.logging import log
from app.services.downloader.download_config import DownloadConfig


# 进度回调类型: (已下载字节数, 总字节数)
ProgressCallback = Callable[[int, int], None]


class BaseDownloadStrategy(ABC):
    """
    下载策略基类 - 模板方法模式

    定义下载流程骨架，子类实现具体下载逻辑。
    本基类不依赖任何第三方下载库。
    """

    # URL 匹配模式，子类必须定义
    url_patterns: List[str] = []

    @classmethod
    def can_handle(cls, url: str) -> bool:
        """判断是否能处理该 URL"""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in cls.url_patterns)

    async def download(
        self,
        url: str,
        user_id: int,
        on_progress: Optional[ProgressCallback] = None
    ) -> str:
        """
        模板方法：定义下载流程骨架

        Args:
            url: 视频 URL
            user_id: 用户 ID（用于获取配置）
            on_progress: 进度回调 (downloaded_bytes, total_bytes)

        Returns:
            下载后的文件绝对路径

        Raises:
            BusinessException: 下载失败时抛出
        """
        log.info(f"[{self.__class__.__name__}] 开始下载: {url}")

        # 1. 获取用户下载配置（公共步骤，单次查询）
        config = await DownloadConfig.from_user(user_id)

        # 2. 准备工作（可选钩子）
        context = await self._prepare(url)

        # 3. 执行下载（子类实现）
        path = await self._do_download(url, config, on_progress, context)

        # 4. 后处理（可选钩子）
        path = await self._post_process(path, context)

        log.info(f"[{self.__class__.__name__}] 下载完成: {path}")
        return path

    # ===== 钩子方法（子类可选覆盖）=====

    async def _prepare(self, url: str) -> dict:
        """
        准备工作钩子

        子类可覆盖此方法进行 URL 预处理、解析真实链接等操作。
        """
        return {}

    async def _post_process(self, path: str, context: dict) -> str:
        """
        后处理钩子

        子类可覆盖此方法进行格式转换、文件重命名等操作。
        """
        return path

    # ===== 抽象方法（子类必须实现）=====

    @abstractmethod
    async def _do_download(
        self,
        url: str,
        config: DownloadConfig,
        on_progress: Optional[ProgressCallback],
        context: dict
    ) -> str:
        """
        执行下载

        Args:
            url: 视频 URL
            config: 下载配置对象
            on_progress: 进度回调
            context: 准备阶段返回的上下文

        Returns:
            下载后的文件绝对路径
        """
        pass

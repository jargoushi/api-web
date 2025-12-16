# 下载模块测试文件
import asyncio
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class DownloaderTester:
    """下载模块测试类"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_user_id = 1
        self.test_output_dir = "./test_downloads"

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({"test_name": test_name, "success": success})

    async def test_download_config_default(self):
        """测试1: 获取默认下载配置"""
        print("\n测试1: 获取默认下载配置")
        try:
            from app.services.downloader.download_config import DownloadConfig

            config = DownloadConfig.default()
            assert config.download_path == "./downloads"
            assert config.proxy is None
            self.log_test_result("获取默认下载配置", True, f"path={config.download_path}")
        except Exception as e:
            self.log_test_result("获取默认下载配置", False, str(e))

    async def test_download_setting_enum(self):
        """测试2: 下载设置枚举结构"""
        print("\n测试2: 下载设置枚举结构")
        try:
            from app.enums.settings import DownloadSettingEnum

            assert len(list(DownloadSettingEnum)) == 2
            assert DownloadSettingEnum.DOWNLOAD_PATH.code == 401
            assert DownloadSettingEnum.PROXY_URL.code == 402
            self.log_test_result("下载设置枚举结构", True, "2个配置项")
        except Exception as e:
            self.log_test_result("下载设置枚举结构", False, str(e))

    async def test_youtube_strategy_can_handle(self):
        """测试3: YouTube策略URL匹配"""
        print("\n测试3: YouTube策略URL匹配")
        try:
            from app.services.downloader.strategies.youtube import YoutubeStrategy

            assert YoutubeStrategy.can_handle("https://www.youtube.com/watch?v=abc123")
            assert YoutubeStrategy.can_handle("https://youtu.be/abc123")
            assert not YoutubeStrategy.can_handle("https://www.bilibili.com/video/xxx")
            self.log_test_result("YouTube策略URL匹配", True)
        except Exception as e:
            self.log_test_result("YouTube策略URL匹配", False, str(e))

    async def test_douyin_strategy_can_handle(self):
        """测试4: 抖音策略URL匹配"""
        print("\n测试4: 抖音策略URL匹配")
        try:
            from app.services.downloader.strategies.douyin import DouyinStrategy

            assert DouyinStrategy.can_handle("https://www.douyin.com/video/123456")
            assert DouyinStrategy.can_handle("https://v.douyin.com/abc123")
            assert DouyinStrategy.can_handle("https://www.iesdouyin.com/share/video/123")
            assert not DouyinStrategy.can_handle("https://www.youtube.com/watch?v=abc")
            self.log_test_result("抖音策略URL匹配", True)
        except Exception as e:
            self.log_test_result("抖音策略URL匹配", False, str(e))

    async def test_downloader_service_get_strategy(self):
        """测试5: 下载服务策略获取"""
        print("\n测试5: 下载服务策略获取")
        try:
            from app.services.downloader.strategy_registry import StrategyRegistry
            from app.services.downloader.strategies.youtube import YoutubeStrategy
            from app.services.downloader.strategies.douyin import DouyinStrategy

            youtube_strategy = StrategyRegistry.get_strategy("https://www.youtube.com/watch?v=abc")
            assert isinstance(youtube_strategy, YoutubeStrategy)

            douyin_strategy = StrategyRegistry.get_strategy("https://www.douyin.com/video/123")
            assert isinstance(douyin_strategy, DouyinStrategy)

            self.log_test_result("下载服务策略获取", True)
        except Exception as e:
            self.log_test_result("下载服务策略获取", False, str(e))

    async def test_downloader_service_unsupported_url(self):
        """测试6: 不支持的URL应返回None"""
        print("\n测试6: 不支持的URL应返回None")
        try:
            from app.services.downloader.strategy_registry import StrategyRegistry

            strategy = StrategyRegistry.get_strategy("https://unsupported-site.com/video/123")
            assert strategy is None
            self.log_test_result("不支持的URL应返回None", True, "正确返回 None")
        except Exception as e:
            self.log_test_result("不支持的URL应返回None", False, str(e))

    async def test_yt_dlp_util_import(self):
        """测试7: yt_dlp_util 模块可正常导入"""
        print("\n测试7: yt_dlp_util 模块可正常导入")
        try:
            from app.util import yt_dlp_util
            assert hasattr(yt_dlp_util, 'download')
            self.log_test_result("yt_dlp_util 模块可正常导入", True)
        except Exception as e:
            self.log_test_result("yt_dlp_util 模块可正常导入", False, str(e))

    async def test_progress_callback(self):
        """测试8: 进度回调类型定义"""
        print("\n测试8: 进度回调类型定义")
        try:
            from app.services.downloader.strategies.base import ProgressCallback

            # 测试回调函数可以正常定义和调用
            progress_data = []

            def my_callback(downloaded: int, total: int):
                progress_data.append((downloaded, total))

            # 类型兼容性（Python 不会运行时检查，只是确保定义存在）
            callback: ProgressCallback = my_callback
            callback(100, 1000)

            assert progress_data == [(100, 1000)]
            self.log_test_result("进度回调类型定义", True)
        except Exception as e:
            self.log_test_result("进度回调类型定义", False, str(e))

    async def run_all_tests(self):
        print("=" * 80)
        print("开始下载模块测试")
        print("=" * 80)

        try:
            await self.test_download_config_default()
            await self.test_download_setting_enum()
            await self.test_youtube_strategy_can_handle()
            await self.test_douyin_strategy_can_handle()
            await self.test_downloader_service_get_strategy()
            await self.test_downloader_service_unsupported_url()
            await self.test_yt_dlp_util_import()
            await self.test_progress_callback()

            total = len(self.test_results)
            passed = sum(1 for r in self.test_results if r["success"])
            print("\n" + "=" * 80)
            print(f"测试结果: {passed}/{total} 通过，成功率 {passed/total*100:.0f}%")
            print("=" * 80)

        except Exception as e:
            print(f"测试过程中出现错误: {e}")


class DownloaderIntegrationTester:
    """下载模块集成测试类（需要网络）"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_output_dir = "./test_downloads"

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({"test_name": test_name, "success": success})

    async def test_youtube_download(self, url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        """集成测试: YouTube视频下载"""
        print(f"\n集成测试: YouTube视频下载 ({url})")
        try:
            from app.util import yt_dlp_util

            def progress_callback(downloaded: int, total: int):
                percent = downloaded / total * 100 if total > 0 else 0
                print(f"  下载进度: {percent:.1f}%", end="\r")

            filepath = await yt_dlp_util.download(
                url=url,
                output_dir=self.test_output_dir,
                on_progress=progress_callback,
                extra_opts={
                    "format": "bestvideo[height<=480]+bestaudio/best[height<=480]",  # 低分辨率用于测试
                }
            )
            print()  # 换行
            self.log_test_result("YouTube视频下载", True, f"保存至: {filepath}")
        except Exception as e:
            self.log_test_result("YouTube视频下载", False, str(e))

    async def test_douyin_download(self, url: str):
        """集成测试: 抖音视频下载"""
        print(f"\n集成测试: 抖音视频下载 ({url})")
        try:
            from app.util import yt_dlp_util

            filepath = await yt_dlp_util.download(
                url=url,
                output_dir=self.test_output_dir,
                extra_opts={"format": "best"}
            )
            self.log_test_result("抖音视频下载", True, f"保存至: {filepath}")
        except Exception as e:
            self.log_test_result("抖音视频下载", False, str(e))

    async def run_integration_tests(self, youtube_url: str = None, douyin_url: str = None):
        """运行集成测试（需要提供有效URL）"""
        print("=" * 80)
        print(f"开始下载模块集成测试（需要网络）, {youtube_url}, {douyin_url}")
        print("=" * 80)

        if youtube_url:
            await self.test_youtube_download(youtube_url)

        if douyin_url:
            await self.test_douyin_download(douyin_url)

        if not youtube_url and not douyin_url:
            print("未提供测试URL，跳过集成测试")
            return

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        print("\n" + "=" * 80)
        print(f"集成测试结果: {passed}/{total} 通过")
        print("=" * 80)


async def main():
    """主测试入口"""
    tester = DownloaderTester()
    await tester.run_all_tests()


async def run_integration_tests(youtube_url: str = None, douyin_url: str = None):
    """运行集成测试"""
    tester = DownloaderIntegrationTester()
    await tester.run_integration_tests(youtube_url, douyin_url)


if __name__ == "__main__":
    # 运行单元测试
    # asyncio.run(main())

    # 运行集成测试
    asyncio.run(run_integration_tests(
        # 使用标准抖音视频链接格式
        douyin_url="https://www.douyin.com/video/7580327048770506027"
    ))


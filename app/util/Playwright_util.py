import asyncio
import random
import uuid
from typing import Optional, Dict, Callable

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class PlaywrightUtil:
    """
    一个简单易用的异步 Playwright 服务，仅支持 XPath 定位。
    """

    def __init__(
            self,
            ws_endpoint: Optional[str] = None,
            headless: bool = True
    ):
        """
        初始化 PlaywrightUtil

        Args:
            ws_endpoint: 可选，如果提供则连接到已存在的浏览器
            headless: 是否以无头模式运行 (仅在启动新浏览器时有效)
        """
        self.ws_endpoint = ws_endpoint
        self.headless = headless

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: Dict[str, Page] = {}
        self._default_page_id: Optional[str] = None

    async def start_browser(self):
        """启动或连接到浏览器。"""
        if self.browser:
            print("浏览器已经启动或连接。")
            return

        self.playwright = await async_playwright().start()

        if self.ws_endpoint:
            print(f"正在连接到浏览器: {self.ws_endpoint}")
            self.browser = await self.playwright.chromium.connect_over_cdp(self.ws_endpoint)
        else:
            print(f"正在启动新的 Chromium 浏览器 (无头模式: {self.headless})...")
            self.browser = await self.playwright.chromium.launch(headless=self.headless)

        # 创建一个独立的浏览器上下文，用于隔离会话
        self.context = await self.browser.new_context()

        # 创建一个默认页面
        default_page = await self.context.new_page()
        self._default_page_id = str(uuid.uuid4())
        self.pages[self._default_page_id] = default_page
        print(f"浏览器已就绪，默认页面 ID: {self._default_page_id}")

    # --- 新增：便捷的自动化脚本植入方法 ---
    async def run_automation(self, automation_func: Callable, *args, **kwargs):
        """
        便捷的自动化脚本执行方法，自动管理浏览器生命周期。

        Args:
            automation_func: 异步函数，接收 PlaywrightUtil 实例作为第一个参数
            *args: 传递给 automation_func 的位置参数
            **kwargs: 传递给 automation_func 的关键字参数
        """
        await self.start_browser()
        try:
            await automation_func(self, *args, **kwargs)
        finally:
            await self.close_browser()

    async def close_browser(self):
        """关闭浏览器并清理资源。"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.pages = {}
            self._default_page_id = None
            print("浏览器已关闭。")
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    def _get_page(self, page_id: Optional[str] = None) -> Page:
        """内部方法：根据 ID 获取 Page 对象。"""
        if not self.pages:
            raise RuntimeError("浏览器未启动或没有可用页面。")

        target_id = page_id or self._default_page_id
        if not target_id or target_id not in self.pages:
            raise ValueError(f"页面 ID '{page_id}' 无效或不存在。")

        return self.pages[target_id]

    async def new_page(self, url: Optional[str] = None) -> str:
        """
        创建一个新页面并返回其 ID。

        Args:
            url: 可选，创建页面后直接导航到此 URL。

        Returns:
            新页面的唯一 ID。
        """
        if not self.context:
            raise RuntimeError("浏览器未启动，无法创建新页面。")

        page = await self.context.new_page()
        page_id = str(uuid.uuid4())
        self.pages[page_id] = page
        print(f"已创建新页面，ID: {page_id}")

        if url:
            await page.goto(url)

        return page_id

    async def close_page(self, page_id: str):
        """关闭指定 ID 的页面。"""
        page = self._get_page(page_id)
        await page.close()
        del self.pages[page_id]
        print(f"已关闭页面: {page_id}")

    # --- 页面级操作 ---

    async def goto(self, url: str, page_id: Optional[str] = None):
        """导航到指定 URL。"""
        page = self._get_page(page_id)
        await page.goto(url)

    async def screenshot(self, file_path: str, page_id: Optional[str] = None):
        """对当前页面截图。"""
        page = self._get_page(page_id)
        await page.screenshot(path=file_path)
        print(f"截图已保存至: {file_path}")

    async def get_title(self, page_id: Optional[str] = None) -> str:
        """获取页面标题。"""
        page = self._get_page(page_id)
        return await page.title()

    # --- 元素级操作 (仅限 XPath) ---

    async def click(self, xpath: str, page_id: Optional[str] = None):
        """点击匹配 XPath 的元素。"""
        page = self._get_page(page_id)
        await page.locator(f'xpath={xpath}').click()

    async def fill(self, xpath: str, value: str, page_id: Optional[str] = None):
        """在匹配 XPath 的输入框中填写文本。"""
        page = self._get_page(page_id)
        await page.locator(f'xpath={xpath}').fill(value)

    async def get_text(self, xpath: str, page_id: Optional[str] = None) -> Optional[str]:
        """获取匹配 XPath 的元素的文本内容。"""
        page = self._get_page(page_id)
        return await page.locator(f'xpath={xpath}').text_content()

    async def wait_for_element(self, xpath: str, timeout: int = 30000, page_id: Optional[str] = None):
        """等待匹配 XPath 的元素出现。"""
        page = self._get_page(page_id)
        await page.wait_for_selector(f'xpath={xpath}', timeout=timeout)

    # --- 实现上下文管理器协议 ---
    async def __aenter__(self):
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()

    @staticmethod
    async def random_wait(min_seconds: float = 1.0, max_seconds: float = 5.0):
        """
        随机等待一段时间

        Args:
            min_seconds: 最小等待时间（秒）
            max_seconds: 最大等待时间（秒）
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(wait_time)
        print(f"随机等待了 {wait_time:.2f} 秒")

    @staticmethod
    async def smart_wait(base_delay: float = 2.0, variability: float = 0.5):
        """
        智能等待，基于正态分布生成更自然的等待时间

        Args:
            base_delay: 基础等待时间
            variability: 时间波动范围（标准差）
        """
        wait_time = max(0.5, random.gauss(base_delay, variability))
        await asyncio.sleep(wait_time)
        print(f"智能等待了 {wait_time:.2f} 秒")

    async def wait_for_network_idle(
            self,
            timeout: int = 30000,
            page_id: Optional[str] = None
    ):
        """
        等待网络空闲

        Args:
            timeout: 超时时间
            page_id: 页面ID
        """
        page = self._get_page(page_id)
        await page.wait_for_load_state('networkidle', timeout=timeout)
        print("网络已空闲")

    async def wait_for_element_with_retry(
            self,
            xpath: str,
            max_retries: int = 3,
            base_timeout: int = 5000,
            page_id: Optional[str] = None
    ):
        """
        带重试机制的等待元素出现

        Args:
            xpath: 元素XPath
            max_retries: 最大重试次数
            base_timeout: 基础超时时间
            page_id: 页面ID
        """
        page = self._get_page(page_id)

        for attempt in range(max_retries):
            try:
                await page.wait_for_selector(f'xpath={xpath}', timeout=base_timeout)
                print(f"元素找到，重试次数: {attempt}")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    backoff_time = (2 ** attempt) * random.uniform(0.5, 1.5)
                    print(f"第 {attempt + 1} 次重试失败，{backoff_time:.2f} 秒后重试")
                    await asyncio.sleep(backoff_time)
                else:
                    print(f"所有重试失败: {e}")
                    raise

        return False

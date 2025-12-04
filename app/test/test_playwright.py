# 独立的自动化脚本函数
import asyncio
from typing import List, Dict, Any

from app.schemas.monitor.browser import BrowserListRequest, BrowserOpenRequest
from app.services.monitor.browser_service import bit_browser_service
from app.util.Playwright_util import PlaywrightUtil


async def browser_automation_script(util: PlaywrightUtil, browser_id: str):
    """
    浏览器自动化脚本

    Args:
        util: PlaywrightUtil实例
        browser_id: 浏览器ID（用于标识）
    """
    try:
        print(f"开始执行浏览器 {browser_id} 的自动化脚本")

        # 访问百度
        await util.goto("https://www.baidu.com")
        print(f"浏览器 {browser_id}: 已访问百度")

        # 搜索
        search_term = f"浏览器{browser_id}自动化测试"
        await util.fill("//*[@id='chat-textarea']", search_term)
        await util.click("//*[@id='chat-submit-button']")
        print(f"浏览器 {browser_id}: 已搜索 '{search_term}'")

        # 截图
        screenshot_name = f"browser_{browser_id}_result.png"
        await util.screenshot(screenshot_name)
        print(f"浏览器 {browser_id}: 截图已保存 - {screenshot_name}")

        print(f"浏览器 {browser_id} 的自动化脚本执行完成")

    except Exception as e:
        print(f"浏览器 {browser_id} 自动化脚本执行失败: {e}")
        raise


class PlaywrightIntegrationTester:
    """Playwright集成测试类"""

    def __init__(self):
        self.browser_ws_list: List[str] = []
        self.automation_tasks: List[asyncio.Task] = []

    @staticmethod
    async def get_all_browsers() -> List[Dict[str, Any]]:
        """获取所有浏览器窗口列表"""
        try:
            # 构建查询参数
            request = BrowserListRequest(page=1, size=100)  # 获取前100个浏览器

            # 调用API获取浏览器列表
            response = await bit_browser_service.get_browser_list(request)

            print(f"获取到 {len(response.list)} 个浏览器窗口")
            for browser in response.list:
                print(f"  - ID: {browser.id}, 名称: {browser.name}, 状态: {browser.status}")

            return response.list

        except Exception as e:
            print(f"获取浏览器列表失败: {e}")
            return []

    async def open_all_browsers(self, browser_list: List[Dict[str, Any]]) -> bool:
        """打开所有浏览器窗口并获取WebSocket地址"""
        try:
            # 提取所有浏览器ID
            browser_ids = [browser.id for browser in browser_list]

            if not browser_ids:
                print("没有可用的浏览器窗口")
                return False

            # 构建打开请求
            request = BrowserOpenRequest(ids=browser_ids)

            # 批量打开浏览器
            print(f"正在打开 {len(browser_ids)} 个浏览器窗口...")
            response = await bit_browser_service.open_browser(request)

            # 收集成功的WebSocket地址
            self.browser_ws_list = []
            for result in response.results:
                if result.success and result.data:
                    ws_url = result.data.ws
                    self.browser_ws_list.append(ws_url)
                    print(f"  ✓ 浏览器 {result.id} 打开成功: {ws_url}")
                else:
                    print(f"  ✗ 浏览器 {result.id} 打开失败: {result.error}")

            print(f"成功打开 {len(self.browser_ws_list)} 个浏览器窗口")
            return len(self.browser_ws_list) > 0

        except Exception as e:
            print(f"打开浏览器失败: {e}")
            return False

    @staticmethod
    async def run_single_automation(ws_url: str, browser_id: str):
        """
        使用run_automation方法执行单个自动化脚本

        Args:
            ws_url: WebSocket连接地址
            browser_id: 浏览器ID
        """
        try:
            # 创建PlaywrightUtil实例
            util = PlaywrightUtil(ws_endpoint=ws_url, headless=False)

            # 使用run_automation方法执行自动化脚本
            await util.run_automation(browser_automation_script, browser_id)

        except Exception as e:
            print(f"执行浏览器 {browser_id} 自动化脚本时出错: {e}")

    async def run_concurrent_automations(self):
        """并发执行自动化脚本"""
        if not self.browser_ws_list:
            print("没有可用的浏览器连接")
            return

        print(f"开始并发执行 {len(self.browser_ws_list)} 个自动化脚本...")

        # 创建并发任务
        tasks = []
        for i, ws_url in enumerate(self.browser_ws_list):
            # 从ws_url中提取browser_id（简化处理）
            browser_id = f"browser_{i + 1}"
            task = asyncio.create_task(
                self.run_single_automation(ws_url, browser_id)
            )
            tasks.append(task)

        # 等待所有任务完成
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
            print("所有自动化脚本执行完成")
        except Exception as e:
            print(f"并发执行过程中出现错误: {e}")

    @staticmethod
    async def close_all_browsers():
        """关闭所有浏览器窗口"""
        try:
            print("正在关闭所有浏览器窗口...")
            await bit_browser_service.close_all_browsers()
            print("所有浏览器窗口已关闭")
        except Exception as e:
            print(f"关闭浏览器失败: {e}")

    async def run_full_test(self):
        """运行完整的测试流程"""
        print("=" * 60)
        print("开始Playwright集成测试")
        print("=" * 60)

        try:
            # 步骤1: 获取所有浏览器
            print("\n步骤1: 获取浏览器列表")
            browser_list = await self.get_all_browsers()

            if not browser_list:
                print("没有找到可用的浏览器，测试终止")
                return

            # 步骤2: 打开所有浏览器
            print("\n步骤2: 打开所有浏览器窗口")
            success = await self.open_all_browsers(browser_list)

            if not success:
                print("没有成功打开任何浏览器，测试终止")
                return

            # 步骤3: 并发执行自动化脚本
            print("\n步骤3: 并发执行自动化脚本")
            await self.run_concurrent_automations()

            # 等待一下，确保所有操作完成
            await asyncio.sleep(2)

        except Exception as e:
            print(f"测试过程中出现错误: {e}")

        finally:
            # 步骤4: 关闭所有浏览器
            print("\n步骤4: 关闭所有浏览器")
            await self.close_all_browsers()

        print("\n" + "=" * 60)
        print("Playwright集成测试完成")
        print("=" * 60)


# 主测试函数
async def main():
    """主测试入口"""
    tester = PlaywrightIntegrationTester()
    await tester.run_full_test()


# 根据你的要求提供的测试方法
async def test_concurrent_automation_with_run_automation():
    """
    测试方法（使用run_automation）：
    1. 调用open_browser方法，打开所有的窗口，解析所有的ws地址
    2. 并发执行同一个自动化脚本（使用run_automation方法）
    3. 自动化脚本执行完成后，调用close_all_browsers关闭所有浏览器
    """
    tester = PlaywrightIntegrationTester()

    # 1. 获取并打开所有浏览器
    browser_list = await tester.get_all_browsers()
    if await tester.open_all_browsers(browser_list):
        # 2. 并发执行自动化脚本（使用run_automation方法）
        await tester.run_concurrent_automations()

        # 3. 关闭所有浏览器
        await tester.close_all_browsers()


# 更复杂的自动化脚本示例
async def advanced_automation_script(util: PlaywrightUtil, browser_id: str, search_keyword: str = "Playwright"):
    """
    更复杂的自动化脚本示例

    Args:
        util: PlaywrightUtil实例
        browser_id: 浏览器ID
        search_keyword: 搜索关键词
    """
    try:
        print(f"开始执行浏览器 {browser_id} 的高级自动化脚本")

        # 访问多个页面
        pages_to_visit = [
            ("https://www.baidu.com", "百度"),
            ("https://www.bing.com", "必应"),
            ("https://duckduckgo.com", "DuckDuckGo")
        ]

        for url, name in pages_to_visit:
            await util.goto(url)
            print(f"浏览器 {browser_id}: 已访问{name}")

            # 根据不同网站使用不同的XPath
            if "baidu.com" in url:
                await util.fill("//input[@id='kw']", search_keyword)
                await util.click("//input[@id='su']")
            elif "bing.com" in url:
                await util.fill("//input[@name='q']", search_keyword)
                await util.click("//input[@type='submit']")
            elif "duckduckgo.com" in url:
                await util.fill("//input[@id='searchbox_input']", search_keyword)
                await util.click("//button[@type='submit']")

            # 等待搜索结果
            await asyncio.sleep(2)  # 简单等待

            # 截图
            screenshot_name = f"browser_{browser_id}_{name}.png"
            await util.screenshot(screenshot_name)
            print(f"浏览器 {browser_id}: {name}截图已保存")

        print(f"浏览器 {browser_id} 的高级自动化脚本执行完成")

    except Exception as e:
        print(f"浏览器 {browser_id} 高级自动化脚本执行失败: {e}")
        raise


async def test_advanced_automation():
    """测试高级自动化脚本"""
    tester = PlaywrightIntegrationTester()

    # 获取并打开所有浏览器
    browser_list = await tester.get_all_browsers()
    if await tester.open_all_browsers(browser_list):
        # 创建高级自动化任务
        tasks = []
        for i, ws_url in enumerate(tester.browser_ws_list):
            browser_id = f"advanced_browser_{i + 1}"
            task = asyncio.create_task(
                run_advanced_automation_with_script(ws_url, browser_id)
            )
            tasks.append(task)

        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)

        # 关闭所有浏览器
        await tester.close_all_browsers()


async def run_advanced_automation_with_script(ws_url: str, browser_id: str):
    """运行高级自动化脚本"""
    util = PlaywrightUtil(ws_endpoint=ws_url, headless=False)
    await util.run_automation(advanced_automation_script, browser_id, search_keyword=f"测试{browser_id}")


if __name__ == "__main__":
    # 运行基础测试
    asyncio.run(main())

    # 或者运行特定测试方法
    # asyncio.run(test_concurrent_automation_with_run_automation())

    # 或者运行高级测试
    # asyncio.run(test_advanced_automation())

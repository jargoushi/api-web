# app/tests/base_test.py

import asyncio
from app.core.logging import setup_logging, log
from app.db.config import init_db, close_db


class TestRunner:
    """
    手动测试运行器，负责初始化环境和执行测试套件。
    """

    def __init__(self):
        setup_logging()

    async def run_tests(self, test_suite_coro):
        """
        运行一个测试套件（一个异步协程）
        """
        log.info("🚀 开始手动执行测试...")

        # 1. 初始化数据库连接
        await init_db()
        log.info("✅ 数据库连接已初始化")

        try:
            await test_suite_coro

            log.info("\n🎉 所有测试执行完毕!")

        except Exception as e:
            log.error(f"\n❌ 测试过程中发生错误: {e}", exc_info=True)

        finally:
            # 3. 关闭数据库连接
            await close_db()
            log.info("✅ 数据库连接已关闭")

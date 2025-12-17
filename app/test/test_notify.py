# 通知模块测试文件
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.util.notify import notifier


async def test_send_ios():
    """测试 iOS Bark 推送"""
    print("测试 iOS Bark 推送")

    # 替换为你的 Bark device_key
    device_key = "tzdbDRLwfqr8ugKCN6LnWF"

    result = await notifier.send_ios(
        device_key=device_key,
        title="测试通知",
        body="这是一条来自 api-web 的测试通知"
    )

    if result.success:
        print(f"✓ 推送成功: {result.message}")
    else:
        print(f"✗ 推送失败: {result.message}")


async def main():
    await test_send_ios()


if __name__ == "__main__":
    asyncio.run(main())

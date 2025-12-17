"""通知工具模块

支持 iOS Bark 推送通知。
官方仓库: https://github.com/Finb/Bark

使用示例:
```python
from app.util.notify import notifier

await notifier.send_ios(
    device_key="你的key",
    title="标题",
    body="内容"
)
```
"""

from app.core.logging import log
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class NotifyResult:
    """通知结果"""
    success: bool
    message: str


class Notifier:
    """通知器"""

    BARK_API_URL = "https://api.day.app/push"

    async def send_ios(
        self,
        device_key: str,
        title: str,
        body: str
    ) -> NotifyResult:
        """发送 iOS Bark 推送通知

        Args:
            device_key: Bark App 中的设备密钥
            title: 通知标题
            body: 通知内容
        """
        if not device_key:
            return NotifyResult(success=False, message="未配置 device_key")

        payload = {"device_key": device_key, "title": title, "body": body}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.BARK_API_URL, json=payload)
                result = resp.json()

                if resp.status_code == 200 and result.get("code") == 200:
                    return NotifyResult(success=True, message="推送成功")
                return NotifyResult(success=False, message=result.get("message", "推送失败"))
        except httpx.TimeoutException:
            log.error("Bark 推送超时")
            return NotifyResult(success=False, message="推送超时")
        except Exception as e:
            log.error(f"Bark 推送异常: {e}")
            return NotifyResult(success=False, message=f"推送异常: {e}")


# 公共实例
notifier = Notifier()

"""账号项目渠道绑定仓储"""

from typing import Optional, List

from app.models.account.account import AccountProjectChannel
from app.repositories.base import BaseRepository


class AccountProjectChannelRepository(BaseRepository[AccountProjectChannel]):
    """账号项目渠道绑定仓储"""

    def __init__(self):
        super().__init__(AccountProjectChannel)

    async def find_by_account(self, account_id: int) -> List[AccountProjectChannel]:
        """获取账号的所有绑定"""
        return await self.find_all(account_id=account_id)

    async def find_binding(
        self, account_id: int, project_code: int, channel_code: int
    ) -> Optional[AccountProjectChannel]:
        """查找指定绑定"""
        return await self.get_or_none(
            account_id=account_id, project_code=project_code, channel_code=channel_code
        )

    async def upsert_binding(
        self, account_id: int, project_code: int, channel_code: int, browser_id: str = None
    ) -> AccountProjectChannel:
        """创建或更新绑定"""
        existing = await self.find_binding(account_id, project_code, channel_code)
        if existing:
            existing.browser_id = browser_id
            await existing.save()
            return existing
        return await self.create(
            account_id=account_id,
            project_code=project_code,
            channel_code=channel_code,
            browser_id=browser_id
        )


# 单例实例
account_project_channel_repository = AccountProjectChannelRepository()

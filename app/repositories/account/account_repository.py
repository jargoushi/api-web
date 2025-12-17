"""账号仓储"""

from datetime import datetime
from typing import Optional, List

from app.models.account.account import Account
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """账号仓储"""

    def __init__(self):
        super().__init__(Account)

    async def find_by_user(self, user_id: int) -> List[Account]:
        """获取用户的所有账号（未删除）"""
        return await self.model.filter(user_id=user_id, deleted_at__isnull=True).all()

    async def find_by_id_and_user(self, account_id: int, user_id: int) -> Optional[Account]:
        """获取用户的指定账号"""
        return await self.get_or_none(id=account_id, user_id=user_id, deleted_at__isnull=True)

    async def soft_delete(self, account: Account) -> Account:
        """软删除账号"""
        account.deleted_at = datetime.now()
        await account.save()
        return account


# 单例实例
account_repository = AccountRepository()

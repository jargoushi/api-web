"""统一配置仓储

合并 UserSettingRepository 和 AccountSettingRepository
"""

from typing import Optional, List, Any

from app.enums.common.setting_owner import SettingOwnerType
from app.models.account.setting import Setting
from app.repositories.base import BaseRepository


class SettingRepository(BaseRepository[Setting]):
    """统一配置仓储"""

    def __init__(self):
        super().__init__(Setting)

    async def find_by_owner_and_key(
        self, owner_type: SettingOwnerType, owner_id: int, setting_key: int
    ) -> Optional[Setting]:
        """获取指定配置"""
        return await self.get_or_none(
            owner_type=owner_type.code, owner_id=owner_id, setting_key=setting_key
        )

    async def find_all_by_owner(
        self, owner_type: SettingOwnerType, owner_id: int
    ) -> List[Setting]:
        """获取所有配置"""
        return await self.find_all(owner_type=owner_type.code, owner_id=owner_id)

    async def upsert(
        self, owner_type: SettingOwnerType, owner_id: int, setting_key: int, setting_value: Any
    ) -> Setting:
        """创建或更新配置"""
        existing = await self.find_by_owner_and_key(owner_type, owner_id, setting_key)
        if existing:
            existing.setting_value = setting_value
            await existing.save()
            return existing
        return await self.create(
            owner_type=owner_type.code,
            owner_id=owner_id,
            setting_key=setting_key,
            setting_value=setting_value
        )

    async def delete_by_owner_and_key(
        self, owner_type: SettingOwnerType, owner_id: int, setting_key: int
    ) -> bool:
        """删除配置"""
        setting = await self.find_by_owner_and_key(owner_type, owner_id, setting_key)
        if setting:
            await setting.delete()
            return True
        return False

    # ========== 便捷方法：用户配置 ==========

    async def find_user_setting(self, user_id: int, setting_key: int) -> Optional[Setting]:
        return await self.find_by_owner_and_key(SettingOwnerType.USER, user_id, setting_key)

    async def find_all_user_settings(self, user_id: int) -> List[Setting]:
        return await self.find_all_by_owner(SettingOwnerType.USER, user_id)

    async def upsert_user_setting(self, user_id: int, setting_key: int, value: Any) -> Setting:
        return await self.upsert(SettingOwnerType.USER, user_id, setting_key, value)

    async def delete_user_setting(self, user_id: int, setting_key: int) -> bool:
        return await self.delete_by_owner_and_key(SettingOwnerType.USER, user_id, setting_key)

    # ========== 便捷方法：账号配置 ==========

    async def find_account_setting(self, account_id: int, setting_key: int) -> Optional[Setting]:
        return await self.find_by_owner_and_key(SettingOwnerType.ACCOUNT, account_id, setting_key)

    async def find_all_account_settings(self, account_id: int) -> List[Setting]:
        return await self.find_all_by_owner(SettingOwnerType.ACCOUNT, account_id)

    async def upsert_account_setting(self, account_id: int, setting_key: int, value: Any) -> Setting:
        return await self.upsert(SettingOwnerType.ACCOUNT, account_id, setting_key, value)

    async def delete_account_setting(self, account_id: int, setting_key: int) -> bool:
        return await self.delete_by_owner_and_key(SettingOwnerType.ACCOUNT, account_id, setting_key)


# 单例实例
setting_repository = SettingRepository()

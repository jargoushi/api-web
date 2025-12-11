"""用户配置仓储"""

from typing import Optional, List

from app.models.account.user_setting import UserSetting
from app.repositories.base import BaseRepository


class UserSettingRepository(BaseRepository[UserSetting]):
    """用户配置仓储类"""

    def __init__(self):
        super().__init__(UserSetting)

    async def find_by_user_and_key(self, user_id: int, setting_key: int) -> Optional[UserSetting]:
        """
        根据用户ID和配置项编码查询配置

        Args:
            user_id: 用户ID
            setting_key: 配置项编码

        Returns:
            配置记录，不存在则返回 None
        """
        return await self.get_or_none(user_id=user_id, setting_key=setting_key)

    async def find_all_by_user(self, user_id: int) -> List[UserSetting]:
        """
        获取用户的所有配置

        Args:
            user_id: 用户ID

        Returns:
            用户的所有配置列表
        """
        return await self.find_all(user_id=user_id)

    async def upsert(self, user_id: int, setting_key: int, setting_value) -> UserSetting:
        """
        更新或创建配置

        Args:
            user_id: 用户ID
            setting_key: 配置项编码
            setting_value: 配置值

        Returns:
            更新后的配置记录
        """
        existing = await self.find_by_user_and_key(user_id, setting_key)
        if existing:
            existing.setting_value = setting_value
            await existing.save()
            return existing
        else:
            return await self.create(
                user_id=user_id,
                setting_key=setting_key,
                setting_value=setting_value
            )

    async def delete_by_user_and_key(self, user_id: int, setting_key: int) -> bool:
        """
        删除用户的某个配置（重置为默认值）

        Args:
            user_id: 用户ID
            setting_key: 配置项编码

        Returns:
            是否删除成功
        """
        setting = await self.find_by_user_and_key(user_id, setting_key)
        if setting:
            await setting.delete()
            return True
        return False

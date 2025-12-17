"""用户配置服务（重构版）

统一处理用户配置和账号配置，通过 SettingOwnerType 区分
"""

from typing import Any, Dict

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.enums.common.setting_owner import SettingOwnerType
from app.enums.settings import SettingGroupEnum
from app.repositories.account.setting_repository import setting_repository
from app.schemas.account.setting import (
    SettingResponse,
    SettingGroupResponse,
    AllSettingsResponse,
    SettingUpdateRequest
)


class SettingService:
    """配置服务类"""

    # ========== 用户配置 ==========

    async def get_all_settings(self, user_id: int) -> AllSettingsResponse:
        """获取用户所有配置（合并默认值）"""
        log.info(f"用户{user_id}获取所有配置")
        return await self._get_all_settings_by_owner(SettingOwnerType.USER, user_id)

    async def get_setting(self, user_id: int, setting_key: int) -> SettingResponse:
        """获取单个配置"""
        log.info(f"用户{user_id}获取配置项{setting_key}")
        return await self._get_setting_by_owner(SettingOwnerType.USER, user_id, setting_key)

    async def update_setting(self, user_id: int, request: SettingUpdateRequest) -> SettingResponse:
        """更新配置"""
        log.info(f"用户{user_id}更新配置项{request.setting_key}，值：{request.setting_value}")
        result = await self._update_setting_by_owner(SettingOwnerType.USER, user_id, request)
        log.info(f"配置项{request.setting_key}更新成功")
        return result

    async def reset_setting(self, user_id: int, setting_key: int) -> SettingResponse:
        """重置配置为默认值"""
        log.info(f"用户{user_id}重置配置项{setting_key}")
        result = await self._reset_setting_by_owner(SettingOwnerType.USER, user_id, setting_key)
        log.info(f"配置项{setting_key}已重置为默认值")
        return result

    async def get_settings_by_group(self, user_id: int, group_code: int) -> SettingGroupResponse:
        """按分组获取配置"""
        log.info(f"用户{user_id}获取分组{group_code}的配置")
        return await self._get_settings_by_group_and_owner(SettingOwnerType.USER, user_id, group_code)

    # ========== 账号配置 ==========

    async def get_account_all_settings(self, account_id: int, user_id: int) -> AllSettingsResponse:
        """获取账号的所有配置（含继承）

        配置优先级：账号配置 > 用户配置 > 默认值
        """
        log.info(f"获取账号{account_id}的配置")

        # 获取账号配置
        account_settings = await setting_repository.find_all_account_settings(account_id)
        account_settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in account_settings
        }

        # 获取用户配置
        user_settings = await setting_repository.find_all_user_settings(user_id)
        user_settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in user_settings
        }

        # 按分组组织
        groups = []
        for group in SettingGroupEnum:
            settings = []
            for setting in group.get_settings():
                # 优先级：账号 > 用户 > 默认
                if setting.code in account_settings_map:
                    value = account_settings_map[setting.code]
                    source = "account"
                elif setting.code in user_settings_map:
                    value = user_settings_map[setting.code]
                    source = "user"
                else:
                    value = setting.default
                    source = "default"

                settings.append(SettingResponse(
                    setting_key=setting.code,
                    setting_key_name=setting.desc,
                    setting_value=value,
                    group=group.desc,
                    value_type=setting.value_type,
                    is_default=(source == "default")
                ))

            groups.append(SettingGroupResponse(
                group=group.desc,
                group_code=group.code,
                settings=settings
            ))

        return AllSettingsResponse(groups=groups)

    async def update_account_setting(self, account_id: int, request: SettingUpdateRequest) -> SettingResponse:
        """更新账号配置"""
        log.info(f"更新账号{account_id}的配置项{request.setting_key}")
        return await self._update_setting_by_owner(SettingOwnerType.ACCOUNT, account_id, request)

    async def reset_account_setting(self, account_id: int, setting_key: int) -> SettingResponse:
        """重置账号配置（恢复继承用户配置）"""
        log.info(f"重置账号{account_id}的配置项{setting_key}")
        return await self._reset_setting_by_owner(SettingOwnerType.ACCOUNT, account_id, setting_key)

    async def get_effective_setting(self, account_id: int, user_id: int, setting_key: int) -> Any:
        """获取有效配置值（账号 > 用户 > 默认）"""
        group, setting = SettingGroupEnum.find_setting_by_code(setting_key)

        # 先查账号配置
        account_setting = await setting_repository.find_account_setting(account_id, setting_key)
        if account_setting:
            return account_setting.setting_value

        # 再查用户配置
        user_setting = await setting_repository.find_user_setting(user_id, setting_key)
        if user_setting:
            return user_setting.setting_value

        # 返回默认值
        return setting.default

    # ========== 私有方法 ==========

    async def _get_all_settings_by_owner(
        self, owner_type: SettingOwnerType, owner_id: int
    ) -> AllSettingsResponse:
        """获取所有配置（通用）"""
        if owner_type == SettingOwnerType.USER:
            settings_list = await setting_repository.find_all_user_settings(owner_id)
        else:
            settings_list = await setting_repository.find_all_account_settings(owner_id)

        settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in settings_list
        }

        groups = []
        for group in SettingGroupEnum:
            settings = []
            for setting in group.get_settings():
                if setting.code in settings_map:
                    value = settings_map[setting.code]
                    is_default = False
                else:
                    value = setting.default
                    is_default = True

                settings.append(SettingResponse(
                    setting_key=setting.code,
                    setting_key_name=setting.desc,
                    setting_value=value,
                    group=group.desc,
                    value_type=setting.value_type,
                    is_default=is_default
                ))

            groups.append(SettingGroupResponse(
                group=group.desc,
                group_code=group.code,
                settings=settings
            ))

        return AllSettingsResponse(groups=groups)

    async def _get_setting_by_owner(
        self, owner_type: SettingOwnerType, owner_id: int, setting_key: int
    ) -> SettingResponse:
        """获取单个配置（通用）"""
        group, setting = SettingGroupEnum.find_setting_by_code(setting_key)

        saved = await setting_repository.find_by_owner_and_key(owner_type, owner_id, setting_key)

        if saved:
            value = saved.setting_value
            is_default = False
        else:
            value = setting.default
            is_default = True

        return SettingResponse(
            setting_key=setting.code,
            setting_key_name=setting.desc,
            setting_value=value,
            group=group.desc,
            value_type=setting.value_type,
            is_default=is_default
        )

    async def _update_setting_by_owner(
        self, owner_type: SettingOwnerType, owner_id: int, request: SettingUpdateRequest
    ) -> SettingResponse:
        """更新配置（通用）"""
        group, setting = SettingGroupEnum.find_setting_by_code(request.setting_key)
        self._validate_value_type(request.setting_value, setting.value_type)

        await setting_repository.upsert(owner_type, owner_id, request.setting_key, request.setting_value)

        return SettingResponse(
            setting_key=setting.code,
            setting_key_name=setting.desc,
            setting_value=request.setting_value,
            group=group.desc,
            value_type=setting.value_type,
            is_default=False
        )

    async def _reset_setting_by_owner(
        self, owner_type: SettingOwnerType, owner_id: int, setting_key: int
    ) -> SettingResponse:
        """重置配置（通用）"""
        group, setting = SettingGroupEnum.find_setting_by_code(setting_key)

        await setting_repository.delete_by_owner_and_key(owner_type, owner_id, setting_key)

        return SettingResponse(
            setting_key=setting.code,
            setting_key_name=setting.desc,
            setting_value=setting.default,
            group=group.desc,
            value_type=setting.value_type,
            is_default=True
        )

    async def _get_settings_by_group_and_owner(
        self, owner_type: SettingOwnerType, owner_id: int, group_code: int
    ) -> SettingGroupResponse:
        """按分组获取配置（通用）"""
        group = SettingGroupEnum.from_code(group_code)

        if owner_type == SettingOwnerType.USER:
            settings_list = await setting_repository.find_all_user_settings(owner_id)
        else:
            settings_list = await setting_repository.find_all_account_settings(owner_id)

        settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in settings_list
        }

        settings = []
        for setting in group.get_settings():
            if setting.code in settings_map:
                value = settings_map[setting.code]
                is_default = False
            else:
                value = setting.default
                is_default = True

            settings.append(SettingResponse(
                setting_key=setting.code,
                setting_key_name=setting.desc,
                setting_value=value,
                group=group.desc,
                value_type=setting.value_type,
                is_default=is_default
            ))

        return SettingGroupResponse(group=group.desc, group_code=group.code, settings=settings)

    def _validate_value_type(self, value: Any, expected_type: str) -> None:
        """验证值类型"""
        type_map = {
            "bool": bool,
            "str": str,
            "int": int,
            "float": (int, float),
            "json": (dict, list)
        }

        expected = type_map.get(expected_type)
        if expected and not isinstance(value, expected):
            raise BusinessException(
                message=f"配置值类型错误，期望 {expected_type}，实际 {type(value).__name__}"
            )


# 创建服务实例
setting_service = SettingService()

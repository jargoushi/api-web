"""用户配置服务"""

from typing import Any, List, Dict

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.enums.common.setting_key import SettingGroupEnum
from app.repositories.account.user_setting_repository import UserSettingRepository
from app.schemas.account.setting import (
    SettingResponse,
    SettingGroupResponse,
    AllSettingsResponse,
    SettingUpdateRequest
)


class SettingService:
    """用户配置服务类"""

    def __init__(self, repository: UserSettingRepository = UserSettingRepository()):
        self.repository = repository

    async def get_all_settings(self, user_id: int) -> AllSettingsResponse:
        """获取用户所有配置（合并默认值）"""
        log.info(f"用户{user_id}获取所有配置")

        # 获取用户已保存的配置
        user_settings = await self.repository.find_all_by_user(user_id)
        user_settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in user_settings
        }

        # 按分组组织配置
        groups = []
        for group in SettingGroupEnum:
            settings = []
            for setting in group.get_settings():
                if setting.code in user_settings_map:
                    value = user_settings_map[setting.code]
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

    async def get_setting(self, user_id: int, setting_key: int) -> SettingResponse:
        """获取单个配置"""
        log.info(f"用户{user_id}获取配置项{setting_key}")

        try:
            group, setting = SettingGroupEnum.find_setting_by_code(setting_key)
        except ValueError:
            raise BusinessException(message=f"不支持的配置项编码: {setting_key}")

        user_setting = await self.repository.find_by_user_and_key(user_id, setting_key)

        if user_setting:
            value = user_setting.setting_value
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

    async def update_setting(self, user_id: int, request: SettingUpdateRequest) -> SettingResponse:
        """更新配置"""
        log.info(f"用户{user_id}更新配置项{request.setting_key}，值：{request.setting_value}")

        try:
            group, setting = SettingGroupEnum.find_setting_by_code(request.setting_key)
        except ValueError:
            raise BusinessException(message=f"不支持的配置项编码: {request.setting_key}")

        # 验证值类型
        self._validate_value_type(request.setting_value, setting.value_type)

        # 保存配置
        await self.repository.upsert(user_id, request.setting_key, request.setting_value)

        log.info(f"配置项{request.setting_key}更新成功")

        return SettingResponse(
            setting_key=setting.code,
            setting_key_name=setting.desc,
            setting_value=request.setting_value,
            group=group.desc,
            value_type=setting.value_type,
            is_default=False
        )

    async def reset_setting(self, user_id: int, setting_key: int) -> SettingResponse:
        """重置配置为默认值"""
        log.info(f"用户{user_id}重置配置项{setting_key}")

        try:
            group, setting = SettingGroupEnum.find_setting_by_code(setting_key)
        except ValueError:
            raise BusinessException(message=f"不支持的配置项编码: {setting_key}")

        await self.repository.delete_by_user_and_key(user_id, setting_key)

        log.info(f"配置项{setting_key}已重置为默认值")

        return SettingResponse(
            setting_key=setting.code,
            setting_key_name=setting.desc,
            setting_value=setting.default,
            group=group.desc,
            value_type=setting.value_type,
            is_default=True
        )

    async def get_settings_by_group(self, user_id: int, group_code: int) -> SettingGroupResponse:
        """按分组获取配置"""
        log.info(f"用户{user_id}获取分组{group_code}的配置")

        try:
            group = SettingGroupEnum.from_code(group_code)
        except ValueError:
            raise BusinessException(message=f"不支持的配置分组: {group_code}")

        user_settings = await self.repository.find_all_by_user(user_id)
        user_settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in user_settings
        }

        settings = []
        for setting in group.get_settings():
            if setting.code in user_settings_map:
                value = user_settings_map[setting.code]
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

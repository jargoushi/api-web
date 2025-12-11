"""用户配置服务"""

from typing import Any, List, Dict

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.enums.common.setting_key import SettingKeyEnum
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
        """
        初始化服务

        Args:
            repository: 配置仓储实例
        """
        self.repository = repository

    async def get_all_settings(self, user_id: int) -> AllSettingsResponse:
        """
        获取用户所有配置（合并默认值）

        Args:
            user_id: 用户ID

        Returns:
            按分组组织的所有配置
        """
        log.info(f"用户{user_id}获取所有配置")

        # 获取用户已保存的配置
        user_settings = await self.repository.find_all_by_user(user_id)
        user_settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in user_settings
        }

        # 按分组组织配置
        groups_map: Dict[str, List[SettingResponse]] = {}

        for setting_enum in SettingKeyEnum:
            # 判断是否使用用户设置还是默认值
            if setting_enum.code in user_settings_map:
                value = user_settings_map[setting_enum.code]
                is_default = False
            else:
                value = setting_enum.default
                is_default = True

            setting_response = SettingResponse(
                setting_key=setting_enum.code,
                setting_key_name=setting_enum.desc,
                setting_value=value,
                group=setting_enum.group,
                value_type=setting_enum.value_type,
                is_default=is_default
            )

            if setting_enum.group not in groups_map:
                groups_map[setting_enum.group] = []
            groups_map[setting_enum.group].append(setting_response)

        # 转换为响应格式
        groups = [
            SettingGroupResponse(group=group, settings=settings)
            for group, settings in groups_map.items()
        ]

        return AllSettingsResponse(groups=groups)

    async def get_setting(self, user_id: int, setting_key: int) -> SettingResponse:
        """
        获取单个配置

        Args:
            user_id: 用户ID
            setting_key: 配置项编码

        Returns:
            配置响应

        Raises:
            BusinessException: 配置项不存在
        """
        log.info(f"用户{user_id}获取配置项{setting_key}")

        # 验证配置项编码
        try:
            setting_enum = SettingKeyEnum.from_code(setting_key)
        except ValueError:
            raise BusinessException(message=f"不支持的配置项编码: {setting_key}")

        # 查询用户配置
        user_setting = await self.repository.find_by_user_and_key(user_id, setting_key)

        if user_setting:
            value = user_setting.setting_value
            is_default = False
        else:
            value = setting_enum.default
            is_default = True

        return SettingResponse(
            setting_key=setting_enum.code,
            setting_key_name=setting_enum.desc,
            setting_value=value,
            group=setting_enum.group,
            value_type=setting_enum.value_type,
            is_default=is_default
        )

    async def update_setting(self, user_id: int, request: SettingUpdateRequest) -> SettingResponse:
        """
        更新配置

        Args:
            user_id: 用户ID
            request: 更新请求

        Returns:
            更新后的配置响应

        Raises:
            BusinessException: 配置项不存在或值类型不匹配
        """
        log.info(f"用户{user_id}更新配置项{request.setting_key}，值：{request.setting_value}")

        # 验证配置项编码
        try:
            setting_enum = SettingKeyEnum.from_code(request.setting_key)
        except ValueError:
            raise BusinessException(message=f"不支持的配置项编码: {request.setting_key}")

        # 验证值类型
        self._validate_value_type(request.setting_value, setting_enum.value_type)

        # 保存配置
        await self.repository.upsert(user_id, request.setting_key, request.setting_value)

        log.info(f"配置项{request.setting_key}更新成功")

        return SettingResponse(
            setting_key=setting_enum.code,
            setting_key_name=setting_enum.desc,
            setting_value=request.setting_value,
            group=setting_enum.group,
            value_type=setting_enum.value_type,
            is_default=False
        )

    async def reset_setting(self, user_id: int, setting_key: int) -> SettingResponse:
        """
        重置配置为默认值

        Args:
            user_id: 用户ID
            setting_key: 配置项编码

        Returns:
            重置后的配置响应（使用默认值）

        Raises:
            BusinessException: 配置项不存在
        """
        log.info(f"用户{user_id}重置配置项{setting_key}")

        # 验证配置项编码
        try:
            setting_enum = SettingKeyEnum.from_code(setting_key)
        except ValueError:
            raise BusinessException(message=f"不支持的配置项编码: {setting_key}")

        # 删除用户配置（重置为默认值）
        await self.repository.delete_by_user_and_key(user_id, setting_key)

        log.info(f"配置项{setting_key}已重置为默认值")

        return SettingResponse(
            setting_key=setting_enum.code,
            setting_key_name=setting_enum.desc,
            setting_value=setting_enum.default,
            group=setting_enum.group,
            value_type=setting_enum.value_type,
            is_default=True
        )

    async def get_settings_by_group(self, user_id: int, group: str) -> SettingGroupResponse:
        """
        按分组获取配置

        Args:
            user_id: 用户ID
            group: 分组名称

        Returns:
            该分组的配置响应

        Raises:
            BusinessException: 分组不存在
        """
        log.info(f"用户{user_id}获取分组{group}的配置")

        # 验证分组
        setting_enums = SettingKeyEnum.get_by_group(group)
        if not setting_enums:
            raise BusinessException(message=f"不支持的配置分组: {group}")

        # 获取用户已保存的配置
        user_settings = await self.repository.find_all_by_user(user_id)
        user_settings_map: Dict[int, Any] = {
            s.setting_key: s.setting_value for s in user_settings
        }

        # 构建响应
        settings = []
        for setting_enum in setting_enums:
            if setting_enum.code in user_settings_map:
                value = user_settings_map[setting_enum.code]
                is_default = False
            else:
                value = setting_enum.default
                is_default = True

            settings.append(SettingResponse(
                setting_key=setting_enum.code,
                setting_key_name=setting_enum.desc,
                setting_value=value,
                group=setting_enum.group,
                value_type=setting_enum.value_type,
                is_default=is_default
            ))

        return SettingGroupResponse(group=group, settings=settings)

    def _validate_value_type(self, value: Any, expected_type: str) -> None:
        """
        验证值类型

        Args:
            value: 配置值
            expected_type: 期望的类型

        Raises:
            BusinessException: 类型不匹配
        """
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

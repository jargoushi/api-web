"""用户配置枚举模块

设计说明：
1. SettingGroupEnum 定义所有配置分组，每个分组直接引用其配置项枚举类
2. 每个分组有独立的配置项枚举类
3. 新增配置时，历史用户自动使用默认值（无需迁移）
"""

from enum import Enum
from typing import Any, Type


class SettingValueType(str, Enum):
    """配置值类型"""
    BOOL = "bool"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    JSON = "json"


class BaseSetting:
    """配置项基类"""

    def __init__(self, code: int, desc: str, default: Any, value_type: SettingValueType):
        self.code = code
        self.desc = desc
        self.default = default
        self.value_type = value_type.value


class GeneralSettingEnum(Enum):
    """通用设置"""
    AUTO_DOWNLOAD = BaseSetting(101, "自动下载", True, SettingValueType.BOOL)
    DOWNLOAD_PATH = BaseSetting(102, "下载目录", "./downloads", SettingValueType.STR)

    @property
    def code(self) -> int:
        return self.value.code

    @property
    def desc(self) -> str:
        return self.value.desc

    @property
    def default(self) -> Any:
        return self.value.default

    @property
    def value_type(self) -> str:
        return self.value.value_type


class NotificationSettingEnum(Enum):
    """通知设置"""
    NOTIFY_ON_SUCCESS = BaseSetting(201, "成功时通知", True, SettingValueType.BOOL)
    NOTIFY_ON_FAILURE = BaseSetting(202, "失败时通知", True, SettingValueType.BOOL)

    @property
    def code(self) -> int:
        return self.value.code

    @property
    def desc(self) -> str:
        return self.value.desc

    @property
    def default(self) -> Any:
        return self.value.default

    @property
    def value_type(self) -> str:
        return self.value.value_type


class AdvancedSettingEnum(Enum):
    """高级设置"""
    MAX_CONCURRENT_TASKS = BaseSetting(301, "最大并发数", 3, SettingValueType.INT)
    TASK_RETRY_COUNT = BaseSetting(302, "任务重试次数", 3, SettingValueType.INT)

    @property
    def code(self) -> int:
        return self.value.code

    @property
    def desc(self) -> str:
        return self.value.desc

    @property
    def default(self) -> Any:
        return self.value.default

    @property
    def value_type(self) -> str:
        return self.value.value_type


class SettingGroupEnum(Enum):
    """
    配置分组枚举

    每个分组直接关联其配置项枚举类
    """
    GENERAL = (1, "通用设置", GeneralSettingEnum)
    NOTIFICATION = (2, "通知设置", NotificationSettingEnum)
    ADVANCED = (3, "高级设置", AdvancedSettingEnum)

    def __init__(self, code: int, desc: str, setting_enum: Type[Enum]):
        self.code = code
        self.desc = desc
        self.setting_enum = setting_enum

    def get_settings(self) -> list:
        """获取该分组下的所有配置项"""
        return list(self.setting_enum)

    @classmethod
    def from_code(cls, code: int) -> "SettingGroupEnum":
        """根据编码获取分组"""
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的分组编码: {code}")

    @classmethod
    def get_all_settings(cls) -> list:
        """获取所有配置项"""
        all_settings = []
        for group in cls:
            all_settings.extend(group.get_settings())
        return all_settings

    @classmethod
    def find_setting_by_code(cls, code: int) -> tuple:
        """
        根据配置项编码查找

        Returns:
            (分组枚举, 配置项枚举) 或抛出 ValueError
        """
        for group in cls:
            for setting in group.get_settings():
                if setting.code == code:
                    return (group, setting)
        raise ValueError(f"不支持的配置项编码: {code}")

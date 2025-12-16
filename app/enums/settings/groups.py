"""配置分组枚举"""

from enum import Enum
from typing import Type

from app.enums.settings.general import GeneralSettingEnum
from app.enums.settings.notification import NotificationSettingEnum
from app.enums.settings.advanced import AdvancedSettingEnum
from app.enums.settings.download import DownloadSettingEnum


class SettingGroupEnum(Enum):
    """
    配置分组枚举

    每个分组直接关联其配置项枚举类
    """
    GENERAL = (1, "通用设置", GeneralSettingEnum)
    NOTIFICATION = (2, "通知设置", NotificationSettingEnum)
    ADVANCED = (3, "高级设置", AdvancedSettingEnum)
    DOWNLOAD = (4, "下载设置", DownloadSettingEnum)

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

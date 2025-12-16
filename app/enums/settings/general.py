"""通用设置"""

from app.enums.settings.base import BaseSetting, BaseSettingEnum, SettingValueType


class GeneralSettingEnum(BaseSettingEnum):
    """通用设置"""
    AUTO_DOWNLOAD = BaseSetting(101, "自动下载", True, SettingValueType.BOOL)
    DOWNLOAD_PATH = BaseSetting(102, "下载目录", "./downloads", SettingValueType.STR)

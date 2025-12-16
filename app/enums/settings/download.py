"""下载设置"""

from app.enums.settings.base import BaseSetting, BaseSettingEnum, SettingValueType


class DownloadSettingEnum(BaseSettingEnum):
    """下载设置"""
    DOWNLOAD_PATH = BaseSetting(401, "下载目录", "./downloads", SettingValueType.STR)
    PROXY_URL = BaseSetting(402, "代理地址", "", SettingValueType.STR)

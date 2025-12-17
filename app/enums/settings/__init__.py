"""配置枚举包

配置分组结构：
- base.py: 基础类型定义 (SettingValueType, BaseSetting, BaseSettingEnum)
- general.py: 通用设置
- notification.py: 通知设置
- advanced.py: 高级设置
- download.py: 下载设置
- groups.py: 配置分组枚举 (SettingGroupEnum)
"""

from app.enums.settings.base import SettingValueType, BaseSetting, BaseSettingEnum
from app.enums.settings.general import GeneralSettingEnum
from app.enums.settings.notification import NotificationSettingEnum
from app.enums.settings.advanced import AdvancedSettingEnum
from app.enums.settings.download import DownloadSettingEnum
from app.enums.settings.groups import SettingGroupEnum

__all__ = [
    "SettingValueType",
    "BaseSetting",
    "BaseSettingEnum",
    "GeneralSettingEnum",
    "NotificationSettingEnum",
    "AdvancedSettingEnum",
    "DownloadSettingEnum",
    "SettingGroupEnum",
]

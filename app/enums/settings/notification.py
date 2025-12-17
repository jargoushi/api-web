"""通知设置"""

from app.enums.settings.base import BaseSetting, BaseSettingEnum, SettingValueType


class NotificationSettingEnum(BaseSettingEnum):
    """通知设置"""
    NOTIFY_ON_SUCCESS = BaseSetting(201, "成功时通知", True, SettingValueType.BOOL)
    NOTIFY_ON_FAILURE = BaseSetting(202, "失败时通知", True, SettingValueType.BOOL)

    # iOS Bark 推送配置
    IOS_BARK_DEVICE_KEY = BaseSetting(210, "iOS Bark 设备密钥", "", SettingValueType.STR)

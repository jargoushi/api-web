"""高级设置"""

from app.enums.settings.base import BaseSetting, BaseSettingEnum, SettingValueType


class AdvancedSettingEnum(BaseSettingEnum):
    """高级设置"""
    MAX_CONCURRENT_TASKS = BaseSetting(301, "最大并发数", 3, SettingValueType.INT)
    TASK_RETRY_COUNT = BaseSetting(302, "任务重试次数", 3, SettingValueType.INT)

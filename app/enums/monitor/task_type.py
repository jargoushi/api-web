from app.enums.base import BaseCodeEnum


class TaskTypeEnum(BaseCodeEnum):
    """任务类型枚举"""
    DAILY_COLLECTION = (1, "每日数据采集")
    MANUAL_REFRESH = (2, "手动刷新")

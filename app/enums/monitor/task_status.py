from app.enums.base import BaseCodeEnum


class TaskStatusEnum(BaseCodeEnum):
    """任务状态枚举"""
    PENDING = (0, "待执行")
    IN_PROGRESS = (1, "进行中")
    SUCCESS = (2, "成功")
    FAILED = (3, "失败")

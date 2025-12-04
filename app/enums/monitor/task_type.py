from enum import Enum


class TaskTypeEnum(Enum):
    """任务类型枚举"""
    DAILY_COLLECTION = (1, "每日数据采集")
    MANUAL_REFRESH = (2, "手动刷新")

    def __new__(cls, code: int, desc: str):
        obj = object.__new__(cls)
        obj.code = code
        obj.desc = desc
        return obj

    @classmethod
    def from_code(cls, code: int) -> "TaskTypeEnum":
        """根据任务类型码获取枚举成员（用于从数据库字段转换）"""
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的任务类型: {code}")

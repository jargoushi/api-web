from enum import Enum


class TaskStatusEnum(Enum):
    """任务状态枚举"""
    PENDING = (0, "待执行")
    IN_PROGRESS = (1, "进行中")
    SUCCESS = (2, "成功")
    FAILED = (3, "失败")

    def __new__(cls, code: int, desc: str):
        obj = object.__new__(cls)
        obj.code = code
        obj.desc = desc
        return obj

    @classmethod
    def from_code(cls, code: int) -> "TaskStatusEnum":
        """根据任务状态码获取枚举成员（用于从数据库字段转换）"""
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的任务状态: {code}")

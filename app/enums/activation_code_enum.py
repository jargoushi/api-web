from datetime import datetime, timedelta
from enum import Enum


class ActivationTypeEnum(Enum):
    """激活码类型枚举"""
    DAY = (0, "日卡", 1)  # (类型码, 描述, 有效天数)
    MONTH = (1, "月卡", 30)
    YEAR = (2, "年卡", 365)
    PERMANENT = (3, "永久卡", 365 * 100)  # 100年作为永久

    def __init__(self, code: int, desc: str, valid_days: int):
        self.code = code  # 类型码
        self.desc = desc  # 类型描述
        self.valid_days = valid_days  # 有效天数

    @classmethod
    def from_code(cls, code: int) -> "ActivationTypeEnum":
        """根据类型码获取枚举成员（用于从数据库字段转换）"""
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的激活码类型: {code}")

    def get_expire_time_from(self, start_time: datetime = None, add_grace_hours: int = 0) -> datetime:
        """从指定时间开始计算过期时间，可增加宽裕时间"""
        if start_time is None:
            start_time = datetime.now()
        return start_time + timedelta(days=self.valid_days, hours=add_grace_hours)


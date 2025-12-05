from datetime import timedelta

from app.enums.base import BaseCodeEnum
from app.util.time_util import get_utc_now


class ActivationTypeEnum(BaseCodeEnum):
    """激活码类型枚举"""
    DAY = (0, "日卡", 1)  # (类型码, 描述, 有效天数)
    MONTH = (1, "月卡", 30)
    YEAR = (2, "年卡", 365)
    PERMANENT = (3, "永久卡", 365 * 100)  # 100年作为永久

    def __new__(cls, code: int, desc: str, valid_days: int):
        """
        创建激活码类型枚举实例

        Args:
            code: 类型编码
            desc: 类型描述
            valid_days: 有效天数
        """
        obj = object.__new__(cls)
        obj.code = code
        obj.desc = desc
        obj.valid_days = valid_days
        return obj

    def get_expire_time_from(self, start_time=None, add_grace_hours: int = 0):
        """
        从指定时间开始计算过期时间

        Args:
            start_time: 开始时间（默认为当前UTC时间）
            add_grace_hours: 额外增加的宽限小时数

        Returns:
            过期时间
        """
        if start_time is None:
            start_time = get_utc_now()
        return start_time + timedelta(days=self.valid_days, hours=add_grace_hours)

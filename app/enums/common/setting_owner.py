"""配置所属类型枚举"""

from enum import IntEnum


class SettingOwnerType(IntEnum):
    """配置所属类型"""
    USER = 1     # 用户
    ACCOUNT = 2  # 账号

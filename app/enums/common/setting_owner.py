"""配置所属类型枚举"""

from app.enums.base import BaseCodeEnum


class SettingOwnerType(BaseCodeEnum):
    """配置所属类型"""
    USER = (1, "用户")
    ACCOUNT = (2, "账号")

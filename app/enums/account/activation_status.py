from app.enums.base import BaseCodeEnum


class ActivationCodeStatusEnum(BaseCodeEnum):
    """激活码状态枚举"""
    UNUSED = (0, "未使用")
    DISTRIBUTED = (1, "已分发")
    ACTIVATED = (2, "已激活")
    INVALID = (3, "作废")

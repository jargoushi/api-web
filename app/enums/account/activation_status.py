from enum import Enum


class ActivationCodeStatusEnum(Enum):
    """激活码状态枚举"""
    UNUSED = (0, "未使用")
    DISTRIBUTED = (1, "已分发")
    ACTIVATED = (2, "已激活")
    INVALID = (3, "作废")

    def __new__(cls, code: int, desc: str):

        obj = object.__new__(cls)
        obj.code = code
        obj.desc = desc
        return obj

    @classmethod
    def from_code(cls, code: int) -> "ActivationCodeStatusEnum":
        """根据状态码获取枚举成员（用于从数据库字段转换）"""
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的激活码状态: {code}")

from enum import Enum
from typing import Dict, List, Any


class BaseCodeEnum(Enum):
    """
    基础枚举类

    所有业务枚举的基类，提供统一的 code 和 desc 字段支持
    """

    def __new__(cls, code: int, desc: str, *args):
        """
        创建枚举实例

        Args:
            code: 枚举编码
            desc: 枚举描述
            *args: 其他自定义字段
        """
        obj = object.__new__(cls)
        obj.code = code
        obj.desc = desc
        return obj

    @classmethod
    def from_code(cls, code: int):
        """
        根据编码获取枚举成员

        Args:
            code: 枚举编码

        Returns:
            枚举成员

        Raises:
            ValueError: 编码不存在
        """
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的{cls.__name__}编码: {code}")

    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典

        Returns:
            包含 code 和 desc 的字典
        """
        return {
            "code": self.code,
            "desc": self.desc
        }

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        """
        获取所有枚举成员列表

        Returns:
            所有枚举成员的字典列表
        """
        return [member.to_dict() for member in cls]

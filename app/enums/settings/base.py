"""配置枚举基础类型"""

from enum import Enum
from typing import Any


class SettingValueType(str, Enum):
    """配置值类型"""
    BOOL = "bool"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    JSON = "json"


class BaseSetting:
    """配置项基类"""

    def __init__(self, code: int, desc: str, default: Any, value_type: SettingValueType):
        self.code = code
        self.desc = desc
        self.default = default
        self.value_type = value_type.value


class BaseSettingEnum(Enum):
    """
    配置项枚举基类

    所有配置枚举都应继承此类，自动获得 code/desc/default/value_type 属性。
    """

    @property
    def code(self) -> int:
        return self.value.code

    @property
    def desc(self) -> str:
        return self.value.desc

    @property
    def default(self) -> Any:
        return self.value.default

    @property
    def value_type(self) -> str:
        return self.value.value_type

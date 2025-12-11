"""用户配置项枚举"""

from typing import Any
from enum import Enum


class SettingKeyEnum(Enum):
    """
    用户配置项枚举

    每个配置项包含：code(编码), desc(描述), group(分组), default(默认值), value_type(值类型)
    """

    # ============ 通用设置 (general) ============
    AUTO_DOWNLOAD = (1, "自动下载", "general", True, "bool")
    DOWNLOAD_PATH = (2, "下载目录", "general", "./downloads", "str")

    # ============ 通知设置 (notification) ============
    NOTIFY_ON_SUCCESS = (10, "成功时通知", "notification", True, "bool")
    NOTIFY_ON_FAILURE = (11, "失败时通知", "notification", True, "bool")

    # ============ 高级设置 (advanced) ============
    MAX_CONCURRENT_TASKS = (20, "最大并发数", "advanced", 3, "int")
    TASK_RETRY_COUNT = (21, "任务重试次数", "advanced", 3, "int")

    def __new__(cls, code: int, desc: str, group: str, default: Any, value_type: str):
        """
        创建枚举实例

        Args:
            code: 配置项编码
            desc: 配置项描述
            group: 所属分组
            default: 默认值
            value_type: 值类型 (bool/str/int/float/json)
        """
        obj = object.__new__(cls)
        obj._value_ = code
        obj.code = code
        obj.desc = desc
        obj.group = group
        obj.default = default
        obj.value_type = value_type
        return obj

    @classmethod
    def from_code(cls, code: int) -> "SettingKeyEnum":
        """
        根据编码获取枚举成员

        Args:
            code: 配置项编码

        Returns:
            枚举成员

        Raises:
            ValueError: 编码不存在
        """
        for member in cls:
            if member.code == code:
                return member
        raise ValueError(f"不支持的配置项编码: {code}")

    @classmethod
    def get_by_group(cls, group: str) -> list["SettingKeyEnum"]:
        """
        根据分组获取配置项列表

        Args:
            group: 分组名称

        Returns:
            该分组下的所有配置项
        """
        return [member for member in cls if member.group == group]

    @classmethod
    def get_all_groups(cls) -> list[str]:
        """
        获取所有分组名称

        Returns:
            分组名称列表（去重）
        """
        return list(set(member.group for member in cls))

    def to_dict(self) -> dict:
        """
        序列化为字典

        Returns:
            包含配置项完整信息的字典
        """
        return {
            "code": self.code,
            "desc": self.desc,
            "group": self.group,
            "default": self.default,
            "value_type": self.value_type
        }

    @classmethod
    def get_all(cls) -> list[dict]:
        """
        获取所有配置项列表

        Returns:
            所有配置项的字典列表
        """
        return [member.to_dict() for member in cls]

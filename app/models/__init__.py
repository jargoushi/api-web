"""
数据模型模块
自动导入所有子模块的 Model，供 Tortoise ORM 使用
"""

# 导入基础模型
from .base import BaseModel

# 导入 account 模块的所有 Model
from .account.user import User
from .account.user_session import UserSession
from .account.activation_code import ActivationCode
from .account.user_setting import UserSetting

# 导入 monitor 模块的所有 Model
from .monitor.monitor_config import MonitorConfig
from .monitor.monitor_daily_stats import MonitorDailyStats
from .monitor.task import Task

__all__ = [
    # 基础模型
    "BaseModel",
    # account 模块
    "User",
    "UserSession",
    "ActivationCode",
    "UserSetting",
    # monitor 模块
    "MonitorConfig",
    "MonitorDailyStats",
    "Task",
]

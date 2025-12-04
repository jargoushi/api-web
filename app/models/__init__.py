"""
数据模型模块
自动导入所有子模块的 Model，供 Tortoise ORM 使用
"""

# 导入 account 模块的所有 Model
from .account.user import User
from .account.user_session import UserSession
from .account.activation_code import ActivationCode

# 导入 monitor 模块的所有 Model
from .monitor.monitor_config import MonitorConfig
from .monitor.monitor_daily_stats import MonitorDailyStats
from .monitor.task import Task

__all__ = [
    # account 模块
    "User",
    "UserSession",
    "ActivationCode",
    # monitor 模块
    "MonitorConfig",
    "MonitorDailyStats",
    "Task",
]

"""
Monitor 仓储模块
"""
from app.repositories.monitor.monitor_config_repository import MonitorConfigRepository
from app.repositories.monitor.monitor_daily_stats_repository import MonitorDailyStatsRepository

__all__ = [
    "MonitorConfigRepository",
    "MonitorDailyStatsRepository",
]

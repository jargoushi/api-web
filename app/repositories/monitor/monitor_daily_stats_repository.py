"""
监控每日数据仓储类
封装监控每日数据相关的所有数据访问操作
"""
from typing import List, Optional, Dict, Any
from datetime import date

from app.repositories.base import BaseRepository
from app.models.monitor.monitor_daily_stats import MonitorDailyStats


class MonitorDailyStatsRepository(BaseRepository[MonitorDailyStats]):
    """
    监控每日数据仓储类

    提供监控每日数据相关的数据访问方法，封装所有与数据库交互的操作
    """

    def __init__(self):
        """初始化监控每日数据仓储"""
        super().__init__(MonitorDailyStats)

    async def find_by_config_and_date_range(
        self,
        config_id: int,
        start_date: date,
        end_date: date
    ) -> List[MonitorDailyStats]:
        """
        根据配置 ID 和日期范围查询每日数据

        Args:
            config_id: 配置 ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            每日数据列表，按日期升序排列
        """
        return await self.model.filter(
            config_id=config_id,
            stat_date__gte=start_date,
            stat_date__lte=end_date
        ).order_by("stat_date").all()

    async def find_by_config_and_date(
        self,
        config_id: int,
        stat_date: date
    ) -> Optional[MonitorDailyStats]:
        """
        根据配置 ID 和日期查询单条数据

        Args:
            config_id: 配置 ID
            stat_date: 统计日期

        Returns:
            每日数据实例，如果不存在则返回 None
        """
        return await self.get_or_none(config_id=config_id, stat_date=stat_date)

    async def create_daily_stats(
        self,
        config_id: int,
        stat_date: date,
        follower_count: int = 0,
        liked_count: int = 0,
        view_count: int = 0,
        content_count: int = 0,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> MonitorDailyStats:
        """
        创建每日数据

        Args:
            config_id: 配置 ID
            stat_date: 统计日期
            follower_count: 粉丝数
            liked_count: 获赞/收藏数
            view_count: 总播放/阅读量
            content_count: 发布内容数量
            extra_data: 渠道特有数据

        Returns:
            创建的每日数据实例
        """
        return await self.create(
            config_id=config_id,
            stat_date=stat_date,
            follower_count=follower_count,
            liked_count=liked_count,
            view_count=view_count,
            content_count=content_count,
            extra_data=extra_data
        )

    async def update_daily_stats(
        self,
        stats: MonitorDailyStats,
        follower_count: Optional[int] = None,
        liked_count: Optional[int] = None,
        view_count: Optional[int] = None,
        content_count: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> MonitorDailyStats:
        """
        更新每日数据

        Args:
            stats: 每日数据实例
            follower_count: 粉丝数
            liked_count: 获赞/收藏数
            view_count: 总播放/阅读量
            content_count: 发布内容数量
            extra_data: 渠道特有数据

        Returns:
            更新后的每日数据实例
        """
        if follower_count is not None:
            stats.follower_count = follower_count
        if liked_count is not None:
            stats.liked_count = liked_count
        if view_count is not None:
            stats.view_count = view_count
        if content_count is not None:
            stats.content_count = content_count
        if extra_data is not None:
            stats.extra_data = extra_data

        await stats.save()
        return stats

    async def upsert_daily_stats(
        self,
        config_id: int,
        stat_date: date,
        follower_count: int = 0,
        liked_count: int = 0,
        view_count: int = 0,
        content_count: int = 0,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> MonitorDailyStats:
        """
        创建或更新每日数据（如果已存在则更新）

        Args:
            config_id: 配置 ID
            stat_date: 统计日期
            follower_count: 粉丝数
            liked_count: 获赞/收藏数
            view_count: 总播放/阅读量
            content_count: 发布内容数量
            extra_data: 渠道特有数据

        Returns:
            每日数据实例
        """
        stats = await self.find_by_config_and_date(config_id, stat_date)

        if stats:
            # 更新已存在的记录
            return await self.update_daily_stats(
                stats,
                follower_count=follower_count,
                liked_count=liked_count,
                view_count=view_count,
                content_count=content_count,
                extra_data=extra_data
            )
        else:
            # 创建新记录
            return await self.create_daily_stats(
                config_id=config_id,
                stat_date=stat_date,
                follower_count=follower_count,
                liked_count=liked_count,
                view_count=view_count,
                content_count=content_count,
                extra_data=extra_data
            )


# 创建单例实例
monitor_daily_stats_repository = MonitorDailyStatsRepository()

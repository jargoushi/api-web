"""
监控配置仓储类
封装监控配置相关的所有数据访问操作
"""
from typing import Optional, List
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.monitor.monitor_config import MonitorConfig
from app.util.time_util import get_utc_now


class MonitorConfigRepository(BaseRepository[MonitorConfig]):
    """
    监控配置仓储类

    提供监控配置相关的数据访问方法，封装所有与数据库交互的操作
    """

    def __init__(self):
        """初始化监控配置仓储"""
        super().__init__(MonitorConfig)

    async def find_by_id(
        self,
        config_id: int,
        user_id: int,
        include_deleted: bool = False
    ) -> Optional[MonitorConfig]:
        """
        根据 ID 查询监控配置

        Args:
            config_id: 配置 ID
            user_id: 用户 ID
            include_deleted: 是否包含已删除的记录

        Returns:
            监控配置实例，如果不存在则返回 None
        """
        filters = {"id": config_id, "user_id": user_id}
        if not include_deleted:
            filters["deleted_at__isnull"] = True

        return await self.get_or_none(**filters)

    def find_with_filters(
        self,
        user_id: int,
        params
    ):
        """
        根据条件查询监控配置列表（返回 QuerySet，用于分页）

        Args:
            user_id: 用户 ID
            params: 查询参数对象

        Returns:
            监控配置查询集（QuerySet）
        """
        query = self.model.filter(user_id=user_id)

        query = query.filter(deleted_at__isnull=True)

        if params.account_name:
            query = query.filter(account_name__icontains=params.account_name)

        if params.channel_code is not None:
            query = query.filter(channel_code=params.channel_code)

        if params.is_active is not None:
            query = query.filter(is_active=params.is_active)

        if params.created_at_start:
            query = query.filter(created_at__gte=params.created_at_start)

        if params.created_at_end:
            query = query.filter(created_at__lte=params.created_at_end)

        return query.order_by("-created_at")

    async def create_monitor_config(
        self,
        user_id: int,
        channel_code: int,
        target_url: str,
        is_active: int = 1,
        target_external_id: Optional[str] = None,
        account_name: Optional[str] = None,
        account_avatar: Optional[str] = None
    ) -> MonitorConfig:
        """
        创建监控配置

        Args:
            user_id: 用户 ID
            channel_code: 渠道编码
            target_url: 监控目标链接
            is_active: 是否启用
            target_external_id: 平台唯一 ID
            account_name: 账号名称
            account_avatar: 账号头像 URL

        Returns:
            创建的监控配置实例
        """
        return await self.create(
            user_id=user_id,
            channel_code=channel_code,
            target_url=target_url,
            is_active=is_active,
            target_external_id=target_external_id,
            account_name=account_name,
            account_avatar=account_avatar
        )

    async def update_monitor_config(
        self,
        config: MonitorConfig,
        target_url: Optional[str] = None,
        target_external_id: Optional[str] = None,
        account_name: Optional[str] = None,
        account_avatar: Optional[str] = None
    ) -> MonitorConfig:
        """
        更新监控配置

        Args:
            config: 监控配置实例
            target_url: 监控目标链接
            target_external_id: 平台唯一 ID
            account_name: 账号名称
            account_avatar: 账号头像 URL

        Returns:
            更新后的监控配置实例
        """
        if target_url is not None:
            config.target_url = target_url
        if target_external_id is not None:
            config.target_external_id = target_external_id
        if account_name is not None:
            config.account_name = account_name
        if account_avatar is not None:
            config.account_avatar = account_avatar

        await config.save()
        return config

    async def toggle_monitor_status(
        self,
        config: MonitorConfig,
        is_active: int
    ) -> MonitorConfig:
        """
        切换监控状态

        Args:
            config: 监控配置实例
            is_active: 是否启用

        Returns:
            更新后的监控配置实例
        """
        config.is_active = is_active
        await config.save()
        return config

    async def soft_delete_config(self, config: MonitorConfig) -> MonitorConfig:
        """
        软删除监控配置

        Args:
            config: 监控配置实例

        Returns:
            更新后的监控配置实例
        """
        config.deleted_at = get_utc_now()
        await config.save()
        return config

    async def update_last_run_info(
        self,
        config: MonitorConfig,
        last_run_at: datetime,
        last_run_status: int
    ) -> MonitorConfig:
        """
        更新最后执行信息

        Args:
            config: 监控配置实例
            last_run_at: 最后执行时间
            last_run_status: 最后执行状态

        Returns:
            更新后的监控配置实例
        """
        config.last_run_at = last_run_at
        config.last_run_status = last_run_status
        await config.save()
        return config


# 创建单例实例
monitor_config_repository = MonitorConfigRepository()

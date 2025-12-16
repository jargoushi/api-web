from typing import List

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.repositories.monitor.monitor_config_repository import monitor_config_repository
from app.repositories.monitor.monitor_daily_stats_repository import monitor_daily_stats_repository
from app.schemas.monitor.monitor import (
    MonitorConfigCreateRequest,
    MonitorConfigUpdateRequest,
    MonitorConfigToggleRequest,
    MonitorConfigQueryRequest,
    MonitorConfigResponse,
    MonitorDailyStatsQueryRequest,
    MonitorDailyStatsResponse
)
from app.util.time_util import get_utc_now


class MonitorService:
    """监控服务类"""

    async def create_monitor_config(self, user_id: int, request: MonitorConfigCreateRequest) -> MonitorConfigResponse:
        """
        创建监控配置

        Args:
            user_id: 用户 ID
            request: 创建请求

        Returns:
            监控配置响应
        """
        log.info(f"用户{user_id}创建监控配置，渠道：{request.channel_code}，链接：{request.target_url}")

        # TODO: 执行爬虫任务解析链接，获取账号信息

        config = await monitor_config_repository.create_monitor_config(
            user_id=user_id,
            channel_code=request.channel_code,
            target_url=request.target_url,
            is_active=1
        )

        log.info(f"监控配置创建成功，ID：{config.id}")
        return MonitorConfigResponse.model_validate(config, from_attributes=True)

    def get_monitor_config_queryset(self, user_id: int, params: MonitorConfigQueryRequest):
        """
        获取监控配置查询集（用于分页）

        Args:
            user_id: 用户 ID
            params: 查询参数

        Returns:
            监控配置查询集（QuerySet）
        """
        return monitor_config_repository.find_with_filters(user_id, params)

    async def update_monitor_config(
        self,
        user_id: int,
        request: MonitorConfigUpdateRequest
    ) -> MonitorConfigResponse:
        """
        修改监控配置

        Args:
            user_id: 用户 ID
            config_id: 配置 ID
            request: 更新请求

        Returns:
            监控配置响应

        Raises:
            BusinessException: 监控配置不存在
        """
        log.info(f"用户{user_id}修改监控配置{request.id}，新链接：{request.target_url}")

        # 查询配置
        config = await monitor_config_repository.find_by_id(request.id, user_id)
        if not config:
            raise BusinessException(message="监控配置不存在")

        # TODO: 执行爬虫任务解析新链接

        config = await monitor_config_repository.update_monitor_config(
            config,
            target_url=request.target_url if request.target_url else None
        )

        log.info(f"监控配置{request.id}修改成功")
        return MonitorConfigResponse.model_validate(config, from_attributes=True)

    async def toggle_monitor_config(
        self,
        user_id: int,
        request: MonitorConfigToggleRequest
    ) -> MonitorConfigResponse:
        """
        切换监控状态

        Args:
            user_id: 用户 ID
            config_id: 配置 ID
            request: 切换请求

        Returns:
            监控配置响应

        Raises:
            BusinessException: 监控配置不存在
        """
        log.info(f"用户{user_id}切换监控配置{request.id}状态为：{request.is_active}")

        # 查询配置
        config = await monitor_config_repository.find_by_id(request.id, user_id)
        if not config:
            raise BusinessException(message="监控配置不存在")

        config = await monitor_config_repository.toggle_monitor_status(config, request.is_active)

        log.info(f"监控配置{request.id}状态切换成功")
        return MonitorConfigResponse.model_validate(config, from_attributes=True)

    async def delete_monitor_config(self, user_id: int, id: int) -> bool:
        """
        删除监控配置（软删除）

        Args:
            user_id: 用户 ID
            config_id: 配置 ID

        Returns:
            是否删除成功

        Raises:
            BusinessException: 监控配置不存在
        """
        log.info(f"用户{user_id}删除监控配置{id}")

        # 查询配置
        config = await monitor_config_repository.find_by_id(id, user_id)
        if not config:
            raise BusinessException(message="监控配置不存在")

        await monitor_config_repository.soft_delete_config(config)

        log.info(f"监控配置{id}删除成功")
        return True

    async def get_daily_stats(
        self,
        user_id: int,
        request: MonitorDailyStatsQueryRequest
    ) -> List[MonitorDailyStatsResponse]:
        """
        查询每日明细数据

        Args:
            user_id: 用户 ID
            request: 查询请求

        Returns:
            每日数据列表

        Raises:
            BusinessException: 监控配置不存在
        """
        log.info(
            f"用户{user_id}查询配置{request.config_id}的每日数据，时间范围：{request.start_date} ~ {request.end_date}")

        # 验证配置归属
        config = await monitor_config_repository.find_by_id(request.config_id, user_id)
        if not config:
            raise BusinessException(message="监控配置不存在")

        stats = await monitor_daily_stats_repository.find_by_config_and_date_range(
            config_id=request.config_id,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return [MonitorDailyStatsResponse.model_validate(stat, from_attributes=True) for stat in stats]


# 创建服务实例
monitor_service = MonitorService()

from typing import List

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.monitor_config import MonitorConfig
from app.models.monitor_daily_stats import MonitorDailyStats
from app.schemas.monitor import (
    MonitorConfigCreateRequest,
    MonitorConfigUpdateRequest,
    MonitorConfigToggleRequest,
    MonitorConfigQueryRequest,
    MonitorConfigResponse,
    MonitorDailyStatsQueryRequest,
    MonitorDailyStatsResponse
)


class MonitorService:
    """监控服务"""

    @staticmethod
    async def create_monitor_config(user_id: int, request: MonitorConfigCreateRequest) -> MonitorConfigResponse:
        """创建监控配置"""
        log.info(f"用户{user_id}创建监控配置，渠道：{request.channel_code}，链接：{request.target_url}")

        # TODO: 执行爬虫任务解析链接，获取账号信息

        config = await MonitorConfig.create(
            user_id=user_id,
            channel_code=request.channel_code,
            target_url=request.target_url,
            is_active=1
        )

        log.info(f"监控配置创建成功，ID：{config.id}")
        return MonitorConfigResponse.model_validate(config, from_attributes=True)

    @staticmethod
    def get_monitor_config_queryset(user_id: int, params: MonitorConfigQueryRequest):
        """获取监控配置查询集"""
        query = MonitorConfig.filter(user_id=user_id, deleted_at__isnull=True)

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

    @staticmethod
    async def update_monitor_config(user_id: int, config_id: int,
                                    request: MonitorConfigUpdateRequest) -> MonitorConfigResponse:
        """修改监控配置"""
        log.info(f"用户{user_id}修改监控配置{config_id}，新链接：{request.target_url}")

        config = await MonitorConfig.get_or_none(id=config_id, user_id=user_id, deleted_at__isnull=True)
        if not config:
            raise BusinessException(message="监控配置不存在")

        # TODO: 执行爬虫任务解析新链接

        config.target_url = request.target_url
        await config.save()

        log.info(f"监控配置{config_id}修改成功")
        return MonitorConfigResponse.model_validate(config, from_attributes=True)

    @staticmethod
    async def toggle_monitor_config(user_id: int, config_id: int,
                                    request: MonitorConfigToggleRequest) -> MonitorConfigResponse:
        """切换监控状态"""
        log.info(f"用户{user_id}切换监控配置{config_id}状态为：{request.is_active}")

        config = await MonitorConfig.get_or_none(id=config_id, user_id=user_id, deleted_at__isnull=True)
        if not config:
            raise BusinessException(message="监控配置不存在")

        config.is_active = request.is_active
        await config.save()

        log.info(f"监控配置{config_id}状态切换成功")
        return MonitorConfigResponse.model_validate(config, from_attributes=True)

    @staticmethod
    async def delete_monitor_config(user_id: int, config_id: int) -> bool:
        """删除监控配置（软删除）"""
        log.info(f"用户{user_id}删除监控配置{config_id}")

        config = await MonitorConfig.get_or_none(id=config_id, user_id=user_id, deleted_at__isnull=True)
        if not config:
            raise BusinessException(message="监控配置不存在")

        config.soft_delete()
        await config.save()

        log.info(f"监控配置{config_id}删除成功")
        return True

    @staticmethod
    async def get_daily_stats(user_id: int, request: MonitorDailyStatsQueryRequest) -> List[MonitorDailyStatsResponse]:
        """查询每日明细数据"""
        log.info(
            f"用户{user_id}查询配置{request.config_id}的每日数据，时间范围：{request.start_date} ~ {request.end_date}")

        # 验证配置归属
        config = await MonitorConfig.get_or_none(id=request.config_id, user_id=user_id, deleted_at__isnull=True)
        if not config:
            raise BusinessException(message="监控配置不存在")

        # 查询每日数据
        stats = await MonitorDailyStats.filter(
            config_id=request.config_id,
            stat_date__gte=request.start_date,
            stat_date__lte=request.end_date
        ).order_by("stat_date")

        return [MonitorDailyStatsResponse.model_validate(stat, from_attributes=True) for stat in stats]

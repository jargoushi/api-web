from fastapi import APIRouter, Depends

from app.schemas.monitor.monitor import (
    MonitorConfigCreateRequest,
    MonitorConfigUpdateRequest,
    MonitorConfigToggleRequest,
    MonitorConfigQueryRequest,
    MonitorConfigResponse,
    MonitorDailyStatsQueryRequest,
    MonitorDailyStatsResponse
)
from app.schemas.common.pagination import PageResponse
from app.schemas.common.response import ApiResponse, success_response, paginated_response
from app.services.monitor.monitor_service import monitor_service
from app.util.auth_context import get_current_user_id

router = APIRouter()


@router.post("/config", response_model=ApiResponse[MonitorConfigResponse], summary="创建监控配置")
async def create_monitor_config(
    request: MonitorConfigCreateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    创建监控配置

    - **channel_code**: 渠道编码（1:小红书 2:哔哩哔哩 3:YouTube 4:微信公众号 5:微信视频号）
    - **target_url**: 监控目标链接
    """
    result = await monitor_service.create_monitor_config(user_id, request)
    return success_response(data=result)


@router.post("/config/pageList", response_model=ApiResponse[PageResponse[MonitorConfigResponse]], summary="分页查询监控列表")
async def get_monitor_config_list(
    params: MonitorConfigQueryRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    分页查询监控配置列表（支持多维度筛选）
    """
    query = monitor_service.get_monitor_config_queryset(user_id, params)
    return await paginated_response(query, params)


@router.post("/config/update", response_model=ApiResponse[MonitorConfigResponse], summary="修改监控配置")
async def update_monitor_config(
    request: MonitorConfigUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    修改监控配置

    - **config_id**: 配置ID
    - **target_url**: 新的监控目标链接
    """
    result = await monitor_service.update_monitor_config(user_id, request)
    return success_response(data=result)


@router.post("/config/toggle", response_model=ApiResponse[MonitorConfigResponse], summary="切换监控状态")
async def toggle_monitor_config(
    request: MonitorConfigToggleRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    切换监控启用/禁用状态

    - **config_id**: 配置ID
    - **is_active**: 是否启用（0:否 1:是）
    """
    result = await monitor_service.toggle_monitor_config(user_id, request)
    return success_response(data=result)


@router.post("/config/delete", response_model=ApiResponse[bool], summary="删除监控配置")
async def delete_monitor_config(
    id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    删除监控配置（软删除）

    - **config_id**: 配置ID
    """
    result = await monitor_service.delete_monitor_config(user_id, id)
    return success_response(data=result)


@router.post("/stats/daily", response_model=ApiResponse[list[MonitorDailyStatsResponse]], summary="查询每日明细数据")
async def get_daily_stats(
    request: MonitorDailyStatsQueryRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    查询指定配置的每日明细数据（用于图表展示）

    - **config_id**: 配置ID
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    result = await monitor_service.get_daily_stats(user_id, request)
    return success_response(data=result)

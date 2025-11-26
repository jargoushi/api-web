from fastapi import APIRouter, Depends

from app.schemas.monitor import (
    MonitorConfigCreateRequest,
    MonitorConfigUpdateRequest,
    MonitorConfigToggleRequest,
    MonitorConfigQueryRequest,
    MonitorConfigResponse,
    MonitorDailyStatsQueryRequest,
    MonitorDailyStatsResponse
)
from app.schemas.pagination import PageResponse
from app.schemas.response import ApiResponse, success_response, paginated_response
from app.services.monitor_service import MonitorService

router = APIRouter()


# TODO: 替换为实际的用户认证依赖
async def get_current_user_id() -> int:
    """获取当前用户ID（临时实现）"""
    return 1


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
    result = await MonitorService.create_monitor_config(user_id, request)
    return success_response(data=result)


@router.post("/config/pageList", response_model=ApiResponse[PageResponse[MonitorConfigResponse]], summary="分页查询监控列表")
async def get_monitor_config_list(
    params: MonitorConfigQueryRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    分页查询监控配置列表

    - **page**: 页码，从1开始
    - **size**: 每页数量
    - **account_name**: 账号名称（模糊查询）
    - **channel_code**: 渠道编码
    - **is_active**: 是否启用（0:否 1:是）
    - **created_at_start**: 创建时间开始
    - **created_at_end**: 创建时间结束
    """
    query = MonitorService.get_monitor_config_queryset(user_id, params)
    return await paginated_response(query, params)


@router.put("/config/{config_id}", response_model=ApiResponse[MonitorConfigResponse], summary="修改监控配置")
async def update_monitor_config(
    config_id: int,
    request: MonitorConfigUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    修改监控配置

    - **target_url**: 新的监控目标链接
    """
    result = await MonitorService.update_monitor_config(user_id, config_id, request)
    return success_response(data=result)


@router.patch("/config/{config_id}/toggle", response_model=ApiResponse[MonitorConfigResponse], summary="切换监控状态")
async def toggle_monitor_config(
    config_id: int,
    request: MonitorConfigToggleRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    切换监控启用/禁用状态

    - **is_active**: 是否启用（0:否 1:是）
    """
    result = await MonitorService.toggle_monitor_config(user_id, config_id, request)
    return success_response(data=result)


@router.delete("/config/{config_id}", response_model=ApiResponse[bool], summary="删除监控配置")
async def delete_monitor_config(
    config_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """
    删除监控配置（软删除）
    """
    result = await MonitorService.delete_monitor_config(user_id, config_id)
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
    result = await MonitorService.get_daily_stats(user_id, request)
    return success_response(data=result)

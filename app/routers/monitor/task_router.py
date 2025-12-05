from fastapi import APIRouter

from app.schemas.monitor.task import MonitorTaskQueryRequest, MonitorTaskResponse
from app.schemas.common.pagination import PageResponse
from app.schemas.common.response import ApiResponse, paginated_response
from app.services.monitor.task_service import task_service

router = APIRouter()


@router.post("/pageList", response_model=ApiResponse[PageResponse[MonitorTaskResponse]], summary="分页查询任务列表")
async def get_monitor_task_list(params: MonitorTaskQueryRequest):
    """
    分页查询任务列表（支持多维度筛选）
    """
    query = task_service.get_monitor_task_queryset(params)
    return await paginated_response(query, params)

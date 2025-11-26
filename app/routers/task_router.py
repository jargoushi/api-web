from fastapi import APIRouter

from app.schemas.task import MonitorTaskQueryRequest, MonitorTaskResponse
from app.schemas.pagination import PageResponse
from app.schemas.response import ApiResponse, paginated_response
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/pageList", response_model=ApiResponse[PageResponse[MonitorTaskResponse]], summary="分页查询任务列表")
async def get_monitor_task_list(params: MonitorTaskQueryRequest):
    """
    分页查询任务列表（支持多维度筛选）

    - **page**: 页码，从1开始
    - **size**: 每页数量
    - **channel_code**: 渠道编码
    - **task_type**: 任务类型（1:每日数据采集 2:手动刷新）
    - **task_status**: 任务状态（0:待执行 1:进行中 2:成功 3:失败）
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    query = TaskService.get_monitor_task_queryset(params)
    return await paginated_response(query, params)

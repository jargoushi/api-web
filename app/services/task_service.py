from app.models.task import Task
from app.schemas.task import MonitorTaskQueryRequest


class TaskService:
    """任务服务（独立服务）"""

    @staticmethod
    def get_monitor_task_queryset(params: MonitorTaskQueryRequest):
        """获取任务查询集"""
        query = Task.all()

        if params.channel_code is not None:
            query = query.filter(channel_code=params.channel_code)

        if params.task_type is not None:
            query = query.filter(task_type=params.task_type)

        if params.task_status is not None:
            query = query.filter(task_status=params.task_status)

        if params.start_date:
            query = query.filter(schedule_date__gte=params.start_date)

        if params.end_date:
            query = query.filter(schedule_date__lte=params.end_date)

        return query.order_by("-created_at")

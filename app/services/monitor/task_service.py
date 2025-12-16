from app.repositories.monitor.task_repository import task_repository
from app.schemas.monitor.task import MonitorTaskQueryRequest


class TaskService:
    """任务服务类"""

    def get_monitor_task_queryset(self, params: MonitorTaskQueryRequest):
        """
        获取任务查询集（用于分页）

        Args:
            params: 任务查询请求参数

        Returns:
            任务查询集（QuerySet）
        """
        return task_repository.find_with_filters(
            channel_code=params.channel_code,
            task_type=params.task_type,
            task_status=params.task_status,
            start_date=params.start_date,
            end_date=params.end_date
        )


# 创建服务实例
task_service = TaskService()

from app.repositories.monitor import TaskRepository
from app.schemas.monitor.task import MonitorTaskQueryRequest


class TaskService:
    """任务服务类"""

    def __init__(
        self,
        repository: TaskRepository = TaskRepository()
    ):
        """
        初始化服务

        Args:
            repository: 任务仓储实例
        """
        self.repository = repository

    def get_monitor_task_queryset(self, params: MonitorTaskQueryRequest):
        """
        获取任务查询集

        Args:
            params: 任务查询请求参数

        Returns:
            任务查询集
        """
        return self.repository.find_with_filters(
            channel_code=params.channel_code,
            task_type=params.task_type,
            task_status=params.task_status,
            start_date=params.start_date,
            end_date=params.end_date
        )


# 创建服务实例
task_service = TaskService()

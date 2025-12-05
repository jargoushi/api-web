from datetime import date
from typing import Optional, List

from app.repositories.base import BaseRepository
from app.models.monitor.task import Task


class TaskRepository(BaseRepository[Task]):

    def __init__(self):
        """初始化任务仓储"""
        super().__init__(Task)

    def find_with_filters(
        self,
        channel_code: Optional[int] = None,
        task_type: Optional[int] = None,
        task_status: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ):
        """
        根据条件查询任务列表（返回 QuerySet，用于分页）

        Args:
            channel_code: 渠道编码（可选）
            task_type: 任务类型（可选）
            task_status: 任务状态（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            任务查询集（QuerySet）
        """
        query = self.model.all()

        if channel_code is not None:
            query = query.filter(channel_code=channel_code)

        if task_type is not None:
            query = query.filter(task_type=task_type)

        if task_status is not None:
            query = query.filter(task_status=task_status)

        if start_date:
            query = query.filter(schedule_date__gte=start_date)

        if end_date:
            query = query.filter(schedule_date__lte=end_date)

        return query.order_by("-created_at")


# 创建仓储实例
task_repository = TaskRepository()

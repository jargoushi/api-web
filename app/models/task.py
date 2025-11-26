from tortoise import fields
from tortoise.models import Model

from app.enums.channel_enum import ChannelEnum
from app.enums.task_status_enum import TaskStatusEnum
from app.enums.task_type_enum import TaskTypeEnum


class Task(Model):
    """监控任务模型"""
    id = fields.IntField(pk=True, description="任务ID")
    channel_code = fields.IntField(description="渠道编码")
    task_type = fields.IntField(description="任务类型")
    biz_id = fields.IntField(description="业务ID")
    task_status = fields.IntField(default=0, description="任务状态")
    schedule_date = fields.DateField(description="调度日期")
    error_msg = fields.TextField(null=True, description="异常信息栈")
    duration_ms = fields.IntField(default=0, description="耗时(ms)")
    created_at = fields.DatetimeField(auto_now_add=True, description="任务创建时间")
    started_at = fields.DatetimeField(null=True, description="开始执行时间")
    finished_at = fields.DatetimeField(null=True, description="结束执行时间")

    class Meta:
        table = "tasks"
        ordering = ["-created_at"]

    @property
    def channel_enum(self) -> ChannelEnum:
        """获取渠道枚举"""
        return ChannelEnum.from_code(self.channel_code)

    @property
    def channel_name(self) -> str:
        """获取渠道名称"""
        return self.channel_enum.desc

    @property
    def task_type_enum(self) -> TaskTypeEnum:
        """获取任务类型枚举"""
        return TaskTypeEnum.from_code(self.task_type)

    @property
    def task_type_name(self) -> str:
        """获取任务类型名称"""
        return self.task_type_enum.desc

    @property
    def task_status_enum(self) -> TaskStatusEnum:
        """获取任务状态枚举"""
        return TaskStatusEnum.from_code(self.task_status)

    @property
    def task_status_name(self) -> str:
        """获取任务状态名称"""
        return self.task_status_enum.desc

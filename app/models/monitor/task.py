from tortoise import fields

from app.models.base import BaseModel
from app.enums.common.channel import ChannelEnum
from app.enums.monitor.task_status import TaskStatusEnum
from app.enums.monitor.task_type import TaskTypeEnum


class Task(BaseModel):
    """监控任务模型"""
    # 基础字段 (id, created_at, updated_at) 继承自 BaseModel
    channel_code = fields.IntField(description="渠道编码")
    task_type = fields.IntField(description="任务类型")
    biz_id = fields.IntField(description="业务ID")
    task_status = fields.IntField(default=0, description="任务状态")
    schedule_date = fields.DateField(description="调度日期")
    error_msg = fields.TextField(null=True, description="异常信息栈")
    duration_ms = fields.IntField(default=0, description="耗时(ms)")
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

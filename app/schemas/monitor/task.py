from datetime import datetime
from typing import Optional

from pydantic import Field, model_validator

from app.schemas.common.base import BaseResponseModel
from app.schemas.common.pagination import PageRequest


class MonitorTaskQueryRequest(PageRequest):
    """任务查询请求"""
    channel_code: Optional[int] = Field(None, ge=1, le=5, description="渠道编码")
    task_type: Optional[int] = Field(None, ge=1, le=2, description="任务类型")
    task_status: Optional[int] = Field(None, ge=0, le=3, description="任务状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")

    @model_validator(mode='after')
    def validate_date_range(self):
        """验证日期区间"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("开始日期不能大于结束日期")
        return self


class MonitorTaskResponse(BaseResponseModel):
    """任务响应"""
    id: int = Field(..., description="任务ID")
    channel_code: int = Field(..., description="渠道编码")
    channel_name: str = Field(..., description="渠道名称")
    task_type: int = Field(..., description="任务类型")
    task_type_name: str = Field(..., description="任务类型名称")
    biz_id: int = Field(..., description="业务ID")
    task_status: int = Field(..., description="任务状态")
    task_status_name: str = Field(..., description="任务状态名称")
    schedule_date: datetime = Field(..., description="调度日期")
    error_msg: Optional[str] = Field(None, description="错误信息")
    duration_ms: int = Field(..., description="耗时(ms)")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    finished_at: Optional[datetime] = Field(None, description="结束时间")

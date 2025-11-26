from datetime import datetime, date
from typing import Optional, Dict, Any

from pydantic import Field, model_validator

from app.schemas.base import BaseRequestModel, BaseResponseModel
from app.schemas.pagination import PageRequest


# ============ 监控配置相关 ============

class MonitorConfigCreateRequest(BaseRequestModel):
    """创建监控配置请求"""
    channel_code: int = Field(..., ge=1, le=5, description="渠道编码")
    target_url: str = Field(..., min_length=1, max_length=512, description="监控目标链接")


class MonitorConfigUpdateRequest(BaseRequestModel):
    """修改监控配置请求"""
    target_url: str = Field(..., min_length=1, max_length=512, description="监控目标链接")


class MonitorConfigToggleRequest(BaseRequestModel):
    """切换监控状态请求"""
    is_active: int = Field(..., ge=0, le=1, description="是否启用 0:否 1:是")


class MonitorConfigQueryRequest(PageRequest):
    """监控配置查询请求"""
    account_name: Optional[str] = Field(None, max_length=128, description="账号名称（模糊查询）")
    channel_code: Optional[int] = Field(None, ge=1, le=5, description="渠道编码")
    is_active: Optional[int] = Field(None, ge=0, le=1, description="是否启用")
    created_at_start: Optional[datetime] = Field(None, description="创建时间开始")
    created_at_end: Optional[datetime] = Field(None, description="创建时间结束")

    @model_validator(mode='after')
    def validate_time_range(self):
        """验证时间区间"""
        if self.created_at_start and self.created_at_end:
            if self.created_at_start > self.created_at_end:
                raise ValueError("创建时间开始不能大于结束时间")
        return self


class MonitorConfigResponse(BaseResponseModel):
    """监控配置响应"""
    id: int = Field(..., description="配置ID")
    user_id: int = Field(..., description="用户ID")
    channel_code: int = Field(..., description="渠道编码")
    channel_name: str = Field(..., description="渠道名称")
    target_url: str = Field(..., description="监控目标链接")
    target_external_id: Optional[str] = Field(None, description="平台唯一ID")
    account_name: Optional[str] = Field(None, description="账号名称")
    account_avatar: Optional[str] = Field(None, description="账号头像")
    is_active: int = Field(..., description="是否启用")
    last_run_at: Optional[datetime] = Field(None, description="上次执行时间")
    last_run_status: Optional[int] = Field(None, description="上次执行结果")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============ 每日明细数据相关 ============

class MonitorDailyStatsQueryRequest(BaseRequestModel):
    """每日明细数据查询请求"""
    config_id: int = Field(..., description="配置ID")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")

    @model_validator(mode='after')
    def validate_date_range(self):
        """验证日期区间"""
        if self.start_date > self.end_date:
            raise ValueError("开始日期不能大于结束日期")
        return self


class MonitorDailyStatsResponse(BaseResponseModel):
    """每日明细数据响应"""
    id: int = Field(..., description="记录ID")
    config_id: int = Field(..., description="配置ID")
    stat_date: date = Field(..., description="统计日期")
    follower_count: int = Field(..., description="粉丝数")
    liked_count: int = Field(..., description="获赞数")
    view_count: int = Field(..., description="播放量")
    content_count: int = Field(..., description="内容数")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="扩展数据")
    created_at: datetime = Field(..., description="创建时间")

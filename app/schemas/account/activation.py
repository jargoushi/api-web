from datetime import datetime
from typing import List, Dict, Optional

from pydantic import Field, ConfigDict, field_validator, model_validator

from app.enums.account.activation_type import ActivationTypeEnum
from app.schemas.common.base import BaseRequestModel, BaseResponseModel
from app.schemas.common.pagination import PageRequest


class ActivationCodeCreateItem(BaseRequestModel):
    """单个激活码创建项"""
    type: int = Field(..., ge=0, le=3,
                      description=f"激活码类型：{', '.join([f'{e.code}：{e.desc}' for e in ActivationTypeEnum])}")
    count: int = Field(..., ge=1, le=1000, description="生成数量")


class ActivationCodeBatchCreateRequest(BaseRequestModel):
    """批量创建激活码的请求模型"""
    items: List[ActivationCodeCreateItem] = Field(..., min_items=1, max_items=10, description="激活码创建项列表")

    @classmethod
    @field_validator('items')
    def validate_items(cls, v):
        """验证创建项列表"""
        type_counts = {}
        for item in v:
            if item.type in type_counts:
                raise ValueError(f"激活码类型 {item.type} 重复，每种类型只能出现一次")
            type_counts[item.type] = item.count
        return v


class ActivationCodeTypeResult(BaseRequestModel):
    """单个类型的激活码结果"""
    type: int = Field(..., description="类型码")
    type_name: str = Field(..., description="类型名称")
    activation_codes: List[str] = Field(..., description="激活码列表")
    count: int = Field(..., description="数量")


class ActivationCodeBatchResponse(BaseResponseModel):
    """批量激活码响应模型"""
    results: List[ActivationCodeTypeResult] = Field(..., description="各类型激活码结果")
    total_count: int = Field(..., description="总数量")
    summary: Dict[str, int] = Field(..., description="各类型数量汇总")


class ActivationCodeGetRequest(BaseRequestModel):
    """获取激活码的请求模型"""
    type: int = Field(..., ge=0, le=3,
                      description=f"激活码类型：{', '.join([f'{e.code}：{e.desc}' for e in ActivationTypeEnum])}")
    count: int = Field(1, ge=1, le=100, description="查询条数，默认1条")


class ActivationCodeInvalidateRequest(BaseRequestModel):
    """作废激活码的请求模型"""
    activation_code: str = Field(..., min_length=1, max_length=50, description="激活码")


class ActivationCodeQueryRequest(PageRequest):
    """激活码列表查询参数（继承分页参数）"""
    type: Optional[int] = Field(None, ge=0, le=3, description="激活码类型")
    activation_code: Optional[str] = Field(None, min_length=1, max_length=50, description="激活码（精准匹配）")
    status: Optional[int] = Field(None, ge=0, le=3, description="激活码状态")
    distributed_at_start: Optional[datetime] = Field(None, description="分发时间开始")
    distributed_at_end: Optional[datetime] = Field(None, description="分发时间结束")
    activated_at_start: Optional[datetime] = Field(None, description="激活时间开始")
    activated_at_end: Optional[datetime] = Field(None, description="激活时间结束")
    expire_time_start: Optional[datetime] = Field(None, description="过期时间开始")
    expire_time_end: Optional[datetime] = Field(None, description="过期时间结束")

    @model_validator(mode='after')
    def validate_time_ranges(self):
        """验证所有时间区间"""
        errors = []

        # 验证分发时间区间
        if self.distributed_at_start and self.distributed_at_end:
            if self.distributed_at_start > self.distributed_at_end:
                errors.append("分发时间开始不能大于结束时间")

        # 验证激活时间区间
        if self.activated_at_start and self.activated_at_end:
            if self.activated_at_start > self.activated_at_end:
                errors.append("激活时间开始不能大于结束时间")

        # 验证过期时间区间
        if self.expire_time_start and self.expire_time_end:
            if self.expire_time_start > self.expire_time_end:
                errors.append("过期时间开始不能大于结束时间")

        if errors:
            raise ValueError("; ".join(errors))

        return self


class ActivationCodeResponse(BaseResponseModel):
    """激活码响应模型"""
    id: int = Field(..., description="激活码ID")
    activation_code: str = Field(..., description="激活码")
    distributed_at: Optional[datetime] = Field(None, description="分发时间")
    expire_time: Optional[datetime] = Field(None, description="过期时间")  # 改为可选
    type: int = Field(..., description="类型码")
    type_name: str = Field(..., description="类型名称")
    status: int = Field(..., description="状态码：0：未使用 1：已分发 2：已激活 3：作废")
    status_name: str = Field(..., description="状态名称")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    activated_at: Optional[datetime] = Field(None, description="激活时间")  # 新增字段


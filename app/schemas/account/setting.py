"""用户配置Schema"""

from datetime import datetime
from typing import Any, Optional, List

from pydantic import Field

from app.schemas.common.base import BaseRequestModel, BaseResponseModel


class SettingUpdateRequest(BaseRequestModel):
    """更新配置请求"""
    setting_key: int = Field(..., description="配置项编码")
    setting_value: Any = Field(..., description="配置值")


class SettingResponse(BaseResponseModel):
    """配置响应"""
    setting_key: int = Field(..., description="配置项编码")
    setting_key_name: str = Field(..., description="配置项名称")
    setting_value: Any = Field(..., description="配置值")
    group: str = Field(..., description="所属分组名称")
    value_type: str = Field(..., description="值类型")
    is_default: bool = Field(..., description="是否为默认值")


class SettingGroupResponse(BaseResponseModel):
    """分组配置响应"""
    group: str = Field(..., description="分组名称")
    group_code: int = Field(..., description="分组编码")
    settings: List[SettingResponse] = Field(..., description="该分组下的配置列表")


class AllSettingsResponse(BaseResponseModel):
    """所有配置响应"""
    groups: List[SettingGroupResponse] = Field(..., description="按分组组织的配置")

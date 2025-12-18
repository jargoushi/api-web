"""公共响应模型"""

from typing import Optional, List, Any

from pydantic import Field

from app.schemas.common.base import BaseResponseModel


class EnumResponse(BaseResponseModel):
    """枚举响应（通用）

    所有枚举类返回给前端的统一格式
    """
    code: int = Field(..., description="编码")
    desc: str = Field(..., description="描述")


class SettingItemMetadata(BaseResponseModel):
    """配置项元数据"""
    code: int = Field(..., description="配置项编码")
    name: str = Field(..., description="配置项名称")
    type: str = Field(..., description="值类型")
    default: Any = Field(..., description="默认值")
    options: Optional[List[dict]] = Field(None, description="选项列表")
    required: bool = Field(False, description="是否必填")


class SettingGroupMetadata(BaseResponseModel):
    """配置分组元数据"""
    code: int = Field(..., description="分组编码")
    name: str = Field(..., description="分组名称")
    icon: str = Field(..., description="分组图标")
    settings: List[SettingItemMetadata] = Field(..., description="配置项列表")


class SettingsMetadataResponse(BaseResponseModel):
    """配置元数据响应"""
    groups: List[SettingGroupMetadata] = Field(..., description="配置分组列表")

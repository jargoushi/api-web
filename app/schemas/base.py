from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class BaseRequestModel(BaseModel):
    """所有请求模型的基类，自动处理时间格式"""
    model_config = ConfigDict(
        populate_by_name=True,
        extra='ignore'
    )

    # @classmethod
    # @field_validator('*')
    # def validate_datetime_fields(cls, v: Any, info) -> Any:
    #     """自动验证所有 datetime 类型的字段"""
    #     # 获取字段的类型注解
    #     field_name = info.field_name
    #     if field_name not in cls.model_fields:
    #         return v
    #
    #     field_info = cls.model_fields[field_name]
    #
    #     # 只处理 Optional[datetime] 或 datetime 类型的字段
    #     if (hasattr(field_info, 'annotation') and
    #             field_info.annotation and
    #             ('datetime' in str(field_info.annotation))):
    #
    #         if v is None:
    #             return None
    #
    #         if isinstance(v, datetime):
    #             return v
    #
    #         if isinstance(v, str):
    #             try:
    #                 return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
    #             except ValueError:
    #                 raise ValueError(
    #                     f"字段 {field_name} 时间格式错误，请使用 yyyy-MM-dd HH:mm:ss 格式"
    #                 )
    #
    #     return v


class BaseResponseModel(BaseModel):
    """所有响应模型的基类"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        },
        from_attributes=True,
        populate_by_name=True,
        extra='ignore'
    )

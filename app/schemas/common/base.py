from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseRequestModel(BaseModel):
    """所有请求模型的基类，自动处理时间格式"""
    model_config = ConfigDict(
        populate_by_name=True,
        extra='ignore'
    )


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

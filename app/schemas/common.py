from pydantic import BaseModel, Field


class ChannelResponse(BaseModel):
    """渠道信息响应"""
    code: int = Field(..., description="渠道编码")
    desc: str = Field(..., description="渠道中文描述")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 1,
                "desc": "小红书"
            }
        }

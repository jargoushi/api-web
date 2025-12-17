"""公共响应模型"""

from pydantic import Field

from app.schemas.common.base import BaseResponseModel


class EnumResponse(BaseResponseModel):
    """枚举响应（通用）

    所有枚举类返回给前端的统一格式
    """
    code: int = Field(..., description="编码")
    desc: str = Field(..., description="描述")

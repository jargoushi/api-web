from fastapi import APIRouter

from app.schemas.response import success_response

router = APIRouter()


@router.get("/")
async def health_check():
    """健康检查"""
    return success_response(
        data="健康检查通过"
    )

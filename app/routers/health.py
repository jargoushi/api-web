from fastapi import APIRouter

from app.schemas.response import success_response

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return success_response(
        data={"status": "healthy"},
        message="服务健康"
    )

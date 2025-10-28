from fastapi import APIRouter

from app.routers import activation_code_router
from app.routers import browser_router
from app.routers import index_router
from app.routers import user_router

# 创建主 APIRouter，作为所有子路由的入口
api_router = APIRouter()


def setup_routers():
    """
    设置并聚合所有子模块路由
    在这里统一管理所有路由的前缀、标签等信息
    """

    # 聚合子路由，并统一添加前缀和标签
    api_router.include_router(user_router.router, prefix="/users", tags=["用户管理"])

    api_router.include_router(index_router.router, prefix="/index", tags=["系统"])

    api_router.include_router(browser_router.router, prefix="/browser", tags=["比特浏览器"])

    api_router.include_router(activation_code_router.router, prefix="/activation", tags=["激活码管理"])


# 执行路由设置
setup_routers()

# 导出主路由，供 main.py 使用
__all__ = ["api_router"]

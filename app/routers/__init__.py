from fastapi import APIRouter


# 创建主 APIRouter，作为所有子路由的入口
api_router = APIRouter()


def setup_routers():
    """
    设置并聚合所有子模块路由
    在这里统一管理所有路由的前缀、标签等信息
    """
    # 导入所有子模块路由
    from app.routers import user_router
    from app.routers import index_router
    from app.routers import bit_browser_router

    # 聚合子路由，并统一添加前缀和标签
    api_router.include_router(
        user_router.router,
        prefix="/users",
        tags=["用户管理"]
    )

    # 新增模块时，只需在这里添加一行 include_router 即可
    api_router.include_router(
        index_router.router,
        prefix="/index",
        tags=["系统"]
    )

    api_router.include_router(
        bit_browser_router.router,
        prefix="/browser",
        tags=["比特浏览器"]
    )


# 执行路由设置
setup_routers()

# 导出主路由，供 main.py 使用
__all__ = ["api_router"]

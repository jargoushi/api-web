from fastapi import APIRouter

from app.routers import activation_code_router
from app.routers import auth_router
from app.routers import browser_router
from app.routers import common_router
from app.routers import index_router
from app.routers import monitor_router
from app.routers import task_router
from app.routers import user_router

# 创建主 APIRouter，作为所有子路由的入口
api_router = APIRouter()


def setup_routers():
    """
    设置并聚合所有子模块路由
    在这里统一管理所有路由的前缀、标签等信息
    """

    # 认证相关路由（包含登录等不需要认证的接口）
    api_router.include_router(auth_router.router, prefix="/auth", tags=["认证管理"])

    # 激活码相关路由（根据业务需求，大部分不需要认证）
    api_router.include_router(activation_code_router.router, prefix="/activation", tags=["激活码管理"])

    # 系统相关路由（通常不需要认证）
    api_router.include_router(index_router.router, prefix="/index", tags=["系统"])

    # 公共业务路由（枚举配置、字典数据等，不需要认证）
    api_router.include_router(common_router.router, prefix="/common", tags=["公共接口"])

    # 用户管理相关路由（需要认证 - 由中间件控制）
    api_router.include_router(user_router.router, prefix="/users", tags=["用户管理"])

    # 监控中心相关路由（需要认证 - 由中间件控制）
    api_router.include_router(monitor_router.router, prefix="/monitor", tags=["监控中心"])

    # 监控任务相关路由（独立服务 - 需要认证）
    api_router.include_router(task_router.router, prefix="/task", tags=["任务管理"])

    # 比特浏览器相关路由（需要认证 - 由中间件控制）
    api_router.include_router(browser_router.router, prefix="/browser", tags=["比特浏览器"])


# 执行路由设置
setup_routers()

# 导出主路由，供 main.py 使用
__all__ = ["api_router"]

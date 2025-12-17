"""
路由模块
按业务领域组织路由：account（账户）、monitor（监控）、system（系统）
"""
from fastapi import APIRouter

# 导入各模块路由
from app.routers.account import auth_router, user_router, activation_router, setting_router, account_router
from app.routers.monitor import monitor_router, task_router, browser_router
from app.routers.system import common_router

# 创建主 APIRouter，作为所有子路由的入口
api_router = APIRouter()


def setup_routers():
    """
    设置并聚合所有子模块路由
    按业务领域组织：account（账户）、monitor（监控）、system（系统）
    """

    # ==================== 账户模块 ====================
    # 认证相关路由（包含登录等不需要认证的接口）
    api_router.include_router(
        auth_router.router,
        prefix="/auth",
        tags=["账户-认证管理"]
    )

    # 用户管理相关路由（需要认证 - 由中间件控制）
    api_router.include_router(
        user_router.router,
        prefix="/users",
        tags=["账户-用户管理"]
    )

    # 激活码相关路由（根据业务需求，大部分不需要认证）
    api_router.include_router(
        activation_router.router,
        prefix="/activation",
        tags=["账户-激活码管理"]
    )

    # 用户配置相关路由（需要认证）
    api_router.include_router(
        setting_router.router,
        prefix="/settings",
        tags=["账户-配置管理"]
    )

    # 账号管理相关路由（需要认证）
    api_router.include_router(
        account_router.router,
        prefix="/accounts",
        tags=["账户-账号管理"]
    )

    # ==================== 监控模块 ====================
    # 监控中心相关路由（需要认证 - 由中间件控制）
    api_router.include_router(
        monitor_router.router,
        prefix="/monitor",
        tags=["监控-监控中心"]
    )

    # 监控任务相关路由（需要认证）
    api_router.include_router(
        task_router.router,
        prefix="/task",
        tags=["监控-任务管理"]
    )

    # 比特浏览器相关路由（需要认证 - 由中间件控制）
    api_router.include_router(
        browser_router.router,
        prefix="/browser",
        tags=["监控-浏览器管理"]
    )

    # ==================== 系统模块 ====================
    # 公共业务路由（枚举配置、项目信息等，不需要认证）
    api_router.include_router(
        common_router.router,
        prefix="/common",
        tags=["系统-公共接口"]
    )


# 执行路由设置
setup_routers()

# 导出主路由，供 main.py 使用
__all__ = ["api_router"]

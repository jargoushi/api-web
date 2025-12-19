import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import log
from app.core.middleware import setup_middleware
from app.db.config import init_db, close_db
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    log.info("🚀 应用启动中...")

    # 初始化数据库连接
    await init_db()
    log.info("✅ 数据库连接已建立")

    # 这里可以添加其他启动时的初始化操作
    # 例如：加载缓存、预热模型、检查外部服务等

    log.info("🎉 应用启动完成")

    yield  # 应用运行中...

    # 关闭时执行
    log.info("🛑 应用关闭中...")
    try:
        # 关闭数据库连接
        await close_db()
        log.info("✅ 数据库连接已关闭")

        # 这里可以添加其他清理操作
        # 例如：清理缓存、保存状态等

        log.info("👋 应用已安全关闭")
    except asyncio.CancelledError:
        # 捕获并忽略关闭时的取消错误，避免日志噪音
        log.info("👋 应用因中断而关闭")
    except Exception as e:
        # 捕获其他可能的异常，避免关闭时崩溃
        log.error(f"应用关闭时发生错误: {e}", exc_info=True)


def create_app() -> FastAPI:
    """
    应用工厂函数
    """

    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,  # 使用生命周期管理
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        swagger_ui_parameters={
            "docExpansion": "none",  # 默认折叠所有接口
            "defaultModelsExpandDepth": -1,  # 隐藏 Schemas 区域
        },
    )

    # 设置中间件
    setup_middleware(app)

    # 设置异常处理器
    setup_exception_handlers(app)

    # 注册路由
    app.include_router(api_router, prefix=settings.api_prefix)

    return app

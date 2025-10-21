import sys
import logging
from pathlib import Path

from loguru import logger
from app.core.config import settings


# --- 全局日志配置 ---
def setup_logging():
    """
    配置并初始化 Loguru 日志系统，并拦截标准库日志。
    """

    # --- 关键修改：拦截标准库日志 ---
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # 设置标准库的日志级别为 INFO，并使用我们的拦截处理器
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    # 设置 uvicorn 等第三方库的日志级别
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]

    # 1. 移除 Loguru 默认的处理器
    logger.remove()

    # 2. 添加控制台日志处理器
    logger.add(
        sys.stdout,
        # --- 关键修改：使用 {name} 替代 {module} 来获取完整路径 ---
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> | <level>{message}</level>",
        level=settings.log_level.upper(),
        colorize=True,
        # 过滤掉 uvicorn 的 access 日志，避免重复
        filter=lambda record: "uvicorn.access" not in record["name"]
    )

    # 3. 添加文件日志处理器
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "app.log",
        # --- 文件日志格式也同步修改 ---
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
    )


# --- 全局日志快捷方式 ---
log = logger

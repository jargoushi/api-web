import sys

from loguru import logger

from app.core.config import settings

# 移除默认的控制台处理器
logger.remove()

# 添加控制台输出处理器（带颜色）
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<level>{message}</level>",
    level=settings.log_level
)

# # 创建logs目录（如果不存在）
# log_dir = Path("logs")
# log_dir.mkdir(exist_ok=True)
#
# # 添加文件输出处理器（按日期分割）
# logger.add(
#     log_dir / "app_{time:YYYY-MM-DD}.log",
#     format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} | {message}",
#     level="DEBUG",
#     rotation="00:00",
#     retention="30 days",
#     compression="zip",
#     encoding="utf-8"
# )

#
# # 添加错误日志单独文件
# logger.add(
#     log_dir / "error_{time:YYYY-MM-DD}.log",
#     format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {module}:{function}:{line} | {message}",
#     level="ERROR",
#     rotation="00:00",
#     retention="30 days",
#     compression="zip",
#     encoding="utf-8"
# )


log = logger

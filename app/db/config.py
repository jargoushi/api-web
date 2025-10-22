from pathlib import Path

from tortoise import Tortoise

from app.core.config import settings
from app.core.logging import log


def ensure_database_directory():
    """确保数据库文件的目录存在"""
    db_url = settings.database_url

    if not db_url.startswith("sqlite://"):
        return  # 只处理 SQLite

    # 提取文件路径
    file_path = db_url.replace("sqlite://", "").lstrip("/")

    # 获取目录部分
    db_dir = Path(file_path).parent

    # 如果目录不是当前目录，则创建
    if db_dir != Path("."):
        db_dir.mkdir(parents=True, exist_ok=True)


# 数据库配置
TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """初始化数据库"""
    # 确保数据库目录存在
    ensure_database_directory()

    await Tortoise.init(config=TORTOISE_ORM)

    # 生成数据库表（仅开发环境）
    if settings.debug:
        await Tortoise.generate_schemas()


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()

from tortoise import Tortoise

from app.core.config import settings


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
    await Tortoise.init(config=TORTOISE_ORM)

    # 生成数据库表（仅开发环境）
    # if settings.debug:
    #     await Tortoise.generate_schemas()


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()

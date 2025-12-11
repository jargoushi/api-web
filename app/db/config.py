from pathlib import Path
import pkgutil

from tortoise import Tortoise

from app.core.config import settings


def _discover_model_modules() -> list[str]:
    """
    自动发现 app/models 目录下所有模型模块

    扫描规则：
    - 遍历 app/models 下的所有子目录（如 account, monitor）
    - 每个子目录下的 .py 文件（排除 __init__.py）都视为模型模块

    Returns:
        模型模块路径列表，如 ["app.models.account.user", "app.models.monitor.task"]
    """
    models_dir = Path(__file__).parent.parent / "models"
    modules = []

    for sub_dir in models_dir.iterdir():
        if sub_dir.is_dir() and not sub_dir.name.startswith("_"):
            for py_file in sub_dir.glob("*.py"):
                if py_file.stem != "__init__":
                    module_path = f"app.models.{sub_dir.name}.{py_file.stem}"
                    modules.append(module_path)

    return modules


# 数据库配置
TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": _discover_model_modules(),
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

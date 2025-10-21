from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 确定项目根目录（从当前文件向上两级）
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # 自动从 .env 文件加载配置
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.env',
                                      env_file_encoding='utf-8',
                                      # 如果 .env 文件不存在，会抛出错误而不是静默忽略
                                      env_file_required=True,
                                      # 环境变量名不区分大小写
                                      case_sensitive=False
                                      )

    # 数据库配置
    database_url: str

    # 应用配置
    app_name: str = "FastAPI + TortoiseORM Demo"
    debug: bool = True
    description: str = "一个使用 FastAPI 和 TortoiseORM 构建的示例 API"
    version: str = "1.0.0"

    # 日志级别配置 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_level: str = "INFO"


# 创建一个全局设置实例
settings = Settings()

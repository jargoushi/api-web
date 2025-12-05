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
    log_level: str = "DEBUG"

    # 添加比特浏览器配置
    BIT_BROWSER_BASE_URL: str = "http://127.0.0.1:54345"  # 默认本地地址

    # 激活码配置
    ACTIVATION_GRACE_HOURS: int = 1  # 激活码默认宽裕时间（小时）

    # JWT配置
    JWT_SECRET_KEY: str  # JWT密钥，生产环境必须设置
    JWT_ALGORITHM: str = "HS256"  # JWT算法
    JWT_EXPIRE_MINUTES: int = 1440  # Token有效期（分钟），默认24小时

    # API配置
    API_PREFIX: str = "/api"  # API路由前缀

    # 认证配置
    ENABLE_AUTH: bool = True  # 是否启用认证中间件
    TOKEN_REFRESH_THRESHOLD: int = 60  # Token刷新阈值（分钟），剩余时间少于阈值时建议刷新

    # 视频生成配置
    JIANYING_DRAFT_FOLDER: str = ""  # 剪映草稿文件夹路径，例如：C:/Users/用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft
    MATERIAL_BASE_PATH: str = "./materials"  # 素材文件基础路径


# 创建一个全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取设置实例的便捷函数"""
    return settings

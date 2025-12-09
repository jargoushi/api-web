# FastAPI + TortoiseORM + MySQL 项目

基于 FastAPI 和 TortoiseORM 构建的 Web API 项目，使用 MySQL 作为数据库。

## 🆕 新功能：地理视频生成系统

基于 GeoJSON 地图数据和方言音频，自动生成带运镜效果的地理信息视频。

**快速开始:**

```bash
# 安装依赖
uv sync

# 快速启动
python quick_start.py

# 或运行测试
python test_geo_video.py
```

**详细文档:** 查看 [GEO_VIDEO_GUIDE.md](GEO_VIDEO_GUIDE.md)

## 技术栈

- **FastAPI** - 现代、高性能的 Web 框架
- **TortoiseORM** - 异步 ORM 框架
- **MySQL** - 关系型数据库
- **Pydantic** - 数据验证和设置管理
- **JWT** - 用户认证
- **Uvicorn** - ASGI 服务器

## 快速开始

### 1. 环境要求

- Python 3.9+
- MySQL 8.0+
- uv (Python 包管理器)

### 2. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync
```

### 3. 配置数据库

编辑 `.env` 文件，配置 MySQL 连接：

```env
DATABASE_URL="mysql://root:password@localhost:3306/fastapi_db"
```

### 4. 初始化数据库

```bash
# 使用 MySQL 命令行执行初始化脚本
mysql -u root -p < app/sql/init_database.sql
```

或手动执行：

```sql
CREATE DATABASE fastapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE fastapi_db;
SOURCE app/sql/01_activation_codes.sql;
SOURCE app/sql/02_users.sql;
SOURCE app/sql/03_user_sessions.sql;
```

### 5. 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload

# 或使用启动脚本
python app/run.py
```

访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
.
├── app/
│   ├── core/           # 核心配置（配置、日志、中间件等）
│   ├── db/             # 数据库配置
│   ├── enums/          # 枚举类型
│   ├── models/         # 数据模型
│   ├── routers/        # API 路由
│   ├── schemas/        # Pydantic 模式
│   ├── services/       # 业务逻辑
│   ├── sql/            # SQL 建表语句
│   ├── util/           # 工具函数
│   └── main.py         # 应用入口
├── .env                # 环境变量配置
├── pyproject.toml      # 项目依赖
└── README.md           # 项目说明
```

## 数据库表

- `activation_codes` - 激活码表
- `user` - 用户表
- `user_sessions` - 用户会话表

详细的表结构请查看 `app/sql/` 目录下的 SQL 文件。

## 配置说明

主要配置项在 `.env` 文件中：

```env
# 数据库配置
DATABASE_URL="mysql://root:password@localhost:3306/fastapi_db"

# 日志级别
LOG_LEVEL=DEBUG

# JWT 配置
JWT_SECRET_KEY="your-secret-key"
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 认证配置
ENABLE_AUTH=true
TOKEN_REFRESH_THRESHOLD=60

# 激活码配置
ACTIVATION_GRACE_HOURS=2
```

## 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black app/
```

### 类型检查

```bash
mypy app/
```

## 迁移指南

如果从 SQLite 迁移到 MySQL，请参考 [MIGRATION_TO_MYSQL.md](MIGRATION_TO_MYSQL.md)。

## API 文档

启动应用后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 许可证

MIT

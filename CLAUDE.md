# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 FastAPI 和 TortoiseORM 构建的 Python Web API 项目，主要功能包括用户管理、激活码管理和浏览器自动化操作。

## 常用命令

### 开发环境运行
```bash
# 激活虚拟环境（如果需要）
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 启动开发服务器
python app/run.py
# 或使用 uvicorn 直接启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 代码质量检查
```bash
# 代码格式化
black app/

# 代码风格检查
flake8 app/

# 类型检查
mypy app/
```

### 测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest app/test/test_playwright.py

# 运行测试并显示覆盖率
pytest --cov=app
```

### 数据库操作
```bash
# 数据库迁移（如果使用了 aerich）
# aerich init -t app.db.config.TORTOISE_ORM
# aerich init-db
# aerich migrate
# aerich upgrade
```

## 项目架构

### 目录结构
```
api-web/
├── app/
│   ├── core/           # 核心配置和工具
│   │   ├── config.py   # 应用配置
│   │   ├── events.py   # 应用生命周期管理
│   │   ├── middleware.py # 中间件
│   │   └── exceptions.py # 异常处理
│   ├── db/             # 数据库配置
│   ├── models/         # TortoiseORM 数据模型
│   ├── schemas/        # Pydantic 数据验证模式
│   ├── routers/        # API 路由
│   ├── services/       # 业务逻辑层
│   ├── util/           # 工具函数
│   ├── enums/          # 枚举类
│   ├── data/           # 数据存储目录
│   ├── logs/           # 日志文件
│   ├── test/           # 测试文件
│   ├── main.py         # 应用入口
│   └── run.py          # 开发服务器启动脚本
├── .env                # 环境变量配置
└── pyproject.toml      # 项目配置和依赖
```

### 关键架构模式

1. **应用工厂模式**: `app/core/events.py:create_app()` 负责创建和配置 FastAPI 应用实例
2. **生命周期管理**: 使用 `@asynccontextmanager` 管理应用启动和关闭时的操作
3. **分层架构**:
   - `routers/`: API 路由层，处理 HTTP 请求
   - `services/`: 业务逻辑层，包含复杂的业务处理
   - `models/`: 数据模型层，定义数据库表结构
   - `schemas/`: 数据验证层，定义请求/响应格式

### 主要技术栈

- **Web框架**: FastAPI
- **ORM**: TortoiseORM
- **数据库**: SQLite (开发) / MySQL (生产)
- **异步支持**: asyncio, aiomysql, aiosqlite
- **认证**: python-jose, bcrypt
- **自动化**: Playwright (浏览器自动化)
- **日志**: loguru
- **配置管理**: pydantic-settings
- **测试**: pytest, pytest-asyncio
- **代码质量**: black, flake8, mypy

### 核心模块

1. **激活码模块** (`models/activation_code.py`, `routers/activation_code_router.py`)
   - 管理软件激活码的生成、验证和使用

2. **浏览器自动化模块** (`routers/browser_router.py`, `services/browser_service.py`)
   - 集成 Playwright 进行浏览器自动化操作
   - 支持比特浏览器 API 集成

3. **用户管理模块** (`models/user.py`, `routers/user_router.py`)
   - 用户注册、登录和权限管理

### 配置管理

- 使用 `pydantic-settings` 从 `.env` 文件加载配置
- 主要配置项：
  - `DATABASE_URL`: 数据库连接字符串
  - `LOG_LEVEL`: 日志级别
  - `BIT_BROWSER_BASE_URL`: 比特浏览器 API 地址
  - `ACTIVATION_GRACE_HOURS`: 激活码宽裕时间

### 开发注意事项

1. **环境配置**: 确保 `.env` 文件存在并配置正确的数据库连接
2. **虚拟环境**: 推荐使用 uv 进行依赖管理，已配置 `.venv` 虚拟环境
3. **数据库**: 默认使用 SQLite，数据库文件存储在 `app/data/db.sqlite3`
4. **日志**: 日志文件存储在 `app/logs/` 目录
5. **异步编程**: 所有数据库操作和 API 处理都使用 async/await 模式
6. **类型注解**: 使用 mypy 进行类型检查，避免使用 `Any` 类型
7. **中文注释**: 所有代码注释和文档都使用中文
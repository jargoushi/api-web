# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 FastAPI 和 TortoiseORM 构建的 Python Web API 项目，主要功能包括用户管理、激活码管理和浏览器自动化操作。项目采用异步架构，支持 SQLite 和 MySQL 数据库，集成了比特浏览器 API 用于自动化操作。

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
pytest app/test/test_auth.py
pytest app/test/test_activation_code.py
pytest app/test/test_user.py

# 运行测试并显示覆盖率
pytest --cov=app
```

## 项目架构

### 核心架构模式

1. **应用工厂模式**: `app/core/events.py:create_app()` 负责创建和配置 FastAPI 应用实例
2. **生命周期管理**: 使用 `@asynccontextmanager` 管理应用启动和关闭时的操作
3. **分层架构**:
   - `routers/`: API 路由层，处理 HTTP 请求
   - `services/`: 业务逻辑层，包含复杂的业务处理
   - `models/`: 数据模型层，定义数据库表结构
   - `schemas/`: 数据验证层，定义请求/响应格式

### 路由架构

项目使用模块化路由设计，通过 `app/routers/__init__.py` 统一管理：

- **认证路由** (`/api/auth`): 登录、注册等无需认证的接口
- **激活码路由** (`/api/activation`): 激活码管理相关接口
- **系统路由** (`/api/index`): 系统状态等基础接口
- **用户管理路由** (`/api/users`): 需要认证的用户管理接口
- **浏览器路由** (`/api/browser`): 需要认证的比特浏览器操作接口

### 数据库层设计

- **配置**: `app/db/config.py` 使用 TortoiseORM 配置数据库连接
- **模型**:
  - `User`: 用户基础信息，包含用户名、密码、激活码等字段
  - `ActivationCode`: 激活码管理，支持分发、激活、过期检查等状态
  - `UserSession`: 用户会话管理（通过 `models/user_session.py` 定义）
- **自动建表**: 开发环境下自动生成数据库表结构

### 核心业务模块

1. **激活码系统**
   - 支持多种激活码类型（通过枚举定义）
   - 完整的生命周期管理：创建 → 分发 → 激活 → 过期
   - 灵活的过期时间计算，支持宽限时间配置

2. **认证与授权**
   - JWT Token 认证机制
   - 密码使用 bcrypt 加密
   - 支持 Token 刷新机制
   - 中间件控制的路由保护

3. **浏览器自动化**
   - 集成比特浏览器 API
   - 支持浏览器批量操作和管理
   - 异步 HTTP 请求处理

### 主要技术栈

- **Web框架**: FastAPI 0.119+
- **ORM**: TortoiseORM 0.25+
- **数据库**: SQLite (开发) / MySQL (生产)
- **异步支持**: asyncio, aiomysql, aiosqlite
- **认证**: python-jose[cryptography], bcrypt
- **自动化**: Playwright 1.55+
- **HTTP客户端**: httpx
- **日志**: loguru
- **配置管理**: pydantic-settings
- **测试**: pytest, pytest-asyncio
- **代码质量**: black, flake8, mypy

### 配置管理

使用 `pydantic-settings` 从 `.env` 文件加载配置，主要配置项：

- `DATABASE_URL`: 数据库连接字符串（SQLite 或 MySQL）
- `LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `BIT_BROWSER_BASE_URL`: 比特浏览器 API 地址（默认：http://127.0.0.1:54345）
- `ACTIVATION_GRACE_HOURS`: 激活码宽裕时间（小时）
- `JWT_SECRET_KEY`: JWT 签名密钥（生产环境必须设置）
- `JWT_ALGORITHM`: JWT 算法（默认 HS256）
- `JWT_EXPIRE_MINUTES`: Token 有效期（分钟）
- `ENABLE_AUTH`: 是否启用认证中间件
- `TOKEN_REFRESH_THRESHOLD`: Token 刷新阈值（分钟）

### 开发注意事项

1. **环境配置**:
   - 确保 `.env` 文件存在并配置正确的数据库连接
   - 生产环境必须设置强密钥的 `JWT_SECRET_KEY`

2. **虚拟环境**:
   - 使用 uv 进行依赖管理，已配置 `.venv` 虚拟环境
   - 项目依赖在 `pyproject.toml` 中定义

3. **数据库**:
   - 默认使用 SQLite，数据库文件存储在 `app/data/db.sqlite3`
   - 开发环境自动建表，生产环境建议使用数据库迁移工具

4. **文件存储**:
   - 数据库文件：`app/data/` 目录
   - 日志文件：`app/logs/` 目录
   - 测试数据：`app/test/data/` 目录

5. **编程规范**:
   - 所有数据库操作和 API 处理都使用 async/await 模式
   - 使用 mypy 进行类型检查，避免使用 `Any` 类型
   - 所有代码注释和文档都使用中文
   - 遵循 PEP 8 代码风格规范
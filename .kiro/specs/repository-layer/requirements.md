# 需求文档 - Repository 层架构重构

## 简介

当前项目采用 `Router -> Service -> Model` 三层架构，随着业务复杂度增加，Service 层承担了过多职责（业务编排 + 数据访问），导致代码臃肿、难以测试和维护。本需求旨在引入 Repository（仓储）层，将数据访问逻辑从业务逻辑中剥离，形成 `Router -> Service -> Repository -> Model` 四层架构。

## 术语表

- **Repository（仓储层）**: 数据访问层，封装所有与数据库交互的操作，提供语义化的数据访问接口
- **Service（服务层）**: 业务逻辑层，负责业务流程编排和业务规则实现
- **Model（模型层）**: 数据模型层，定义数据库表结构和基本属性
- **Router（路由层）**: API 接口层，负责请求参数解析和响应格式化
- **ORM**: 对象关系映射，本项目使用 Tortoise ORM
- **充血模型**: 模型中包含业务方法的设计模式
- **贫血模型**: 模型中只包含数据字段的设计模式

## 需求

### 需求 1

**用户故事:** 作为开发者，我希望将数据访问逻辑从 Service 层剥离到 Repository 层，以便 Service 层专注于业务编排。

#### 验收标准

1. WHEN 创建 Repository 类 THEN 系统应将所有 ORM 查询操作（filter、create、get_or_none 等）封装在 Repository 中
2. WHEN Service 需要访问数据 THEN 系统应通过调用 Repository 的方法而不是直接调用 ORM
3. WHEN Repository 方法被调用 THEN 系统应返回 Model 实例或查询结果
4. WHEN 定义 Repository 接口 THEN 系统应提供语义化的方法名（如 find_unused_codes、create_code）而不是暴露底层 ORM 细节

### 需求 2

**用户故事:** 作为开发者，我希望 Service 层只包含业务逻辑，不包含任何数据库查询代码，以提高代码可读性和可测试性。

#### 验收标准

1. WHEN Service 方法执行业务逻辑 THEN 系统应通过 Repository 获取和保存数据
2. WHEN Service 需要复杂查询 THEN 系统应调用 Repository 提供的专门查询方法
3. WHEN Service 执行业务流程 THEN 系统应专注于业务规则判断、状态流转、异常处理等逻辑
4. WHEN 查看 Service 代码 THEN 系统不应包含任何 `Model.filter()`、`Model.create()` 等 ORM 调用

### 需求 3

**用户故事:** 作为开发者，我希望 Repository 层提供统一的基类，以便所有 Repository 共享通用的 CRUD 操作。

#### 验收标准

1. WHEN 创建 BaseRepository THEN 系统应提供通用的 CRUD 方法（create、get_by_id、update、delete、find_all）
2. WHEN 具体 Repository 继承 BaseRepository THEN 系统应自动获得基础 CRUD 能力
3. WHEN 需要特殊查询 THEN 系统应在具体 Repository 中添加专门的查询方法
4. WHEN BaseRepository 方法被调用 THEN 系统应正确处理泛型类型，返回对应的 Model 实例

### 需求 4

**用户故事:** 作为开发者，我希望 Model 层保持简洁，只包含数据定义和简单的属性方法，复杂的业务逻辑应在 Service 层实现。

#### 验收标准

1. WHEN 定义 Model THEN 系统应只包含字段定义、@property 属性、简单的计算方法
2. WHEN Model 需要状态变更方法 THEN 系统应保留简单的状态设置方法（如 distribute、activate）
3. WHEN 业务逻辑复杂 THEN 系统应将逻辑移至 Service 层而不是放在 Model 中
4. WHEN Model 方法被调用 THEN 系统应只修改自身属性，不应包含数据库查询或其他 Model 的操作

### 需求 5

**用户故事:** 作为开发者，我希望重构后的代码易于测试，Service 层可以通过 Mock Repository 进行单元测试。

#### 验收标准

1. WHEN 编写 Service 单元测试 THEN 系统应能够 Mock Repository 而不依赖真实数据库
2. WHEN 编写 Repository 测试 THEN 系统应能够独立测试数据访问逻辑
3. WHEN 测试业务逻辑 THEN 系统应能够专注于业务规则验证而不是数据库操作
4. WHEN 运行测试 THEN 系统应提供清晰的测试边界（单元测试 vs 集成测试）

### 需求 6

**用户故事:** 作为开发者，我希望按照统一的规范重构现有的 Service 代码，以激活码模块为示例进行改造。

#### 验收标准

1. WHEN 重构 ActivationCodeService THEN 系统应将所有数据库操作移至 ActivationCodeRepository
2. WHEN ActivationCodeRepository 被创建 THEN 系统应提供 find_unused_codes、find_by_code、create_code、update_code 等方法
3. WHEN ActivationCodeService 调用 Repository THEN 系统应保持原有的业务逻辑不变
4. WHEN 重构完成 THEN 系统应确保所有现有的 API 接口功能正常，不影响现有业务

### 需求 7

**用户故事:** 作为开发者，我希望有清晰的目录结构来组织 Repository 代码，便于后续扩展。

#### 验收标准

1. WHEN 创建 Repository 目录 THEN 系统应在 `app/repositories` 下按模块组织（account、monitor）
2. WHEN 创建 BaseRepository THEN 系统应放置在 `app/repositories/base.py`
3. WHEN 创建具体 Repository THEN 系统应放置在对应模块目录下（如 `app/repositories/account/activation_repository.py`）
4. WHEN 导出 Repository THEN 系统应在 `__init__.py` 中统一导出，便于导入使用

### 需求 8

**用户故事:** 作为开发者，我希望有完整的文档说明新架构的设计理念、使用方式和最佳实践。

#### 验收标准

1. WHEN 查看架构文档 THEN 系统应清晰说明四层架构的职责划分
2. WHEN 查看使用示例 THEN 系统应提供 Repository 和 Service 的代码示例
3. WHEN 新增功能 THEN 系统应提供开发指南，说明如何创建新的 Repository 和 Service
4. WHEN 遇到问题 THEN 系统应提供常见问题和解决方案的文档

## 非功能性需求

### 性能要求

1. Repository 层不应引入额外的性能开销
2. 查询优化应在 Repository 层实现（如预加载关联数据）

### 兼容性要求

1. 重构应保持向后兼容，不影响现有 API 接口
2. 现有的测试用例应继续通过

### 可维护性要求

1. 代码结构清晰，职责明确
2. 新增功能时遵循统一的开发模式
3. 代码注释完整，便于理解

## 约束条件

1. 使用 Tortoise ORM 作为底层 ORM 框架
2. 保持 Python 类型提示的完整性
3. 遵循项目现有的代码风格和命名规范
4. 重构应分阶段进行，先完成激活码模块的示例改造

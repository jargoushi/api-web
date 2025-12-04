# Model 和 Service 层重构总结

## 重构目标

完成以下两个优先级任务：

1. **优先级 1（高）**: 移除 Model 中的业务方法 → Service 层
2. **优先级 3（中）**: 提取工具类，清理 Service 层

## 重构内容

### 1. 创建工具类

#### 新增文件：`app/util/activation_code_generator.py`

- 提取激活码生成逻辑到独立的工具类
- 使用静态方法 `generate()` 生成激活码
- 遵循单一职责原则，专注于激活码生成

**优势：**

- 代码复用性更强
- 易于单元测试
- Service 层更简洁

### 2. 重构 ActivationCode Model

#### 修改文件：`app/models/account/activation_code.py`

**移除的业务方法：**

- `distribute()` - 分发激活码
- `activate()` - 激活激活码
- `invalidate()` - 作废激活码
- `calculate_expire_time()` - 计算过期时间

**保留的内容：**

- 字段定义
- 简单的属性访问器（`@property`）
  - `type_enum` - 获取类型枚举
  - `type_name` - 获取类型名称
  - `status_enum` - 获取状态枚举
  - `status_name` - 获取状态名称
  - `is_expired` - 检查是否过期（只读属性）

**设计原则：**

- Model 只作为数据容器
- 只包含简单的计算属性，不包含状态变更逻辑

### 3. 重构 ActivationCodeService

#### 修改文件：`app/services/account/activation_service.py`

**主要变更：**

1. **使用工具类生成激活码**

   ```python
   # 之前：在 Service 中实现生成逻辑
   def generate_activation_code(self) -> str:
       # 复杂的生成逻辑...

   # 之后：使用工具类
   self.code_generator = ActivationCodeGenerator()
   code = self.code_generator.generate()
   ```

2. **业务逻辑从 Model 移到 Service**

   ```python
   # 之前：调用 Model 方法
   code.distribute()
   code.activate()
   code.invalidate()

   # 之后：在 Service 中实现业务逻辑
   code.distributed_at = get_utc_now()
   code.status = ActivationCodeStatusEnum.DISTRIBUTED.code
   await self.repository.update(code)
   ```

3. **新增辅助方法**
   - `_calculate_expire_time()` - 计算过期时间（从 Model 移过来）

**优势：**

- 业务逻辑集中在 Service 层
- 更容易进行单元测试和 Mock
- Service 层代码更清晰

### 4. 重构 UserSession Model

#### 修改文件：`app/models/account/user_session.py`

**移除的类方法：**

- `create_session()` - 创建会话
- `get_active_session()` - 获取活跃会话
- `get_session_by_token()` - 根据 token 获取会话
- `revoke_session()` - 撤销会话
- `revoke_user_sessions()` - 撤销用户所有会话
- `cleanup_expired_sessions()` - 清理过期会话
- `extend_session()` - 延长会话时间

**移除的实例方法：**

- `extend_session()` - 延长会话时间（改为 Service 方法）

**保留的内容：**

- 字段定义
- 简单的属性访问器
  - `is_expired` - 检查是否过期
  - `should_cleanup` - 检查是否应该清理
- `get_device_info()` - 获取设备信息（纯数据转换，无状态变更）

### 5. 创建 UserSessionService

#### 新增文件：`app/services/account/user_session_service.py`

**实现的业务方法：**

- `create_session()` - 创建会话（包含单设备登录逻辑）
- `get_active_session()` - 获取活跃会话
- `get_session_by_token()` - 根据 token 获取会话
- `revoke_session()` - 撤销会话
- `revoke_user_sessions()` - 撤销用户所有会话
- `cleanup_expired_sessions()` - 清理过期会话
- `extend_session()` - 延长会话时间

**设计特点：**

- 通过 Repository 进行数据访问
- 包含完整的业务逻辑和验证
- 支持依赖注入，便于测试

### 6. 更新 AuthService

#### 修改文件：`app/services/account/auth_service.py`

**主要变更：**

- 使用 `UserSessionService` 替代直接操作 `UserSession` Model
- 简化登录、注销等方法的实现
- 移除对 `UserSessionRepository` 的直接依赖

**示例：**

```python
# 之前：直接使用 Repository
await self.session_repository.delete_user_sessions(user.id)
await self.session_repository.create(...)

# 之后：使用 Service
await self.session_service.create_session(...)
```

### 7. 更新中间件

#### 修改文件：`app/core/middleware.py`

**主要变更：**

- 使用 `UserSessionService` 替代 `UserSession` 类方法
- 在 `_validate_session()` 方法中使用 Service 层

### 8. 更新测试文件

#### 修改文件：`app/test/test_auth.py`

**主要变更：**

- 在测试类中添加 `session_service` 实例
- 所有 `UserSession.get_session_by_token()` 调用改为 `self.session_service.get_session_by_token()`

## 架构改进

### 之前的架构问题

1. **Model 包含业务逻辑**

   - `ActivationCode.distribute()`, `activate()`, `invalidate()`
   - `UserSession.create_session()`, `revoke_session()` 等
   - 违反单一职责原则

2. **Service 层混杂工具方法**

   - 激活码生成逻辑在 Service 中
   - 难以复用和测试

3. **职责不清晰**
   - Model 既是数据容器又是业务逻辑处理器
   - Service 层和 Model 层职责混淆

### 重构后的架构优势

1. **清晰的分层架构**

   ```
   Controller → Service → Repository → Model
                    ↓
                 Utils (工具类)
   ```

2. **Model 层职责明确**

   - 只作为数据容器
   - 只包含简单的计算属性（只读）
   - 不包含状态变更逻辑

3. **Service 层职责明确**

   - 业务逻辑编排
   - 状态变更管理
   - 通过 Repository 访问数据

4. **工具类独立**
   - 可复用的工具方法
   - 易于单元测试
   - 无状态设计

## 代码质量提升

### 1. 可测试性

- Service 层可以轻松 Mock Repository 和工具类
- Model 层不再包含复杂逻辑，测试更简单
- 工具类可以独立测试

### 2. 可维护性

- 职责清晰，修改影响范围小
- 业务逻辑集中在 Service 层
- 代码结构更符合 SOLID 原则

### 3. 可扩展性

- 新增业务逻辑只需修改 Service 层
- Model 层保持稳定
- 工具类可以轻松扩展

## 影响范围

### 修改的文件

1. `app/models/account/activation_code.py` - 移除业务方法
2. `app/models/account/user_session.py` - 移除类方法和业务方法
3. `app/services/account/activation_service.py` - 接管业务逻辑
4. `app/services/account/auth_service.py` - 使用 UserSessionService
5. `app/core/middleware.py` - 使用 UserSessionService
6. `app/test/test_auth.py` - 更新测试代码

### 新增的文件

1. `app/util/activation_code_generator.py` - 激活码生成工具类
2. `app/services/account/user_session_service.py` - 用户会话服务

## 验证结果

所有修改的文件通过了语法检查，无诊断错误：

- ✅ `app/models/account/activation_code.py`
- ✅ `app/models/account/user_session.py`
- ✅ `app/services/account/activation_service.py`
- ✅ `app/services/account/user_session_service.py`
- ✅ `app/services/account/auth_service.py`
- ✅ `app/core/middleware.py`
- ✅ `app/util/activation_code_generator.py`

## 后续建议

### 已完成的优先级任务

- ✅ 优先级 1（高）: 移除 Model 中的业务方法 → Service 层
- ✅ 优先级 3（中）: 提取工具类，清理 Service 层

### 待完成的优先级任务

- ⏳ 优先级 2（中）: 引入查询对象模式，简化 Repository 方法签名
- ⏳ 优先级 4（低）: 在具体 Repository 中提供类型安全的包装方法

### 其他改进建议

1. 考虑为其他 Model（如 `User`, `MonitorConfig` 等）应用相同的重构模式
2. 为新增的 Service 和工具类编写单元测试
3. 更新 API 文档，反映架构变更

## 总结

本次重构成功实现了：

1. **Model 层纯净化** - 只作为数据容器，不包含业务逻辑
2. **Service 层职责明确** - 集中管理业务逻辑和状态变更
3. **工具类独立** - 提取可复用的工具方法
4. **代码质量提升** - 更易测试、维护和扩展

重构遵循了 SOLID 原则，特别是单一职责原则（SRP）和依赖倒置原则（DIP），使代码结构更加清晰和健壮。

## 补充改进：Repository 业务方法封装

### 问题识别

Service 层直接调用 BaseRepository 的通用方法（`create()`, `update()`, `delete()`），存在以下问题：

- 缺少类型安全，IDE 无法提供完整的类型提示
- 缺少业务语义，代码可读性差
- 数据访问逻辑分散在 Service 层

### 解决方案

在具体的 Repository 中添加业务方法，封装数据访问逻辑。

#### ActivationCodeRepository 新增方法

```python
async def create_activation_code(
    self,
    activation_code: str,
    type_code: int,
    status: int,
    expire_time: Optional[datetime] = None,
    activated_at: Optional[datetime] = None
) -> ActivationCode:
    """创建激活码"""
    return await self.create(
        activation_code=activation_code,
        type=type_code,
        status=status,
        expire_time=expire_time,
        activated_at=activated_at
    )

async def update_activation_code(self, code: ActivationCode) -> ActivationCode:
    """更新激活码"""
    await code.save()
    return code
```

#### UserSessionRepository 新增方法

```python
async def create_session(
    self,
    user_id: int,
    token: str,
    device_id: str,
    device_name: Optional[str],
    user_agent: Optional[str],
    ip_address: str,
    expires_at: datetime,
    is_active: bool = True
) -> UserSession:
    """创建用户会话"""
    return await self.create(...)

async def update_session(self, session: UserSession) -> UserSession:
    """更新用户会话"""
    await session.save()
    return session

async def delete_session(self, session: UserSession) -> bool:
    """删除用户会话"""
    return await self.delete(session)
```

#### UserRepository 新增方法

```python
async def create_user(
    self,
    username: str,
    password: str,
    activation_code: str,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> User:
    """创建用户"""
    return await self.create(...)

async def update_user(self, user: User, **update_data) -> User:
    """更新用户信息"""
    return await self.update(user, **update_data)
```

### Service 层调用示例

**之前（直接调用 BaseRepository 方法）：**

```python
# ActivationCodeService
await self.repository.create(
    activation_code=code,
    expire_time=None,
    type=item.type,
    status=ActivationCodeStatusEnum.UNUSED.code,
    activated_at=None
)

# UserSessionService
await self.repository.create(
    user_id=user_id,
    token=token,
    device_id=device_id,
    ...
)
```

**之后（调用业务方法）：**

```python
# ActivationCodeService
await self.repository.create_activation_code(
    activation_code=code,
    type_code=item.type,
    status=ActivationCodeStatusEnum.UNUSED.code,
    expire_time=None,
    activated_at=None
)

# UserSessionService
await self.repository.create_session(
    user_id=user_id,
    token=token,
    device_id=device_id,
    ...
)
```

### 改进优势

1. **类型安全**

   - 明确的参数类型，IDE 可以提供完整的类型提示
   - 编译时就能发现参数错误，而不是运行时

2. **业务语义清晰**

   - `create_activation_code()` 比 `create()` 更清楚表达业务意图
   - 方法名直接反映业务操作

3. **封装性更好**

   - 数据访问逻辑完全封装在 Repository 层
   - Service 层不需要知道底层实现细节

4. **可维护性提升**

   - 修改数据访问逻辑只需修改 Repository，不影响 Service 层
   - 便于统一处理数据验证、日志记录等横切关注点

5. **便于测试**
   - 可以轻松 Mock Repository 的业务方法
   - 测试更加聚焦于业务逻辑

### 架构层次更清晰

```
Controller (路由层)
    ↓ 调用
Service (业务逻辑层)
    ↓ 调用业务方法（不直接调用 BaseRepository 方法）
Repository (数据访问层)
    ├─ 业务方法（封装具体操作）
    └─ 继承 BaseRepository（通用 CRUD）
        ↓ 操作
Model (数据模型层) - 纯数据容器
```

### 修改的文件

**Repository 层：**

- `app/repositories/account/activation_repository.py` - 新增 2 个业务方法
- `app/repositories/account/user_session_repository.py` - 新增 3 个业务方法
- `app/repositories/account/user_repository.py` - 新增 2 个业务方法

**Service 层：**

- `app/services/account/activation_service.py` - 更新为调用业务方法
- `app/services/account/user_session_service.py` - 更新为调用业务方法
- `app/services/account/user_service.py` - 更新为调用业务方法

### 验证结果

所有修改的文件通过了语法检查，无诊断错误：

- ✅ `app/repositories/account/activation_repository.py`
- ✅ `app/repositories/account/user_session_repository.py`
- ✅ `app/repositories/account/user_repository.py`
- ✅ `app/services/account/activation_service.py`
- ✅ `app/services/account/user_session_service.py`
- ✅ `app/services/account/user_service.py`

## 最终总结

本次重构成功实现了：

1. **Model 层纯净化** - 只作为数据容器，不包含业务逻辑
2. **Service 层职责明确** - 集中管理业务逻辑和状态变更
3. **Repository 层封装完善** - 提供类型安全的业务方法，不暴露 BaseRepository 细节
4. **工具类独立** - 提取可复用的工具方法
5. **代码质量全面提升** - 更易测试、维护和扩展

重构遵循了 SOLID 原则：

- **单一职责原则（SRP）** - 每层职责清晰
- **开闭原则（OCP）** - 易于扩展，无需修改现有代码
- **里氏替换原则（LSP）** - Repository 可以轻松替换和 Mock
- **接口隔离原则（ISP）** - Service 只依赖需要的业务方法
- **依赖倒置原则（DIP）** - 依赖抽象而非具体实现

代码结构更加清晰、健壮，符合企业级应用的最佳实践。

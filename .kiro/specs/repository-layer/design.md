# 设计文档 - Repository 层架构重构

## 概述

本设计文档描述了如何在现有的三层架构基础上引入 Repository（仓储）层，形成清晰的四层架构：`Router -> Service -> Repository -> Model`。通过职责分离，提高代码的可维护性、可测试性和可扩展性。

## 架构设计

### 四层架构职责划分

```
┌─────────────────────────────────────────────────────────┐
│                    Router Layer                          │
│  - 接收 HTTP 请求                                         │
│  - 参数验证和解析                                         │
│  - 调用 Service 层                                        │
│  - 格式化响应数据                                         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                          │
│  - 业务流程编排                                           │
│  - 业务规则验证                                           │
│  - 状态流转控制                                           │
│  - 异常处理和日志                                         │
│  - 调用 Repository 获取/保存数据                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 Repository Layer                         │
│  - 封装数据访问逻辑                                       │
│  - 提供语义化的查询接口                                   │
│  - 处理 ORM 查询细节                                      │
│  - 查询优化（预加载、索引）                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Model Layer                           │
│  - 定义数据库表结构                                       │
│  - 字段定义和约束                                         │
│  - 简单的属性方法（@property）                            │
│  - 简单的状态变更方法                                     │
└─────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **单一职责原则**: 每一层只负责自己的职责
2. **依赖倒置原则**: Service 依赖 Repository 接口，而不是具体实现
3. **开闭原则**: 对扩展开放，对修改关闭
4. **接口隔离原则**: Repository 提供细粒度的接口方法

## 组件设计

### 1. BaseRepository（基础仓储类）

**位置**: `app/repositories/base.py`

**职责**:

- 提供通用的 CRUD 操作
- 处理泛型类型
- 统一异常处理

**接口设计**:

```python
from typing import TypeVar, Generic, Optional, List, Type
from tortoise.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """基础仓储类，提供通用的 CRUD 操作"""

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, **kwargs) -> T:
        """创建记录"""
        pass

    async def get_by_id(self, id: int) -> Optional[T]:
        """根据 ID 获取记录"""
        pass

    async def get_or_none(self, **filters) -> Optional[T]:
        """根据条件获取单条记录"""
        pass

    async def find_all(self, **filters) -> List[T]:
        """根据条件获取所有记录"""
        pass

    async def update(self, instance: T, **kwargs) -> T:
        """更新记录"""
        pass

    async def delete(self, instance: T) -> bool:
        """删除记录"""
        pass

    async def exists(self, **filters) -> bool:
        """检查记录是否存在"""
        pass

    async def count(self, **filters) -> int:
        """统计记录数量"""
        pass
```

### 2. ActivationCodeRepository（激活码仓储）

**位置**: `app/repositories/account/activation_repository.py`

**职责**:

- 封装激活码相关的所有数据访问操作
- 提供语义化的查询方法

**接口设计**:

```python
class ActivationCodeRepository(BaseRepository[ActivationCode]):
    """激活码仓储类"""

    def __init__(self):
        super().__init__(ActivationCode)

    async def find_by_code(self, code: str) -> Optional[ActivationCode]:
        """根据激活码查询"""
        pass

    async def find_unused_codes(
        self,
        type_code: int,
        limit: int
    ) -> List[ActivationCode]:
        """查询未使用的激活码"""
        pass

    async def find_distributed_codes(
        self,
        type_code: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[ActivationCode]:
        """查询已分发的激活码"""
        pass

    async def code_exists(self, code: str) -> bool:
        """检查激活码是否存在"""
        pass

    async def count_by_status(
        self,
        status: int,
        type_code: Optional[int] = None
    ) -> int:
        """按状态统计激活码数量"""
        pass

    async def find_with_filters(
        self,
        type_code: Optional[int] = None,
        status: Optional[int] = None,
        distributed_at_start: Optional[datetime] = None,
        distributed_at_end: Optional[datetime] = None,
        activated_at_start: Optional[datetime] = None,
        activated_at_end: Optional[datetime] = None,
        expire_time_start: Optional[datetime] = None,
        expire_time_end: Optional[datetime] = None,
        order_by: str = "-created_at"
    ) -> List[ActivationCode]:
        """复杂条件查询"""
        pass
```

### 3. ActivationCodeService（重构后）

**位置**: `app/services/account/activation_service.py`

**职责**:

- 业务流程编排
- 业务规则验证
- 调用 Repository 进行数据操作

**重构示例**:

```python
class ActivationCodeService:
    def __init__(self):
        self.repository = ActivationCodeRepository()

    async def init_activation_codes(
        self,
        request: ActivationCodeBatchCreateRequest
    ) -> ActivationCodeBatchResponse:
        """批量初始化激活码"""
        results = []
        total_count = 0

        for item in request.items:
            type_enum = ActivationTypeEnum.from_code(item.type)
            activation_codes = []

            for i in range(item.count):
                # 生成唯一激活码（业务逻辑）
                code = await self._generate_unique_code()

                # 通过 Repository 创建记录（数据访问）
                activation_code = await self.repository.create(
                    activation_code=code,
                    type=item.type,
                    status=ActivationCodeStatusEnum.UNUSED.code
                )
                activation_codes.append(code)

            # 业务逻辑：构建响应
            type_result = ActivationCodeTypeResult(...)
            results.append(type_result)
            total_count += len(activation_codes)

        return ActivationCodeBatchResponse(...)

    async def _generate_unique_code(self) -> str:
        """生成唯一激活码（业务逻辑）"""
        while True:
            code = self.generate_activation_code()
            # 通过 Repository 检查是否存在
            if not await self.repository.code_exists(code):
                return code
```

## 数据模型

### Model 层设计原则

**保留的内容**:

- 字段定义
- @property 只读属性
- 简单的计算方法（不涉及数据库操作）
- 简单的状态设置方法（如 `distribute()`, `activate()`）

**移除的内容**:

- 复杂的业务逻辑
- 数据库查询操作
- 与其他 Model 的交互

**示例**:

```python
class ActivationCode(BaseModel):
    """激活码模型"""
    activation_code = fields.CharField(max_length=50, unique=True)
    type = fields.IntField()
    status = fields.IntField(default=0)
    distributed_at = fields.DatetimeField(null=True)
    activated_at = fields.DatetimeField(null=True)
    expire_time = fields.DatetimeField(null=True)

    @property
    def type_enum(self) -> ActivationTypeEnum:
        """获取类型枚举（只读属性）"""
        return ActivationTypeEnum.from_code(self.type)

    @property
    def is_expired(self) -> bool:
        """检查是否过期（简单计算）"""
        if not self.expire_time:
            return False
        return is_expired(normalize_datetime(self.expire_time))

    def distribute(self):
        """设置为已分发状态（简单状态变更）"""
        self.distributed_at = get_utc_now()
        self.status = ActivationCodeStatusEnum.DISTRIBUTED.code

    def activate(self):
        """设置为已激活状态（简单状态变更）"""
        self.activated_at = get_utc_now()
        self.expire_time = self.calculate_expire_time(self.activated_at)
        self.status = ActivationCodeStatusEnum.ACTIVATED.code
```

## 错误处理

### Repository 层错误处理

```python
class RepositoryException(Exception):
    """仓储层异常基类"""
    pass

class RecordNotFoundException(RepositoryException):
    """记录未找到异常"""
    pass

class DuplicateRecordException(RepositoryException):
    """记录重复异常"""
    pass
```

### Service 层错误处理

Service 层捕获 Repository 异常并转换为业务异常：

```python
try:
    code = await self.repository.get_by_id(code_id)
    if not code:
        raise BusinessException(message="激活码不存在")
except RepositoryException as e:
    log.error(f"数据访问错误: {e}")
    raise BusinessException(message="系统错误，请稍后重试")
```

## 测试策略

### 单元测试

**Repository 测试**:

- 使用真实数据库或测试数据库
- 测试每个查询方法的正确性
- 测试边界条件和异常情况

**Service 测试**:

- Mock Repository 依赖
- 专注于业务逻辑测试
- 不依赖真实数据库

**示例**:

```python
# Service 单元测试
@pytest.fixture
def mock_repository():
    return Mock(spec=ActivationCodeRepository)

async def test_distribute_codes_insufficient(mock_repository):
    # 模拟 Repository 返回不足的激活码
    mock_repository.find_unused_codes.return_value = []

    service = ActivationCodeService()
    service.repository = mock_repository

    with pytest.raises(BusinessException):
        await service.distribute_activation_codes(
            ActivationCodeGetRequest(type=1, count=10)
        )
```

### 集成测试

- 测试完整的请求流程（Router -> Service -> Repository -> Model）
- 使用测试数据库
- 验证端到端功能

## 目录结构

```
app/
├── repositories/              # 新增：仓储层
│   ├── __init__.py
│   ├── base.py               # BaseRepository
│   ├── account/              # 账户模块仓储
│   │   ├── __init__.py
│   │   ├── activation_repository.py
│   │   ├── user_repository.py
│   │   └── user_session_repository.py
│   └── monitor/              # 监控模块仓储
│       ├── __init__.py
│       ├── monitor_repository.py
│       └── task_repository.py
├── services/                 # 服务层（重构）
│   ├── account/
│   │   ├── activation_service.py  # 移除 ORM 调用
│   │   └── ...
│   └── monitor/
│       └── ...
├── models/                   # 模型层（简化）
│   ├── base.py
│   ├── account/
│   └── monitor/
└── routers/                  # 路由层（不变）
    ├── account/
    └── monitor/
```

## 迁移策略

### 阶段 1: 创建基础设施

1. 创建 `repositories/` 目录结构
2. 实现 `BaseRepository` 基类
3. 编写 Repository 单元测试框架

### 阶段 2: 激活码模块重构（示例）

1. 创建 `ActivationCodeRepository`
2. 重构 `ActivationCodeService`
3. 运行现有测试确保功能不变
4. 编写新的单元测试

### 阶段 3: 其他模块迁移

1. 用户模块（User, UserSession）
2. 监控模块（MonitorConfig, Task）
3. 逐步迁移，确保每个模块独立可测试

### 阶段 4: 清理和优化

1. 移除 Model 中的复杂业务逻辑
2. 统一异常处理
3. 完善文档和示例

## 性能考虑

### 查询优化

Repository 层负责查询优化：

```python
async def find_with_user(self, code_id: int) -> Optional[ActivationCode]:
    """查询激活码并预加载用户信息"""
    return await self.model.get_or_none(id=code_id).prefetch_related('user')
```

### 批量操作

```python
async def bulk_create(self, codes: List[dict]) -> List[ActivationCode]:
    """批量创建激活码"""
    return await self.model.bulk_create([
        self.model(**code) for code in codes
    ])
```

### 缓存策略

Repository 层可以集成缓存：

```python
async def get_by_code_cached(self, code: str) -> Optional[ActivationCode]:
    """带缓存的查询"""
    cache_key = f"activation_code:{code}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    result = await self.find_by_code(code)
    if result:
        await cache.set(cache_key, result, expire=3600)
    return result
```

## 最佳实践

### 1. Repository 方法命名规范

- `find_*`: 查询多条记录
- `get_*`: 查询单条记录
- `create_*`: 创建记录
- `update_*`: 更新记录
- `delete_*`: 删除记录
- `exists_*`: 检查存在性
- `count_*`: 统计数量

### 2. Service 方法命名规范

- 使用业务语言命名（如 `distribute_codes`, `activate_code`）
- 方法名体现业务意图
- 避免暴露技术细节

### 3. 依赖注入

```python
class ActivationCodeService:
    def __init__(self, repository: ActivationCodeRepository = None):
        self.repository = repository or ActivationCodeRepository()
```

这样便于测试时注入 Mock Repository。

### 4. 事务处理

复杂事务在 Service 层管理：

```python
from tortoise import transactions

async def complex_business_operation(self):
    async with transactions.in_transaction():
        # 多个 Repository 操作
        code = await self.code_repo.create(...)
        user = await self.user_repo.update(...)
        # 如果任何操作失败，自动回滚
```

## 正确性属性

### 属性 1: Repository 封装完整性

_对于任何_ Service 类，其代码中不应包含任何直接的 ORM 调用（如 `Model.filter()`, `Model.create()`），所有数据访问都应通过 Repository 完成
**验证: 需求 1.2, 2.4**

### 属性 2: 职责单一性

_对于任何_ Repository 方法，其职责应仅限于数据访问，不应包含业务逻辑判断或状态流转
**验证: 需求 1.1, 1.4**

### 属性 3: Service 业务纯粹性

_对于任何_ Service 方法，其代码应专注于业务编排，通过 Repository 获取数据后进行业务判断和处理
**验证: 需求 2.1, 2.3**

### 属性 4: BaseRepository 通用性

_对于任何_ 继承 BaseRepository 的具体 Repository，都应自动获得基础 CRUD 能力，无需重复实现
**验证: 需求 3.1, 3.2**

### 属性 5: Model 简洁性

_对于任何_ Model 类，其方法应仅包含数据定义、只读属性和简单状态变更，不应包含数据库查询或复杂业务逻辑
**验证: 需求 4.1, 4.2, 4.3**

### 属性 6: 可测试性

_对于任何_ Service 类，应能够通过 Mock Repository 进行单元测试，不依赖真实数据库
**验证: 需求 5.1, 5.3**

### 属性 7: 接口语义化

_对于任何_ Repository 方法，其命名应清晰表达业务意图（如 `find_unused_codes`），而不是暴露技术细节（如 `filter_by_status_0`）
**验证: 需求 1.4**

### 属性 8: 向后兼容性

_对于任何_ 现有的 API 接口，重构后应保持相同的输入输出行为，不影响现有业务功能
**验证: 需求 6.4**

## 总结

通过引入 Repository 层，我们实现了：

1. **职责清晰**: 每一层专注于自己的职责
2. **易于测试**: Service 可以独立测试，不依赖数据库
3. **易于维护**: 数据访问逻辑集中管理，修改影响范围小
4. **易于扩展**: 新增功能遵循统一模式，降低开发成本
5. **代码复用**: BaseRepository 提供通用能力，减少重复代码

这种架构适合中大型项目，能够有效应对业务复杂度的增长。

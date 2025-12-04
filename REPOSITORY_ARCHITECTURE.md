# Repository 层架构文档

## 概述

本项目采用 **四层架构**：`Router -> Service -> Repository -> Model`，通过引入 Repository（仓储）层，实现了数据访问逻辑与业务逻辑的分离，提高了代码的可维护性、可测试性和可扩展性。

## 架构设计

### 四层职责划分

```
┌─────────────────────────────────────────────────────────────┐
│                      Router Layer                            │
│  职责：                                                       │
│  - 接收 HTTP 请求                                             │
│  - 参数验证和解析（通过 Pydantic Schema）                     │
│  - 调用 Service 层执行业务逻辑                                │
│  - 格式化响应数据（success_response, paginated_response）    │
│  - 不包含任何业务逻辑                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
│  职责：                                                       │
│  - 业务流程编排                                               │
│  - 业务规则验证（状态检查、权限验证）                         │
│  - 状态流转控制                                               │
│  - 异常处理和日志记录                                         │
│  - 调用 Repository 获取/保存数据                              │
│  - 不包含任何 ORM 调用                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Repository Layer                           │
│  职责：                                                       │
│  - 封装所有数据访问逻辑                                       │
│  - 提供语义化的查询接口                                       │
│  - 处理 ORM 查询细节（filter, order_by, limit 等）           │
│  - 查询优化（预加载、批量操作）                               │
│  - 不包含任何业务逻辑                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Model Layer                             │
│  职责：                                                       │
│  - 定义数据库表结构（字段、约束）                             │
│  - 简单的属性方法（@property）                                │
│  - 简单的状态变更方法（如 distribute(), activate()）         │
│  - 不包含数据库查询或复杂业务逻辑                             │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
app/
├── repositories/              # 仓储层
│   ├── __init__.py           # 导出所有 Repository
│   ├── base.py               # BaseRepository 基类
│   ├── account/              # 账户模块仓储
│   │   ├── __init__.py
│   │   ├── activation_repository.py    # 激活码仓储
│   │   ├── user_repository.py          # 用户仓储
│   │   └── user_session_repository.py  # 会话仓储
│   └── monitor/              # 监控模块仓储
│       ├── __init__.py
│       ├── monitor_repository.py       # 监控配置仓储
│       └── task_repository.py          # 任务仓储
├── services/                 # 服务层
│   ├── account/
│   │   ├── activation_service.py  # 使用 Repository
│   │   ├── user_service.py
│   │   └── auth_service.py
│   └── monitor/
│       └── monitor_service.py
├── models/                   # 模型层
│   ├── base.py              # BaseModel
│   ├── account/
│   │   ├── activation_code.py
│   │   ├── user.py
│   │   └── user_session.py
│   └── monitor/
│       ├── monitor_config.py
│       └── task.py
└── routers/                  # 路由层
    ├── account/
    │   └── activation_router.py
    └── monitor/
        └── monitor_router.py
```

## 代码示例

### 1. BaseRepository（基础仓储类）

```python
from typing import TypeVar, Generic, Optional, List, Type
from tortoise.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """基础仓储类，提供通用 CRUD 操作"""

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, **kwargs) -> T:
        """创建记录"""
        return await self.model.create(**kwargs)

    async def get_by_id(self, id: int) -> Optional[T]:
        """根据 ID 获取记录"""
        return await self.model.get_or_none(id=id)

    async def update(self, instance: T, **kwargs) -> T:
        """更新记录"""
        instance.update_from_dict(kwargs)
        await instance.save()
        return instance

    async def delete(self, instance: T) -> bool:
        """删除记录"""
        await instance.delete()
        return True

    # ... 其他通用方法
```

### 2. 具体 Repository（激活码仓储）

```python
from app.repositories.base import BaseRepository
from app.models.account.activation_code import ActivationCode

class ActivationCodeRepository(BaseRepository[ActivationCode]):
    """激活码仓储类"""

    def __init__(self):
        super().__init__(ActivationCode)

    async def find_by_code(self, code: str) -> Optional[ActivationCode]:
        """根据激活码查询"""
        return await self.get_or_none(activation_code=code)

    async def find_unused_codes(
        self,
        type_code: int,
        limit: int
    ) -> List[ActivationCode]:
        """查询未使用的激活码"""
        return await self.model.filter(
            type=type_code,
            status=ActivationCodeStatusEnum.UNUSED.code
        ).order_by("-created_at").limit(limit).all()

    async def code_exists(self, code: str) -> bool:
        """检查激活码是否存在"""
        return await self.exists(activation_code=code)
```

### 3. Service 层（业务逻辑）

```python
from app.repositories.account import ActivationCodeRepository

class ActivationCodeService:
    """激活码服务类"""

    def __init__(self, repository: ActivationCodeRepository = None):
        """支持依赖注入，便于测试"""
        self.repository = repository or ActivationCodeRepository()

    async def distribute_activation_codes(
        self,
        request: ActivationCodeGetRequest
    ) -> List[str]:
        """派发激活码（业务逻辑编排）"""
        log.info(f"派发激活码，类型：{request.type}，数量：{request.count}")

        # 通过 Repository 查询数据
        codes = await self.repository.find_unused_codes(
            type_code=request.type,
            limit=request.count
        )

        # 业务逻辑：验证数量
        if len(codes) < request.count:
            type_enum = ActivationTypeEnum.from_code(request.type)
            raise BusinessException(
                message=f"{type_enum.desc}可用激活码不足"
            )

        # 业务逻辑：批量分发
        activation_codes = []
        for code in codes:
            code.distribute()  # Model 的状态变更方法
            await self.repository.update(code)  # 通过 Repository 保存
            activation_codes.append(code.activation_code)

        log.info(f"成功派发{len(activation_codes)}个激活码")
        return activation_codes
```

### 4. Router 层（接口）

```python
from fastapi import APIRouter
from app.services.account.activation_service import ActivationCodeService

router = APIRouter()

# 创建 Service 实例
activation_service = ActivationCodeService()

@router.post("/distribute")
async def distribute_activation_codes(request: ActivationCodeGetRequest):
    """派发激活码"""
    # 调用 Service 执行业务逻辑
    activation_codes = await activation_service.distribute_activation_codes(request)
    return success_response(data=activation_codes)
```

### 5. Model 层（数据定义）

```python
from tortoise import fields
from app.models.base import BaseModel

class ActivationCode(BaseModel):
    """激活码模型"""
    # 基础字段 (id, created_at, updated_at) 继承自 BaseModel
    activation_code = fields.CharField(max_length=50, unique=True)
    type = fields.IntField()
    status = fields.IntField(default=0)
    distributed_at = fields.DatetimeField(null=True)

    @property
    def type_enum(self) -> ActivationTypeEnum:
        """获取类型枚举（只读属性）"""
        return ActivationTypeEnum.from_code(self.type)

    def distribute(self):
        """设置为已分发状态（简单状态变更）"""
        self.distributed_at = get_utc_now()
        self.status = ActivationCodeStatusEnum.DISTRIBUTED.code
```

## 开发指南

### 如何创建新的 Repository

1. **继承 BaseRepository**

```python
from app.repositories.base import BaseRepository
from app.models.your_module.your_model import YourModel

class YourRepository(BaseRepository[YourModel]):
    def __init__(self):
        super().__init__(YourModel)
```

2. **添加专用查询方法**

```python
    async def find_by_name(self, name: str) -> Optional[YourModel]:
        """根据名称查询"""
        return await self.get_or_none(name=name)

    async def find_active_items(self) -> List[YourModel]:
        """查询活跃项"""
        return await self.model.filter(is_active=True).all()
```

3. **导出 Repository**

在 `app/repositories/your_module/__init__.py` 中：

```python
from .your_repository import YourRepository

__all__ = ["YourRepository"]
```

### 如何重构现有 Service

1. **添加 Repository 依赖**

```python
class YourService:
    def __init__(self, repository: YourRepository = None):
        self.repository = repository or YourRepository()
```

2. **替换 ORM 调用**

**重构前：**

```python
async def get_item(self, id: int):
    item = await YourModel.get_or_none(id=id)  # ❌ 直接 ORM 调用
    if not item:
        raise BusinessException("不存在")
    return item
```

**重构后：**

```python
async def get_item(self, id: int):
    item = await self.repository.get_by_id(id)  # ✅ 通过 Repository
    if not item:
        raise BusinessException("不存在")
    return item
```

3. **更新 Router**

```python
# 创建 Service 实例
your_service = YourService()

@router.get("/{id}")
async def get_item(id: int):
    item = await your_service.get_item(id)
    return success_response(data=item)
```

### 如何编写单元测试

#### Repository 测试（集成测试）

```python
import pytest
from app.repositories.account import ActivationCodeRepository

class TestActivationCodeRepository:
    @pytest.fixture
    def repository(self):
        return ActivationCodeRepository()

    @pytest.mark.asyncio
    async def test_find_by_code(self, repository):
        # 创建测试数据
        await repository.create(
            activation_code="TEST_CODE",
            type=1,
            status=0
        )

        # 测试查询
        code = await repository.find_by_code("TEST_CODE")
        assert code is not None
        assert code.activation_code == "TEST_CODE"
```

#### Service 测试（单元测试，使用 Mock）

```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.account.activation_service import ActivationCodeService

class TestActivationCodeService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def service(self, mock_repository):
        return ActivationCodeService(repository=mock_repository)

    @pytest.mark.asyncio
    async def test_distribute_codes_insufficient(self, service, mock_repository):
        # Mock Repository 返回空列表
        mock_repository.find_unused_codes = AsyncMock(return_value=[])

        # 测试业务逻辑
        with pytest.raises(BusinessException):
            await service.distribute_activation_codes(
                ActivationCodeGetRequest(type=1, count=10)
            )
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
class YourService:
    def __init__(self, repository: YourRepository = None):
        self.repository = repository or YourRepository()
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

### 5. 查询优化

在 Repository 层实现：

```python
async def find_with_user(self, code_id: int):
    """查询激活码并预加载用户信息"""
    return await self.model.get_or_none(id=code_id).prefetch_related('user')
```

### 6. 批量操作

```python
async def bulk_create_codes(self, codes: List[dict]):
    """批量创建激活码"""
    return await self.bulk_create(codes)
```

## 常见问题

### Q1: 为什么要引入 Repository 层？

**A:**

- **职责分离**: Service 专注业务逻辑，Repository 专注数据访问
- **易于测试**: Service 可以 Mock Repository 进行单元测试
- **易于维护**: 数据访问逻辑集中管理，修改影响范围小
- **易于扩展**: 统一的开发模式，降低开发成本

### Q2: Repository 和 Service 的边界在哪里？

**A:**

- **Repository**: 只负责数据访问，不包含业务逻辑判断
- **Service**: 负责业务流程编排、规则验证、状态流转

### Q3: Model 中的方法应该保留吗？

**A:**

- **保留**: 简单的状态变更方法（如 `distribute()`, `activate()`）
- **保留**: 只读属性（`@property`）
- **移除**: 复杂的业务逻辑
- **移除**: 数据库查询操作

### Q4: 如何处理复杂查询？

**A:** 在 Repository 中添加专门的查询方法：

```python
async def find_with_filters(
    self,
    type_code: Optional[int] = None,
    status: Optional[int] = None,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None
) -> List[ActivationCode]:
    """复杂条件查询"""
    query = self.model.all()

    if type_code is not None:
        query = query.filter(type=type_code)
    if status is not None:
        query = query.filter(status=status)
    # ... 更多条件

    return await query.all()
```

### Q5: 性能会受影响吗？

**A:** 不会。Repository 只是封装层，不引入额外开销。反而可以通过 Repository 统一实现查询优化（预加载、批量操作等）。

## 迁移检查清单

重构现有代码时，请确保：

- [ ] Service 中不包含任何 `Model.filter()`, `Model.create()` 等 ORM 调用
- [ ] 所有数据访问都通过 Repository 完成
- [ ] Repository 方法命名清晰，体现业务意图
- [ ] Service 构造函数支持依赖注入
- [ ] Router 创建 Service 实例并调用
- [ ] Model 只包含数据定义和简单方法
- [ ] 编写了相应的单元测试
- [ ] 所有现有功能正常工作

## 总结

通过引入 Repository 层，我们实现了：

1. **职责清晰**: 每一层专注于自己的职责
2. **易于测试**: Service 可以独立测试，不依赖数据库
3. **易于维护**: 数据访问逻辑集中管理，修改影响范围小
4. **易于扩展**: 新增功能遵循统一模式，降低开发成本
5. **代码复用**: BaseRepository 提供通用能力，减少重复代码

这种架构适合中大型项目，能够有效应对业务复杂度的增长。

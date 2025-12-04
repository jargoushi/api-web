# BaseModel 重构说明

## 📋 重构目标

抽取公共字段到 `BaseModel`，所有业务模型都继承此基类，统一管理：

- `id` - 主键 ID
- `created_at` - 创建时间
- `updated_at` - 更新时间

---

## ✅ 已完成的工作

### 1. 创建 BaseModel

**文件：** `app/models/base.py`

```python
class BaseModel(Model):
    """基础模型类"""

    id = fields.BigIntField(pk=True, description="主键ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True  # 抽象类，不创建数据库表
```

### 2. 更新所有业务模型

所有模型都已改为继承 `BaseModel`，并移除了重复的公共字段：

#### 账户模块 (3 个)

- ✅ `User` - 用户模型
- ✅ `UserSession` - 用户会话模型
- ✅ `ActivationCode` - 激活码模型

#### 监控模块 (3 个)

- ✅ `MonitorConfig` - 监控配置模型
- ✅ `MonitorDailyStats` - 监控每日数据模型
- ✅ `Task` - 任务模型

---

## 🎯 重构效果

### 重构前

每个模型都要重复定义：

```python
class User(Model):
    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(...)
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
```

### 重构后

继承 `BaseModel`，代码更简洁：

```python
class User(BaseModel):
    # 基础字段 (id, created_at, updated_at) 继承自 BaseModel
    username = fields.CharField(...)
```

---

## 📊 代码统计

| 项目             | 数量             |
| ---------------- | ---------------- |
| 创建的文件       | 1 个 (`base.py`) |
| 更新的模型       | 6 个             |
| 移除的重复代码行 | ~18 行           |
| 代码可维护性     | ⬆️ 显著提升      |

---

## 💡 优势

### 1. 代码复用

- 公共字段只定义一次
- 减少重复代码

### 2. 统一管理

- 所有模型的基础字段保持一致
- 便于后续扩展（如添加 `deleted_at` 软删除字段）

### 3. 易于维护

- 修改基础字段只需改一处
- 新增模型只需继承 `BaseModel`

### 4. 类型一致

- 所有 `id` 统一为 `BigIntField`
- 所有时间字段统一为 `DatetimeField`

---

## 🚀 使用方式

### 创建新模型

```python
from tortoise import fields
from app.models.base import BaseModel

class NewModel(BaseModel):
    """新业务模型"""
    # 基础字段 (id, created_at, updated_at) 自动继承

    # 只需定义业务字段
    name = fields.CharField(max_length=100, description="名称")
    status = fields.IntField(default=0, description="状态")

    class Meta:
        table = "new_table"
```

### 后续扩展

如果需要添加软删除功能，只需在 `BaseModel` 中添加：

```python
class BaseModel(Model):
    id = fields.BigIntField(pk=True, description="主键ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    deleted_at = fields.DatetimeField(null=True, description="删除时间")  # 新增

    class Meta:
        abstract = True
```

所有继承的模型都会自动拥有 `deleted_at` 字段！

---

## ✅ 验证结果

所有模型文件已通过语法检查，无错误：

- ✅ `app/models/base.py`
- ✅ `app/models/__init__.py`
- ✅ `app/models/account/user.py`
- ✅ `app/models/account/user_session.py`
- ✅ `app/models/account/activation_code.py`
- ✅ `app/models/monitor/monitor_config.py`
- ✅ `app/models/monitor/monitor_daily_stats.py`
- ✅ `app/models/monitor/task.py`

---

## 🎉 总结

成功抽取 `BaseModel`，所有业务模型都已继承基类，代码结构更加清晰和易于维护！

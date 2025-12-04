# 对象映射优化方案 - 最终版

## 📊 优化原则

**保持 Model 层的纯粹性**：Model 不应该包含修改自身属性的业务方法，所有更新操作都在 Service 层完成。

---

## ✅ 最终优化方案

### 统一使用 `update_from_dict()` 方法

所有对象更新都使用 Tortoise ORM 的 `update_from_dict()` 方法：

```python
# 批量更新
code.update_from_dict({
    'distributed_at': get_utc_now(),
    'status': ActivationCodeStatusEnum.DISTRIBUTED.code
})
await code.save()
```

---

## 🔧 已完成的优化

### 1. monitor_service.py（2 处）

**优化前：**

```python
config.target_url = request.target_url
config.is_active = request.is_active
```

**优化后：**

```python
update_data = request.model_dump(exclude_unset=True)
config.update_from_dict(update_data)
```

### 2. activation_service.py（3 处）

#### 分发激活码

**优化前：**

```python
code.distribute()  # Model 中的方法
```

**优化后：**

```python
code.update_from_dict({
    'distributed_at': ActivationCodeService._get_current_time(),
    'status': ActivationCodeStatusEnum.DISTRIBUTED.code
})
```

#### 激活激活码

**优化前：**

```python
code.activate()  # Model 中的方法
```

**优化后：**

```python
activated_at = ActivationCodeService._get_current_time()
code.update_from_dict({
    'activated_at': activated_at,
    'expire_time': code.calculate_expire_time(activated_at),
    'status': ActivationCodeStatusEnum.ACTIVATED.code
})
```

#### 作废激活码

**优化前：**

```python
code.status = ActivationCodeStatusEnum.INVALID.code
```

**优化后：**

```python
code.update_from_dict({'status': ActivationCodeStatusEnum.INVALID.code})
```

### 3. activation_code.py (Model)

**移除的方法：**

- ❌ `distribute()` - 删除
- ❌ `activate()` - 删除
- ❌ `invalidate()` - 删除

**保留的方法：**

- ✅ `calculate_expire_time()` - 保留（纯计算方法，不修改属性）
- ✅ `is_expired` - 保留（只读属性）

---

## 🎯 优化效果

### Model 层职责

**只包含：**

- ✅ 字段定义
- ✅ 只读属性（@property）
- ✅ 纯计算方法（不修改自身属性）

**不包含：**

- ❌ 修改自身属性的方法
- ❌ 业务逻辑

### Service 层职责

**负责：**

- ✅ 所有业务逻辑
- ✅ 所有数据更新操作
- ✅ 使用 `update_from_dict()` 批量更新

---

## 📝 统一的代码模式

### 从 Request 更新（多字段）

```python
update_data = request.model_dump(exclude_unset=True)
model.update_from_dict(update_data)
await model.save()
```

### 业务逻辑更新（多字段）

```python
model.update_from_dict({
    'field1': value1,
    'field2': value2,
    'field3': value3
})
await model.save()
```

### 单字段特殊处理

```python
# 需要特殊处理的情况（如密码哈希）
user.password = hash_password(new_password)
await user.save()
```

---

## 💡 优势

1. **职责清晰**：Model 只负责数据结构，Service 负责业务逻辑
2. **易于测试**：业务逻辑集中在 Service 层
3. **代码简洁**：使用 `update_from_dict()` 批量更新
4. **易于维护**：新增字段时无需修改多处代码
5. **符合最佳实践**：遵循单一职责原则

---

## 🚀 总结

所有优化已完成，项目现在使用统一的对象映射方式：

- ✅ Model 层保持纯粹，不包含修改自身属性的方法
- ✅ Service 层使用 `update_from_dict()` 进行批量更新
- ✅ 从 Request 更新使用 `model_dump()` + `update_from_dict()`
- ✅ 响应对象使用 `model_validate(obj, from_attributes=True)`

代码更加清晰、易维护，符合最佳实践！

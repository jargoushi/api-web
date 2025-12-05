# 数据库修复指南

## 问题描述

在运行 `/monitor/stats/daily` 接口时出现错误：

```
tortoise.exceptions.OperationalError: (1054, "Unknown column 'updated_at' in 'field list'")
```

## 原因分析

`monitor_daily_stats` 表缺少 `updated_at` 字段。

- **Model 定义**：`MonitorDailyStats` 继承自 `BaseModel`，`BaseModel` 包含 `updated_at` 字段
- **数据库表**：`monitor_daily_stats` 表创建时遗漏了 `updated_at` 字段

## 解决方案

### 方案 1：执行 ALTER TABLE 语句（推荐）

执行以下 SQL 语句为现有表添加 `updated_at` 字段：

```sql
ALTER TABLE `monitor_daily_stats`
ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
AFTER `created_at`;
```

**SQL 文件位置：** `app/sql/add_updated_at_to_monitor_daily_stats.sql`

### 方案 2：重建表（仅用于开发环境）

如果是开发环境且数据可以丢弃，可以删除表后重新创建：

```sql
DROP TABLE IF EXISTS `monitor_daily_stats`;

-- 然后执行 app/sql/建表语句.sql 中的 monitor_daily_stats 建表语句
```

## 执行步骤

### 1. 连接数据库

```bash
mysql -h <host> -u <username> -p <database>
```

### 2. 执行修复 SQL

```bash
# 方式 1: 直接执行 SQL 文件
mysql -h <host> -u <username> -p <database> < app/sql/add_updated_at_to_monitor_daily_stats.sql

# 方式 2: 在 MySQL 命令行中执行
mysql> source app/sql/add_updated_at_to_monitor_daily_stats.sql;

# 方式 3: 直接复制 SQL 语句执行
mysql> ALTER TABLE `monitor_daily_stats`
    -> ADD COLUMN `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
    -> AFTER `created_at`;
```

### 3. 验证修复

```sql
-- 查看表结构
DESC monitor_daily_stats;

-- 应该能看到 updated_at 字段
-- | updated_at | datetime | NO   |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
```

### 4. 重启应用

修复完成后，重启 FastAPI 应用即可。

## 已修复的文件

1. ✅ `app/sql/建表语句.sql` - 已更新建表语句，添加 `updated_at` 字段
2. ✅ `app/sql/add_updated_at_to_monitor_daily_stats.sql` - 新增 ALTER TABLE 语句

## 其他表检查

已检查所有表，确认其他表都包含 `updated_at` 字段：

- ✅ `activation_codes` - 有 `updated_at`
- ✅ `user` - 有 `updated_at`
- ✅ `user_sessions` - 有 `last_accessed_at`（功能等同）
- ✅ `monitor_configs` - 有 `updated_at`
- ❌ `monitor_daily_stats` - **缺少 `updated_at`**（已修复）
- ✅ `tasks` - 有 `updated_at`

## 注意事项

1. **生产环境**：执行前请先备份数据库
2. **权限**：确保数据库用户有 ALTER TABLE 权限
3. **影响**：此操作会锁表，建议在低峰期执行
4. **验证**：执行后务必验证表结构和应用功能

## 预防措施

为避免类似问题，建议：

1. 使用数据库迁移工具（如 Alembic）管理表结构变更
2. 建表时严格按照 Model 定义创建字段
3. 定期检查 Model 定义与数据库表结构的一致性

# 实现计划 - Repository 层架构重构

## 任务列表

- [x] 1. 创建 Repository 基础设施

  - 创建 `app/repositories/` 目录结构
  - 实现 `BaseRepository` 基类，提供通用 CRUD 方法
  - 创建 `__init__.py` 文件，统一导出
  - _需求: 3.1, 3.2, 7.1, 7.2_

- [x] 1.1 编写 BaseRepository 单元测试

  - 测试 create、get_by_id、update、delete 等基础方法
  - 测试泛型类型处理
  - 测试异常情况
  - _需求: 5.2_

- [x] 2. 创建 ActivationCodeRepository

  - 创建 `app/repositories/account/activation_repository.py`
  - 继承 BaseRepository
  - 实现 `find_by_code` 方法
  - 实现 `find_unused_codes` 方法
  - 实现 `code_exists` 方法
  - 实现 `count_by_status` 方法
  - 实现 `find_with_filters` 复杂查询方法
  - _需求: 1.1, 1.3, 1.4, 6.2, 7.3_

- [x] 2.1 编写 ActivationCodeRepository 单元测试

  - 测试所有查询方法的正确性
  - 测试边界条件（空结果、大量数据）
  - 测试异常情况
  - _需求: 5.2_

- [x] 3. 重构 ActivationCodeService

  - 在 Service 中注入 ActivationCodeRepository
  - 重构 `init_activation_codes` 方法，使用 Repository
  - 重构 `distribute_activation_codes` 方法，使用 Repository
  - 重构 `activate_activation_code` 方法，使用 Repository
  - 重构 `invalidate_activation_code` 方法，使用 Repository
  - 重构 `get_activation_code_by_code` 方法，使用 Repository
  - 重构 `get_activation_code_queryset` 方法，使用 Repository
  - 移除所有直接的 ORM 调用（`ActivationCode.filter()` 等）
  - _需求: 1.2, 2.1, 2.2, 2.3, 2.4, 6.1, 6.3_

- [x] 3.1 编写 Service 单元测试（使用 Mock Repository）

  - Mock ActivationCodeRepository
  - 测试业务逻辑（状态验证、异常处理）
  - 测试业务流程编排
  - 不依赖真实数据库
  - _需求: 5.1, 5.3_

- [x] 4. 验证功能完整性

  - 运行现有的激活码集成测试
  - 确保所有 API 接口功能正常
  - 验证业务逻辑未被破坏
  - _需求: 6.4_

- [x] 5. 简化 ActivationCode Model

  - 保留字段定义和 @property 属性
  - 保留简单的状态变更方法（distribute、activate、invalidate）
  - 移除复杂的业务逻辑（如果有）
  - 确保 Model 只包含数据定义和简单方法
  - _需求: 4.1, 4.2, 4.3, 4.4_

- [x] 6. 创建其他 Repository（用户模块）

  - 创建 `UserRepository`
  - 创建 `UserSessionRepository`
  - 实现各自的专用查询方法
  - _需求: 7.3_

- [x] 7. 重构其他 Service（用户模块）

  - 重构 `UserService`，使用 `UserRepository`
  - 重构 `AuthService`，使用 `UserRepository` 和 `UserSessionRepository`
  - 移除直接的 ORM 调用
  - _需求: 2.1, 2.2, 2.3, 2.4_

- [x] 8. 创建 Repository（监控模块）

  - 创建 `MonitorConfigRepository`
  - 创建 `TaskRepository`
  - 创建 `MonitorDailyStatsRepository`
  - 实现各自的专用查询方法
  - _需求: 7.3_

- [x] 9. 重构 Service（监控模块）

  - 重构 `MonitorService`，使用 `MonitorConfigRepository`
  - 重构 `TaskService`，使用 `TaskRepository`
  - 移除直接的 ORM 调用
  - _需求: 2.1, 2.2, 2.3, 2.4_

- [x] 10. 添加错误处理机制

  - 创建 `RepositoryException` 异常基类
  - 创建 `RecordNotFoundException` 异常
  - 创建 `DuplicateRecordException` 异常
  - 在 Repository 中使用统一的异常处理
  - 在 Service 中捕获并转换为业务异常
  - _需求: 设计文档 - 错误处理_

- [x] 10.1 编写异常处理测试

  - 测试 Repository 异常抛出
  - 测试 Service 异常转换
  - 测试异常信息的准确性
  - _需求: 5.2_

- [x] 11. 性能优化

  - 在 Repository 中实现查询预加载（prefetch_related）
  - 实现批量操作方法（bulk_create、bulk_update）
  - 添加查询性能日志
  - _需求: 设计文档 - 性能考虑_

- [x] 11.1 编写性能测试

  - 测试批量操作性能
  - 测试预加载效果
  - 对比重构前后的性能差异
  - _需求: 非功能性需求 - 性能要求_

- [x] 12. 编写架构文档

  - 创建 `REPOSITORY_ARCHITECTURE.md`
  - 说明四层架构的职责划分
  - 提供 Repository 和 Service 的代码示例
  - 说明如何创建新的 Repository
  - 说明如何编写单元测试
  - 提供最佳实践和常见问题
  - _需求: 8.1, 8.2, 8.3, 8.4_

- [x] 13. 代码审查和清理

  - 检查所有 Service 是否移除了 ORM 调用
  - 检查所有 Repository 是否遵循命名规范
  - 检查代码注释是否完整
  - 统一代码风格
  - _需求: 非功能性需求 - 可维护性要求_

- [x] 14. 最终验证

  - 运行所有单元测试
  - 运行所有集成测试
  - 验证所有 API 接口功能
  - 检查测试覆盖率
  - _需求: 非功能性需求 - 兼容性要求_

## 任务依赖关系

```
1 (基础设施)
├── 1.1 (测试)*
└── 2 (ActivationCodeRepository)
    ├── 2.1 (测试)*
    └── 3 (重构 ActivationCodeService)
        ├── 3.1 (测试)*
        ├── 4 (验证功能)
        └── 5 (简化 Model)
            └── 6 (其他 Repository - 用户)
                └── 7 (重构 Service - 用户)
                    └── 8 (Repository - 监控)
                        └── 9 (重构 Service - 监控)
                            └── 10 (错误处理)
                                ├── 10.1 (测试)*
                                └── 11 (性能优化)
                                    ├── 11.1 (测试)*
                                    └── 12 (文档)
                                        └── 13 (代码审查)
                                            └── 14 (最终验证)
```

## 里程碑

### 里程碑 1: 基础设施完成（任务 1-2）

- BaseRepository 实现完成
- ActivationCodeRepository 创建完成
- 基础测试通过

### 里程碑 2: 激活码模块重构完成（任务 3-5）

- ActivationCodeService 重构完成
- 所有现有功能正常
- Model 简化完成

### 里程碑 3: 全模块迁移完成（任务 6-9）

- 所有 Repository 创建完成
- 所有 Service 重构完成
- 所有模块功能正常

### 里程碑 4: 完善和优化（任务 10-14）

- 错误处理完善
- 性能优化完成
- 文档完整
- 代码质量达标

## 预估工作量

| 任务     | 预估时间    | 优先级 |
| -------- | ----------- | ------ |
| 1-2      | 4 小时      | 高     |
| 3-5      | 6 小时      | 高     |
| 6-7      | 4 小时      | 中     |
| 8-9      | 4 小时      | 中     |
| 10-11    | 3 小时      | 中     |
| 12-14    | 3 小时      | 低     |
| **总计** | **24 小时** | -      |

## 注意事项

1. **渐进式重构**: 每完成一个模块就进行测试验证，确保功能正常
2. **保持兼容**: 重构过程中不改变 API 接口行为
3. **测试先行**: 在重构前确保有足够的测试覆盖
4. **代码审查**: 每个里程碑完成后进行代码审查
5. **文档同步**: 及时更新文档，记录设计决策

## 测试策略

所有任务都包含完整的测试覆盖，确保代码质量：

- **单元测试**: 测试每个 Repository 和 Service 的独立功能
- **集成测试**: 测试完整的业务流程
- **性能测试**: 确保重构不影响性能
- **测试覆盖率目标**: 80% 以上

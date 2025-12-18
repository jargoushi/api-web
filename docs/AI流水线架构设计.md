# AI 流水线平台架构设计

> 版本：v2.0
> 日期：2025-12-18

---

## 一、整体架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 / API 层                             │
└─────────────────────────────────────────────────────────────────┘
                               │
┌──────────────┬───────────────┼───────────────┬──────────────────┐
│   监控模块   │   下载模块    │   素材管理    │   创作/发布模块   │
│  (Monitor)   │  (Download)   │  (Material)   │  (Create/Pub)   │
└──────────────┴───────────────┴───────────────┴──────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                        任务调度系统                               │
│              (APScheduler + Worker + TaskQueue)                  │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层                                 │
│                    (MySQL + 文件存储)                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心数据流

```
采集监控 → 选品入库 → 分配账号 → 创作加工 → 发布上线
    │           │           │           │           │
    ▼           ▼           ▼           ▼           ▼
监控结果    源素材库    素材分配    最终素材    发布记录
```

---

## 三、模块详细设计

### 3.1 监控模块 (Monitor)

#### 3.1.1 采集监控

**目的**：监控指定平台账号或链接，获取新内容

**配置项**：
| 字段 | 说明 |
|-----|------|
| `platform` | 平台（抖音/快手/小红书/B站） |
| `target_type` | 监控类型（account/link） |
| `target_url` | 目标链接 |
| `check_interval` | 检测间隔（分钟） |

**结果存储**：
```python
class MonitorResult:
    config_id: int          # 监控配置ID
    platform: str           # 平台
    content_id: str         # 内容原始ID
    content_url: str        # 内容链接
    title: str              # 标题
    author: str             # 作者
    thumbnail: str          # 封面
    extra_data: JSON        # 平台特有数据
    discovered_at: datetime # 发现时间
```

#### 3.1.2 效益监控

**目的**：监控已发布内容的每日数据变化

**关联**：基于 `AccountProjectChannel` 绑定关系

---

### 3.2 下载模块 (Download)

**定位**：底层服务，被其他模块调用

**接口设计**：
```python
class DownloadService:
    async def download(self, url: str, platform: str, save_dir: str) -> DownloadResult

class DownloadResult:
    success: bool
    file_path: str
    duration: int
    width: int
    height: int
    error_msg: str
```

**技术选型**：`yt-dlp` + Playwright（备用）

---

### 3.3 素材管理模块 (Material)

#### 3.3.1 源素材库
```python
class SourceMaterial:
    id: int
    user_id: int
    monitor_result_id: int
    platform: str
    content_id: str
    content_url: str
    title: str
    author: str
    thumbnail_path: str
    video_path: str
    duration: int
    width: int
    height: int
    status: SourceMaterialStatus
    # pending → selected → assigned → processing → completed → archived
```

#### 3.3.2 素材分配
```python
class MaterialAssignment:
    id: int
    source_material_id: int
    account_id: int
    assigned_at: datetime
    final_material_id: int
    publish_status: PublishStatus
    # pending → creating → ready → publishing → published → failed
```

#### 3.3.3 最终素材
```python
class FinalMaterial:
    id: int
    assignment_id: int
    source_material_id: int
    draft_name: str
    draft_path: str
    output_path: str
    title: str
    description: str
    tags: JSON
    duration: int
```

---

### 3.4 发布模块 (Publish)

**触发方式**：定时发布 / 手动发布

**发布逻辑**：
1. 查询账号绑定的渠道列表
2. 遍历每个渠道，调用对应平台适配器
3. 上传视频到平台
4. 更新发布状态

```python
class PublishRecord:
    id: int
    assignment_id: int
    final_material_id: int
    account_id: int
    channel_code: int
    platform_content_id: str
    platform_content_url: str
    status: PublishStatus
    error_msg: str
    scheduled_at: datetime
    published_at: datetime
```

---

## 四、表结构汇总

| 表名 | 说明 |
|------|------|
| `monitor_configs` | 监控配置（已有） |
| `monitor_results` | 采集监控结果（新增） |
| `monitor_daily_stats` | 效益监控数据（已有） |
| `source_materials` | 源素材库（新增） |
| `material_assignments` | 素材分配（新增） |
| `final_materials` | 最终素材（新增） |
| `publish_records` | 发布记录（新增） |
| `tasks` | 任务表（已有） |

---

## 五、开发优先级

| 阶段 | 模块 | 内容 |
|-----|------|------|
| **P0** | 任务系统 | Worker基类、调度器、状态机 |
| **P0** | 下载模块 | yt-dlp集成、下载服务 |
| **P1** | 监控-采集 | 配置管理、结果存储 |
| **P1** | 素材管理 | 源素材库、分配功能 |
| **P2** | 创作模块 | 剪映对接 |
| **P2** | 发布模块 | 多平台发布 |
| **P3** | 监控-效益 | 数据统计 |

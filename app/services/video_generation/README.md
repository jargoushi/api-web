# 视频生成服务模块

基于 pyJianYingDraft 实现的剪映自动化视频生成服务。

## 模块结构

```
video_generation/
├── __init__.py              # 模块导出
├── draft_service.py         # 草稿生成服务
├── template_manager.py      # 模板管理服务
├── material_manager.py      # 素材管理服务
├── export_service.py        # 视频导出服务
└── README.md               # 本文档
```

## 服务说明

### 1. DraftService（草稿生成服务）

负责创建和管理剪映草稿，包括：

- 创建新草稿
- 从模板创建草稿
- 添加视频/音频/文本片段
- 导入字幕
- 添加轨道
- 保存草稿

**使用示例：**

```python
from app.services.video_generation import draft_service

# 创建草稿
script = await draft_service.create_draft("我的视频", 1920, 1080)

# 添加视频片段
await draft_service.add_video_segment(
    script,
    video_path="path/to/video.mp4",
    start_time="0s",
    duration="10s"
)

# 添加文本
await draft_service.add_text_segment(
    script,
    text="标题文字",
    start_time="0s",
    duration="5s"
)

# 保存草稿
await draft_service.save_draft(script)
```

### 2. TemplateManager（模板管理服务）

负责管理剪映草稿模板，包括：

- 加载模板
- 复制模板
- 替换素材
- 替换文本
- 提取素材元数据
- 导入轨道

**使用示例：**

```python
from app.services.video_generation import template_manager

# 从模板创建草稿
script = await template_manager.duplicate_template("模板名称", "新草稿名称")

# 替换素材
await template_manager.replace_material_by_name(
    script,
    old_material_name="video.mp4",
    new_material_path="path/to/new_video.mp4",
    material_type="video"
)

# 替换文本
await template_manager.replace_text(
    script,
    track_name="字幕",
    segment_index=0,
    new_text="新的文本内容"
)
```

### 3. MaterialManager（素材管理服务）

负责管理视频、音频、图片等素材文件，包括：

- 获取素材路径
- 列出素材文件
- 保存素材
- 删除素材
- 清理临时文件

**使用示例：**

```python
from app.services.video_generation import material_manager

# 列出视频素材
videos = await material_manager.list_materials("video")

# 获取素材路径
video_path = await material_manager.get_material_path("video", "my_video.mp4")

# 保存素材
await material_manager.save_material(
    "video",
    "new_video.mp4",
    video_content_bytes
)
```

### 4. ExportService（视频导出服务）

负责控制剪映导出视频，包括：

- 单个草稿导出
- 批量草稿导出
- 自定义分辨率和帧率

**使用示例：**

```python
from app.services.video_generation import export_service

# 导出单个草稿
video_path = await export_service.export_draft(
    draft_name="我的视频",
    export_path="./output/my_video.mp4",
    resolution="1080p",
    framerate=30
)

# 批量导出
video_paths = await export_service.batch_export(
    draft_names=["视频1", "视频2", "视频3"],
    export_folder="./output",
    resolution="1080p",
    framerate=30
)
```

## 配置说明

在 `.env` 文件中添加以下配置：

```env
# 剪映草稿文件夹路径（必须配置）
JIANYING_DRAFT_FOLDER=C:/Users/你的用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft

# 素材文件基础路径（可选，默认为 ./materials）
MATERIAL_BASE_PATH=./materials
```

## 注意事项

1. **剪映版本兼容性**

   - 草稿生成功能支持剪映 5+ 所有版本
   - 模板模式仅支持剪映 5.9 及以下版本（6+ 版本草稿文件已加密）
   - 自动导出功能仅支持剪映 6 及以下版本（7+ 版本隐藏了控件）

2. **平台兼容性**

   - Windows：支持所有功能
   - Linux/MacOS：支持草稿生成和模板模式，不支持自动导出

3. **使用前准备**

   - 确保已安装剪映专业版
   - 配置正确的草稿文件夹路径
   - 准备好素材文件

4. **导出功能注意**
   - 导出前需要打开剪映并位于目录页
   - 导出过程会控制鼠标，建议在闲时运行
   - 确保有导出权限（VIP 功能需要开通 VIP）

## 依赖说明

本模块依赖 `pyJianYingDraft` 库，源码已下载到项目根目录的 `pyJianYingDraft_source` 文件夹。

如需更新或查看源码，请访问：https://github.com/GuanYixuan/pyJianYingDraft

## 后续扩展

可以在此基础上扩展以下功能：

- 特效服务（effect_service.py）- 添加和管理视频特效
- 滤镜服务（filter_service.py）- 添加和管理滤镜
- 动画服务（animation_service.py）- 添加和管理动画效果
- 转场服务（transition_service.py）- 添加和管理转场效果

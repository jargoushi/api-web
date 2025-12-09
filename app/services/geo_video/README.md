# 地理视频生成服务

基于 GeoJSON 地图数据和方言音频，自动生成带运镜效果的地理信息视频。

## 功能特性

- ✅ 支持从全国 GeoJSON 数据中筛选指定省份/城市
- ✅ 自动生成地图底图和城市高亮图层
- ✅ 自动计算运镜参数（缩放和位置）
- ✅ 根据音频时长自动调整场景时长
- ✅ 支持从视频中提取音频
- ✅ 生成剪映可编辑的草稿文件

## 模块结构

```
geo_video/
├── __init__.py              # 模块导出
├── models.py                # 数据模型
├── geo_processor.py         # GeoJSON 处理
├── asset_generator.py       # 素材生成（地图、高亮）
├── camera_calculator.py     # 运镜计算
├── draft_builder.py         # 草稿组装
├── video_utils.py           # 视频工具（提取音频等）
├── pipeline.py              # 完整流程编排
└── README.md               # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
uv add geopandas matplotlib shapely mutagen

# 安装 ffmpeg（用于音频处理）
# Windows: 下载 https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### 2. 准备数据

```
materials/geo_video/
├── geojson/
│   └── china.geojson        # 中国地图数据
└── audios/
    ├── hefei.mp3            # 合肥方言音频
    ├── wuhu.mp3             # 芜湖方言音频
    └── huangshan.mp3        # 黄山方言音频
```

### 3. 运行示例

```bash
python examples/geo_video_example.py
```

## 使用示例

### 示例 1：生成地理视频

```python
import asyncio
from app.services.geo_video import GeoVideoPipeline
from app.services.geo_video.models import VideoScript, Scene

async def main():
    # 创建流程
    pipeline = GeoVideoPipeline("中国geo.json")

    # 配置视频脚本
    script_config = VideoScript(
        video_title="安徽方言视频",
        geojson_path="中国geo.json",
        province_name="安徽省",
        resolution={"width": 1080, "height": 1920},
        scenes=[
            Scene(
                city_name="合肥市",
                pinyin="hefei",
                audio_path="materials/geo_video/audios/hefei.mp3",
                subtitle_text="合肥姑娘说话温柔...",
                transition_duration=1.5
            ),
            # 更多场景...
        ]
    )

    # 生成视频
    draft_path = await pipeline.generate_video(
        script_config=script_config,
        draft_name="我的地理视频"
    )

    print(f"草稿已保存: {draft_path}")

asyncio.run(main())
```

### 示例 2：从视频提取音频

```python
from app.services.geo_video import VideoUtils

# 提取音频
audio_path = VideoUtils.extract_audio_from_video(
    video_path="video.mp4",
    output_path="audio.mp3"
)

# 获取音频时长
duration = VideoUtils.get_audio_duration(audio_path)
print(f"音频时长: {duration:.2f} 秒")
```

### 示例 3：列出可用城市

```python
from app.services.geo_video import GeoVideoPipeline

pipeline = GeoVideoPipeline("中国geo.json")

# 列出安徽省的所有城市
cities = pipeline.list_available_cities("安徽省")
for city in cities:
    print(f"{city['name']} - {city['adcode']}")
```

## 配置说明

### VideoScript 配置

```python
VideoScript(
    video_title="视频标题",
    geojson_path="GeoJSON文件路径",
    province_name="省份名称",  # 如 "安徽省"
    resolution={"width": 1080, "height": 1920},  # 竖屏
    scenes=[...],  # 场景列表
    subtitle_style={  # 字幕样式（可选）
        "font_size": 60,
        "color": [1.0, 1.0, 1.0],  # RGB (0-1)
        "stroke_width": 2,
        "position": "bottom"
    },
    highlight_style={  # 高亮样式（可选）
        "color": "#ff6b6b",
        "opacity": 0.6
    }
)
```

### Scene 配置

```python
Scene(
    city_name="城市名称",  # 如 "合肥市"
    pinyin="拼音",  # 如 "hefei"
    audio_path="音频文件路径",
    subtitle_text="字幕文本",
    transition_duration=1.5,  # 运镜过渡时长（秒）
    audio_duration=None  # 自动获取，无需手动设置
)
```

## 工作流程

1. **加载 GeoJSON 数据** - 读取中国地图数据
2. **筛选省份/城市** - 根据配置筛选目标区域
3. **获取音频时长** - 自动读取所有音频文件的时长
4. **生成底图** - 绘制省份地图底图
5. **生成高亮图层** - 为每个城市生成透明高亮图层
6. **计算运镜参数** - 计算缩放和位置关键帧
7. **构建草稿** - 组装多轨道剪映草稿
8. **保存草稿** - 保存到剪映草稿文件夹

## 运镜效果

- **初始状态**: 省份全景视图
- **过渡效果**: 平滑缩放到目标城市
- **过渡时长**: 可配置（默认 1.5 秒）
- **插值方式**: 线性插值（pyJianYingDraft 默认）

## 注意事项

1. **GeoJSON 数据格式**

   - 必须包含 `name`、`adcode`、`geometry` 字段
   - 支持 MultiPolygon 几何类型

2. **音频文件**

   - 支持 MP3、MP4、M4A 格式
   - 自动获取时长，无需手动配置

3. **ffmpeg 依赖**

   - 提取音频功能需要 ffmpeg
   - 确保 ffmpeg 已添加到系统 PATH

4. **剪映版本**
   - 支持剪映专业版 5.0+
   - 草稿文件保存到剪映草稿文件夹

## 常见问题

### Q: 如何获取 GeoJSON 数据？

A: 可以从以下来源获取：

- 阿里云 DataV: http://datav.aliyun.com/portal/school/atlas/area_selector
- GitHub: 搜索 "china geojson"

### Q: 运镜效果不明显？

A: 调整以下参数：

- 增加 `transition_duration`（过渡时长）
- 调整 `padding` 参数（在 CameraCalculator 中）

### Q: 如何添加更多城市？

A: 在 `scenes` 列表中添加更多 `Scene` 对象即可。

### Q: 支持其他省份吗？

A: 支持！只需修改 `province_name` 参数，如 "浙江省"、"江苏省" 等。

## 后续扩展

- [ ] 支持自定义地图样式（卫星图、简约风格等）
- [ ] 支持缓动函数（ease-in/ease-out）
- [ ] 支持自定义字体和字幕位置
- [ ] 支持批量生成多个省份视频
- [ ] 支持导出视频（集成 export_service）

## 技术栈

- **geopandas**: GeoJSON 数据处理
- **matplotlib**: 地图绘制
- **shapely**: 几何计算
- **mutagen**: 音频元数据读取
- **ffmpeg**: 音视频处理
- **pyJianYingDraft**: 剪映草稿生成

## 许可证

MIT

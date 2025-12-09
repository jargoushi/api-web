"""
数据模型定义
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Point:
    """坐标点"""
    x: float
    y: float


@dataclass
class Bounds:
    """边界框"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def center(self) -> Point:
        return Point(
            x=(self.min_x + self.max_x) / 2,
            y=(self.min_y + self.max_y) / 2
        )


@dataclass
class CityInfo:
    """城市信息"""
    name: str
    adcode: int
    centroid: Point
    bounds: Bounds
    geometry: any  # GeoDataFrame geometry


@dataclass
class CameraParams:
    """运镜参数"""
    scale: float  # 缩放比例
    position_x: float  # X轴位置（剪映坐标系）
    position_y: float  # Y轴位置（剪映坐标系）


@dataclass
class Scene:
    """场景配置"""
    city_name: str
    pinyin: str
    audio_path: str
    subtitle_text: str
    transition_duration: float = 1.0  # 运镜过渡时长（秒）
    audio_duration: Optional[float] = None  # 音频时长（秒）


@dataclass
class VideoScript:
    """视频脚本配置"""
    video_title: str
    geojson_path: str
    province_name: str  # 省份名称，用于筛选
    resolution: Dict[str, int]  # {"width": 1080, "height": 1920}
    scenes: List[Scene]

    # 样式配置
    subtitle_style: Dict = None
    highlight_style: Dict = None

    def __post_init__(self):
        if self.subtitle_style is None:
            self.subtitle_style = {
                "font_size": 60,
                "color": [1.0, 1.0, 1.0],
                "stroke_width": 2,
                "position": "bottom"
            }

        if self.highlight_style is None:
            self.highlight_style = {
                "color": "#ff6b6b",
                "opacity": 0.6
            }

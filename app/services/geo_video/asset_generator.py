"""
素材生成服务 - 生成地图底图和高亮图层
"""
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List
import geopandas as gpd
from .geo_processor import GeoProcessor


class AssetGenerator:
    """素材生成器"""

    def __init__(self, geo_processor: GeoProcessor):
        """
        初始化生成器

        Args:
            geo_processor: GeoJSON 处理器
        """
        self.geo_processor = geo_processor

    def generate_base_map(
        self,
        province_name: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        background_color: str = "#1a1a2e",
        border_color: str = "#ffffff",
        border_width: float = 1.0
    ) -> str:
        """
        生成省份底图

        Args:
            province_name: 省份名称
            output_path: 输出文件路径
            width: 图片宽度（像素）
            height: 图片高度（像素）
            background_color: 背景颜色
            border_color: 边框颜色
            border_width: 边框宽度

        Returns:
            输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取省份数据
        cities = self.geo_processor.filter_by_province(province_name)

        # 计算 DPI（保持高分辨率）
        dpi = 100
        fig_width = width / dpi
        fig_height = height / dpi

        # 创建图形
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        ax.set_aspect('equal')

        # 设置背景色
        fig.patch.set_facecolor(background_color)
        ax.set_facecolor(background_color)

        # 绘制所有城市边界
        cities.boundary.plot(
            ax=ax,
            color=border_color,
            linewidth=border_width
        )

        # 移除坐标轴
        ax.axis('off')

        # 调整布局，移除边距
        plt.tight_layout(pad=0)

        # 保存图片
        plt.savefig(
            output_path,
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0,
            facecolor=background_color
        )
        plt.close()

        return str(output_path)

    def generate_highlight_layer(
        self,
        province_name: str,
        city_name: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        highlight_color: str = "#ff6b6b",
        opacity: float = 0.6
    ) -> str:
        """
        生成城市高亮图层（透明背景）

        Args:
            province_name: 省份名称
            city_name: 城市名称
            output_path: 输出文件路径
            width: 图片宽度
            height: 图片高度
            highlight_color: 高亮颜色
            opacity: 不透明度

        Returns:
            输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取城市信息
        city_info = self.geo_processor.get_city_info(city_name, province_name)

        # 获取省份边界（用于设置相同的坐标范围）
        cities = self.geo_processor.filter_by_province(province_name)
        province_bounds = cities.total_bounds  # (minx, miny, maxx, maxy)

        # 计算 DPI
        dpi = 100
        fig_width = width / dpi
        fig_height = height / dpi

        # 创建图形（透明背景）
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        ax.set_aspect('equal')

        # 设置透明背景
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

        # 设置坐标范围与底图一致
        ax.set_xlim(province_bounds[0], province_bounds[2])
        ax.set_ylim(province_bounds[1], province_bounds[3])

        # 绘制高亮城市
        gpd.GeoSeries([city_info.geometry]).plot(
            ax=ax,
            color=highlight_color,
            alpha=opacity
        )

        # 移除坐标轴
        ax.axis('off')

        # 调整布局
        plt.tight_layout(pad=0)

        # 保存为 PNG（支持透明度）
        plt.savefig(
            output_path,
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0,
            transparent=True
        )
        plt.close()

        return str(output_path)

    def batch_generate_highlights(
        self,
        province_name: str,
        city_names: List[str],
        output_dir: str,
        **kwargs
    ) -> Dict[str, str]:
        """
        批量生成城市高亮图层

        Args:
            province_name: 省份名称
            city_names: 城市名称列表
            output_dir: 输出目录
            **kwargs: 传递给 generate_highlight_layer 的其他参数

        Returns:
            城市名称到文件路径的映射
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {}

        for city_name in city_names:
            # 生成文件名（使用城市名的拼音或简化名）
            filename = f"{city_name.replace('市', '').replace('省', '')}_highlight.png"
            output_path = output_dir / filename

            # 生成高亮图层
            path = self.generate_highlight_layer(
                province_name=province_name,
                city_name=city_name,
                output_path=str(output_path),
                **kwargs
            )

            result[city_name] = path

        return result

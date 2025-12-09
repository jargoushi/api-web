"""
GeoJSON 数据处理服务
"""
import json
from pathlib import Path
from typing import List, Optional, Dict
import geopandas as gpd
from shapely.geometry import shape
from .models import CityInfo, Point, Bounds


class GeoProcessor:
    """GeoJSON 数据处理器"""

    def __init__(self, geojson_path: str):
        """
        初始化处理器

        Args:
            geojson_path: GeoJSON 文件路径
        """
        self.geojson_path = Path(geojson_path)
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self._load_geojson()

    def _load_geojson(self):
        """加载 GeoJSON 数据"""
        if not self.geojson_path.exists():
            raise FileNotFoundError(f"GeoJSON 文件不存在: {self.geojson_path}")

        # 读取 GeoJSON
        with open(self.geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 转换为 GeoDataFrame
        features = []
        for feature in data['features']:
            geom = shape(feature['geometry'])
            props = feature['properties']
            features.append({
                'geometry': geom,
                'name': props.get('name', ''),
                'adcode': props.get('adcode', 0),
                'level': props.get('level', ''),
                'center': props.get('center', []),
                'centroid': props.get('centroid', [])
            })

        self.gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')

    def filter_by_province(self, province_name: str) -> gpd.GeoDataFrame:
        """
        按省份名称筛选数据

        Args:
            province_name: 省份名称（如"安徽省"）

        Returns:
            筛选后的 GeoDataFrame
        """
        # 查找省份
        province = self.gdf[self.gdf['name'] == province_name]

        if not province.empty:
            # 找到了省份级别的数据
            province_adcode = province.iloc[0]['adcode']

            # 筛选该省份下的所有城市（adcode 前两位相同）
            province_prefix = str(province_adcode)[:2]
            cities = self.gdf[
                (self.gdf['adcode'].astype(str).str.startswith(province_prefix)) &
                (self.gdf['level'] == 'city')
            ]

            return cities
        else:
            # 没有找到省份，可能数据中直接是城市级别
            # 检查是否所有数据都是城市级别（或district级别）
            if len(self.gdf) > 0 and all(self.gdf['level'].isin(['city', 'district'])):
                # 返回所有城市数据（这种情况下，文件本身就是某个省份的城市数据）
                return self.gdf
            else:
                raise ValueError(f"未找到省份: {province_name}")

    def get_city_info(self, city_name: str, province_name: Optional[str] = None) -> CityInfo:
        """
        获取城市信息

        Args:
            city_name: 城市名称（如"合肥市"）
            province_name: 省份名称（可选，用于精确匹配）

        Returns:
            城市信息对象
        """
        # 如果指定了省份，先筛选省份
        if province_name:
            gdf = self.filter_by_province(province_name)
        else:
            gdf = self.gdf

        # 查找城市
        city = gdf[gdf['name'] == city_name]

        if city.empty:
            raise ValueError(f"未找到城市: {city_name}")

        city_data = city.iloc[0]
        geometry = city_data['geometry']

        # 计算边界
        bounds = self._calculate_bounds(geometry)

        # 计算中心点
        centroid = self._calculate_centroid(geometry)

        return CityInfo(
            name=city_data['name'],
            adcode=city_data['adcode'],
            centroid=centroid,
            bounds=bounds,
            geometry=geometry
        )

    def _calculate_bounds(self, geometry) -> Bounds:
        """计算几何体的边界框"""
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        return Bounds(
            min_x=bounds[0],
            min_y=bounds[1],
            max_x=bounds[2],
            max_y=bounds[3]
        )

    def _calculate_centroid(self, geometry) -> Point:
        """计算几何体的中心点"""
        centroid = geometry.centroid
        return Point(x=centroid.x, y=centroid.y)

    def get_province_bounds(self, province_name: str) -> Bounds:
        """
        获取整个省份的边界框

        Args:
            province_name: 省份名称

        Returns:
            省份边界框
        """
        cities = self.filter_by_province(province_name)

        # 合并所有城市的几何体
        union_geom = cities.geometry.unary_union

        return self._calculate_bounds(union_geom)

    def list_cities(self, province_name: str) -> List[Dict[str, any]]:
        """
        列出省份下的所有城市

        Args:
            province_name: 省份名称

        Returns:
            城市列表
        """
        cities = self.filter_by_province(province_name)

        result = []
        for _, city in cities.iterrows():
            result.append({
                'name': city['name'],
                'adcode': city['adcode'],
                'center': city.get('center', []),
            })

        return result

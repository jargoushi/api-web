"""
GeoJSON 数据管理服务

自动从在线 API 获取中国各省市的地理数据
"""
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List
import time


class GeoDataManager:
    """GeoJSON 数据管理器"""

    # 阿里云 DataV 的 GeoJSON API
    BASE_URL = "https://geo.datav.aliyun.com/areas_v3/bound"

    def __init__(self, cache_dir: str = "materials/geo_video/geojson"):
        """
        初始化数据管理器

        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 从配置文件加载行政区划代码
        self.adcodes = self._load_adcodes()

    def _load_adcodes(self) -> Dict[str, str]:
        """
        从配置文件加载行政区划代码

        Returns:
            行政区划代码字典
        """
        config_file = Path(__file__).parent / "adcode_config.json"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('adcodes', {})
        except FileNotFoundError:
            print(f"⚠️  配置文件不存在: {config_file}")
            print("提示: 运行 'python update_adcode_config.py' 生成配置文件")
            # 返回默认配置
            return {"中国": "100000"}
        except Exception as e:
            print(f"⚠️  加载配置文件失败: {e}")
            return {"中国": "100000"}

    def get_adcode(self, province_name: str) -> Optional[str]:
        """
        获取省份的行政区划代码

        Args:
            province_name: 省份名称

        Returns:
            行政区划代码，如果未找到返回 None
        """
        return self.adcodes.get(province_name)

    def reload_adcodes(self) -> bool:
        """
        重新加载行政区划代码配置

        Returns:
            是否加载成功
        """
        try:
            self.adcodes = self._load_adcodes()
            print(f"✓ 已重新加载 {len(self.adcodes)} 个行政区划代码")
            return True
        except Exception as e:
            print(f"✗ 重新加载失败: {e}")
            return False

    def download_geojson(
        self,
        province_name: str,
        force_update: bool = False
    ) -> str:
        """
        下载省份的 GeoJSON 数据

        Args:
            province_name: 省份名称（如 "安徽省"）
            force_update: 是否强制更新（忽略缓存）

        Returns:
            GeoJSON 文件路径
        """
        # 检查缓存
        cache_file = self.cache_dir / f"{province_name}.json"
        if cache_file.exists() and not force_update:
            print(f"✓ 使用缓存: {cache_file}")
            return str(cache_file)

        # 获取行政区划代码
        adcode = self.get_adcode(province_name)
        if not adcode:
            raise ValueError(f"未找到省份 '{province_name}' 的行政区划代码")

        print(f"📥 正在下载 {province_name} 的 GeoJSON 数据...")

        # 下载省级边界（包含所有城市）
        url = f"{self.BASE_URL}/{adcode}_full.json"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # 保存到缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✓ 下载成功: {cache_file}")
            return str(cache_file)

        except requests.RequestException as e:
            raise RuntimeError(f"下载 GeoJSON 数据失败: {e}")

    def download_city_geojson(
        self,
        province_name: str,
        city_name: str,
        force_update: bool = False
    ) -> str:
        """
        下载城市的 GeoJSON 数据

        Args:
            province_name: 省份名称
            city_name: 城市名称
            force_update: 是否强制更新

        Returns:
            GeoJSON 文件路径
        """
        # 先获取省级数据
        province_file = self.download_geojson(province_name, force_update)

        # 从省级数据中提取城市数据
        with open(province_file, 'r', encoding='utf-8') as f:
            province_data = json.load(f)

        # 查找城市
        city_feature = None
        for feature in province_data.get('features', []):
            if feature['properties']['name'] == city_name:
                city_feature = feature
                break

        if not city_feature:
            raise ValueError(f"在 {province_name} 中未找到城市 '{city_name}'")

        # 保存城市数据
        city_file = self.cache_dir / f"{province_name}_{city_name}.json"
        city_data = {
            "type": "FeatureCollection",
            "features": [city_feature]
        }

        with open(city_file, 'w', encoding='utf-8') as f:
            json.dump(city_data, f, ensure_ascii=False, indent=2)

        print(f"✓ 提取城市数据: {city_file}")
        return str(city_file)

    def list_cities(self, province_name: str) -> List[Dict]:
        """
        列出省份下的所有城市

        Args:
            province_name: 省份名称

        Returns:
            城市列表
        """
        # 获取省级数据
        province_file = self.download_geojson(province_name)

        with open(province_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cities = []
        for feature in data.get('features', []):
            props = feature['properties']
            cities.append({
                'name': props['name'],
                'adcode': props['adcode'],
                'center': props.get('center', []),
                'level': props.get('level', 'city')
            })

        return cities

    def batch_download(
        self,
        province_names: List[str],
        force_update: bool = False
    ) -> Dict[str, str]:
        """
        批量下载多个省份的数据

        Args:
            province_names: 省份名称列表
            force_update: 是否强制更新

        Returns:
            省份名称到文件路径的映射
        """
        result = {}

        for i, province_name in enumerate(province_names, 1):
            print(f"\n[{i}/{len(province_names)}] {province_name}")
            try:
                file_path = self.download_geojson(province_name, force_update)
                result[province_name] = file_path

                # 避免请求过快
                if i < len(province_names):
                    time.sleep(0.5)

            except Exception as e:
                print(f"✗ 下载失败: {e}")

        return result

    def get_available_provinces(self) -> List[str]:
        """
        获取所有可用的省份列表

        Returns:
            省份名称列表
        """
        return list(self.adcodes.keys())

    def get_config_info(self) -> Dict:
        """
        获取配置文件信息

        Returns:
            配置信息字典
        """
        config_file = Path(__file__).parent / "adcode_config.json"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {
                    "version": config.get("version", "unknown"),
                    "last_updated": config.get("last_updated", "unknown"),
                    "source": config.get("source", "unknown"),
                    "count": len(config.get("adcodes", {}))
                }
        except Exception as e:
            return {
                "error": str(e),
                "count": len(self.adcodes)
            }

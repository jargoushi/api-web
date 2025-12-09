"""
完整流程编排 - 地理视频生成管道
"""
import os
from pathlib import Path
from typing import Optional
from .models import VideoScript, Scene
from .geo_processor import GeoProcessor
from .asset_generator import AssetGenerator
from .camera_calculator import CameraCalculator
from .draft_builder import GeoDraftBuilder
from .video_utils import VideoUtils


class GeoVideoPipeline:
    """地理视频生成流程"""

    def __init__(self, geojson_path: str):
        """
        初始化流程

        Args:
            geojson_path: GeoJSON 文件路径
        """
        self.geojson_path = geojson_path
        self.geo_processor = GeoProcessor(geojson_path)

    async def generate_video(
        self,
        script_config: VideoScript,
        draft_name: str,
        output_dir: Optional[str] = None
    ) -> str:
        """
        生成视频草稿（完整流程）

        Args:
            script_config: 视频脚本配置
            draft_name: 草稿名称
            output_dir: 输出目录（可选）

        Returns:
            草稿保存路径
        """
        if output_dir is None:
            output_dir = Path("materials/geo_video/output")
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"🚀 开始生成地理视频: {draft_name}")
        print(f"📍 省份: {script_config.province_name}")
        print(f"🎬 场景数: {len(script_config.scenes)}")

        # 1. 自动获取音频时长
        print("\n📊 步骤 1/5: 获取音频时长...")
        await self._load_audio_durations(script_config)

        # 2. 生成底图
        print("\n🗺️  步骤 2/5: 生成省份底图...")
        base_map_path = await self._generate_base_map(
            script_config,
            output_dir
        )
        print(f"   ✓ 底图已生成: {base_map_path}")

        # 3. 生成高亮图层
        print("\n✨ 步骤 3/5: 生成城市高亮图层...")
        highlight_paths = await self._generate_highlights(
            script_config,
            output_dir
        )
        print(f"   ✓ 已生成 {len(highlight_paths)} 个高亮图层")

        # 4. 构建草稿
        print("\n🎞️  步骤 4/5: 构建剪映草稿...")
        script = await self._build_draft(
            script_config,
            draft_name,
            base_map_path,
            highlight_paths
        )
        print(f"   ✓ 草稿构建完成")

        # 5. 保存草稿
        print("\n💾 步骤 5/5: 保存草稿...")
        script.save()
        draft_path = script.save_path
        print(f"   ✓ 草稿已保存: {draft_path}")

        print(f"\n✅ 视频生成完成！")
        print(f"📂 可以在剪映中打开草稿: {draft_name}")

        return draft_path

    async def _load_audio_durations(self, script_config: VideoScript):
        """自动获取所有音频的时长"""
        for scene in script_config.scenes:
            if scene.audio_duration is None:
                try:
                    duration = VideoUtils.get_audio_duration(scene.audio_path)
                    scene.audio_duration = duration
                    print(f"   ✓ {scene.city_name}: {duration:.2f}秒")
                except Exception as e:
                    print(f"   ✗ {scene.city_name}: 获取时长失败 - {e}")
                    raise

    async def _generate_base_map(
        self,
        script_config: VideoScript,
        output_dir: Path
    ) -> str:
        """生成底图"""
        asset_gen = AssetGenerator(self.geo_processor)

        base_map_path = output_dir / "base_maps" / f"{script_config.province_name}_base.png"

        return asset_gen.generate_base_map(
            province_name=script_config.province_name,
            output_path=str(base_map_path),
            width=script_config.resolution['width'],
            height=script_config.resolution['height']
        )

    async def _generate_highlights(
        self,
        script_config: VideoScript,
        output_dir: Path
    ) -> dict:
        """生成所有城市的高亮图层"""
        asset_gen = AssetGenerator(self.geo_processor)

        city_names = [scene.city_name for scene in script_config.scenes]
        highlights_dir = output_dir / "highlights"

        highlight_style = script_config.highlight_style

        return asset_gen.batch_generate_highlights(
            province_name=script_config.province_name,
            city_names=city_names,
            output_dir=str(highlights_dir),
            width=script_config.resolution['width'],
            height=script_config.resolution['height'],
            highlight_color=highlight_style.get('color', '#ff6b6b'),
            opacity=highlight_style.get('opacity', 0.6)
        )

    async def _build_draft(
        self,
        script_config: VideoScript,
        draft_name: str,
        base_map_path: str,
        highlight_paths: dict
    ):
        """构建草稿"""
        camera_calc = CameraCalculator(
            canvas_width=script_config.resolution['width'],
            canvas_height=script_config.resolution['height']
        )

        draft_builder = GeoDraftBuilder(
            geo_processor=self.geo_processor,
            camera_calculator=camera_calc
        )

        return await draft_builder.build_draft(
            script_config=script_config,
            draft_name=draft_name,
            base_map_path=base_map_path,
            highlight_paths=highlight_paths
        )

    def list_available_cities(self, province_name: str) -> list:
        """
        列出可用的城市

        Args:
            province_name: 省份名称

        Returns:
            城市列表
        """
        return self.geo_processor.list_cities(province_name)

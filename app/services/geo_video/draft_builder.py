"""
草稿组装服务 - 使用 pyJianYingDraft 构建剪映草稿
"""
import sys
from pathlib import Path
from typing import List

# 添加 pyJianYingDraft 到路径
project_root = Path(__file__).parent.parent.parent.parent
pyjy_path = project_root / "pyJianYingDraft_source"
if str(pyjy_path) not in sys.path:
    sys.path.insert(0, str(pyjy_path))

from pyJianYingDraft import ScriptFile, DraftFolder
from pyJianYingDraft.time_util import tim, Timerange
import os

from .models import VideoScript, Scene, CameraParams
from .geo_processor import GeoProcessor
from .camera_calculator import CameraCalculator


class GeoDraftBuilder:
    """地理视频草稿构建器"""

    def __init__(
        self,
        geo_processor: GeoProcessor,
        camera_calculator: CameraCalculator
    ):
        """
        初始化构建器

        Args:
            geo_processor: GeoJSON 处理器
            camera_calculator: 运镜计算器
        """
        self.geo_processor = geo_processor
        self.camera_calculator = camera_calculator

    async def build_draft(
        self,
        script_config: VideoScript,
        draft_name: str,
        base_map_path: str,
        highlight_paths: dict
    ) -> ScriptFile:
        """
        构建完整草稿

        Args:
            script_config: 视频脚本配置
            draft_name: 草稿名称
            base_map_path: 底图路径
            highlight_paths: 城市高亮图层路径映射

        Returns:
            剪映草稿对象
        """
        width = script_config.resolution['width']
        height = script_config.resolution['height']

        # 获取剪映草稿文件夹路径
        draft_folder_path = os.getenv('JIANYING_DRAFT_FOLDER')
        if not draft_folder_path:
            # 使用默认路径
            draft_folder_path = os.path.join(
                os.path.expanduser('~'),
                'AppData', 'Local', 'JianyingPro', 'User Data', 'Projects', 'com.lveditor.draft'
            )

        # 创建 DraftFolder 管理器
        draft_folder = DraftFolder(draft_folder_path)

        # 创建草稿
        script = draft_folder.create_draft(
            draft_name=draft_name,
            width=width,
            height=height,
            fps=30,
            maintrack_adsorb=True,
            allow_replace=True  # 允许覆盖同名草稿
        )

        # 计算总时长
        total_duration_us = 0
        for scene in script_config.scenes:
            if scene.audio_duration:
                total_duration_us += int(scene.audio_duration * 1_000_000)

        # 添加底图（背景轨道）
        await self._add_base_map(script, base_map_path, total_duration_us)

        # 添加场景（音频、高亮、字幕）
        current_time_us = 0
        province_bounds = self.geo_processor.get_province_bounds(
            script_config.province_name
        )

        # 初始运镜参数（省份全景）
        prev_params = self.camera_calculator.calculate_province_view(province_bounds)

        for i, scene in enumerate(script_config.scenes):
            scene_duration_us = int(scene.audio_duration * 1_000_000)
            transition_duration_us = int(scene.transition_duration * 1_000_000)

            # 获取城市信息
            city_info = self.geo_processor.get_city_info(
                scene.city_name,
                script_config.province_name
            )

            # 计算目标运镜参数
            target_params = self.camera_calculator.calculate_city_view(
                city_info.bounds
            )

            # 添加音频
            await self._add_audio(
                script,
                scene.audio_path,
                current_time_us,
                scene_duration_us
            )

            # 添加高亮图层
            await self._add_highlight(
                script,
                highlight_paths[scene.city_name],
                current_time_us,
                scene_duration_us
            )

            # 添加字幕
            await self._add_subtitle(
                script,
                scene.subtitle_text,
                current_time_us,
                scene_duration_us,
                script_config.subtitle_style
            )

            # 添加运镜关键帧（在过渡时间内完成）
            if i == 0:
                # 第一个场景：从省份全景过渡到城市特写
                transition_end = current_time_us + transition_duration_us
            else:
                # 后续场景：从上一个城市过渡到当前城市
                transition_end = current_time_us + transition_duration_us

            # TODO: 将关键帧应用到底图片段
            # 这需要访问底图的 VideoSegment 对象
            # 暂时跳过，在后续版本中实现

            # 更新时间和参数
            current_time_us += scene_duration_us
            prev_params = target_params

        return script

    async def _add_base_map(
        self,
        script: ScriptFile,
        image_path: str,
        duration_us: int
    ):
        """添加底图到背景轨道"""
        from pyJianYingDraft import VideoMaterial, VideoSegment
        from pyJianYingDraft.track import TrackType

        # 创建视频轨道
        script.add_track(TrackType.video, "背景", relative_index=0)

        # 创建视频素材
        material = VideoMaterial(image_path)
        script.add_material(material)

        # 创建视频片段
        segment = VideoSegment(
            material=material,
            target_timerange=Timerange(start=0, duration=duration_us)
        )

        # 添加片段到轨道
        script.add_segment(segment, "背景")

    async def _add_audio(
        self,
        script: ScriptFile,
        audio_path: str,
        start_time_us: int,
        duration_us: int
    ):
        """添加音频"""
        from pyJianYingDraft import AudioMaterial, AudioSegment
        from pyJianYingDraft.track import TrackType

        # 创建音频轨道（如果不存在）
        if "音频" not in script.tracks:
            script.add_track(TrackType.audio, "音频", relative_index=0)

        # 创建音频素材
        material = AudioMaterial(audio_path)
        script.add_material(material)

        # 创建音频片段
        segment = AudioSegment(
            material=material,
            target_timerange=Timerange(start=start_time_us, duration=duration_us)
        )

        # 添加片段到轨道
        script.add_segment(segment, "音频")

    async def _add_highlight(
        self,
        script: ScriptFile,
        image_path: str,
        start_time_us: int,
        duration_us: int
    ):
        """添加高亮图层"""
        from pyJianYingDraft import VideoMaterial, VideoSegment
        from pyJianYingDraft.track import TrackType

        # 创建高亮轨道（如果不存在）
        if "高亮" not in script.tracks:
            script.add_track(TrackType.video, "高亮", relative_index=1)

        # 创建视频素材
        material = VideoMaterial(image_path)
        script.add_material(material)

        # 创建视频片段
        segment = VideoSegment(
            material=material,
            target_timerange=Timerange(start=start_time_us, duration=duration_us)
        )

        # 添加片段到轨道
        script.add_segment(segment, "高亮")

    async def _add_subtitle(
        self,
        script: ScriptFile,
        text: str,
        start_time_us: int,
        duration_us: int,
        style: dict
    ):
        """添加字幕"""
        from pyJianYingDraft import TextSegment, TextStyle, TextBorder
        from pyJianYingDraft.track import TrackType

        # 创建文本轨道（如果不存在）
        if "字幕" not in script.tracks:
            script.add_track(TrackType.text, "字幕", relative_index=0)

        # 构建文本样式
        text_style_kwargs = {}
        text_border_kwargs = {}

        if style:
            # 字体大小
            if 'font_size' in style:
                text_style_kwargs['size'] = style['font_size']

            # 字体颜色
            if 'color' in style:
                color = style['color']
                if isinstance(color, list) and len(color) == 3:
                    text_style_kwargs['color'] = tuple(color)

            # 描边宽度
            if 'stroke_width' in style:
                text_border_kwargs['width'] = style['stroke_width']

        # 创建样式对象
        text_style = TextStyle(**text_style_kwargs) if text_style_kwargs else None
        text_border = TextBorder(**text_border_kwargs) if text_border_kwargs else None

        # 创建文本片段
        segment = TextSegment(
            text=text,
            timerange=Timerange(start=start_time_us, duration=duration_us),
            style=text_style,
            border=text_border
        )

        # 添加片段到轨道
        script.add_segment(segment, "字幕")

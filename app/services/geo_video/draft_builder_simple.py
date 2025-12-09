"""
简化版草稿组装服务
"""
import sys
import os
from pathlib import Path

# 添加 pyJianYingDraft 到路径
project_root = Path(__file__).parent.parent.parent.parent
pyjy_path = project_root / "pyJianYingDraft_source"
if str(pyjy_path) not in sys.path:
    sys.path.insert(0, str(pyjy_path))

from pyJianYingDraft import DraftFolder, VideoMaterial, AudioMaterial, VideoSegment, AudioSegment, TextSegment
from pyJianYingDraft.track import TrackType
from pyJianYingDraft.time_util import Timerange

from .models import VideoScript


class SimpleDraftBuilder:
    """简化版草稿构建器"""

    async def build_draft(
        self,
        script_config: VideoScript,
        draft_name: str,
        base_map_path: str,
        highlight_paths: dict
    ) -> str:
        """
        构建完整草稿

        Returns:
            草稿保存路径
        """
        width = script_config.resolution['width']
        height = script_config.resolution['height']

        # 获取剪映草稿文件夹路径
        draft_folder_path = os.getenv('JIANYING_DRAFT_FOLDER')
        if not draft_folder_path:
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
            allow_replace=True
        )

        # 计算总时长
        total_duration_us = sum(int(scene.audio_duration * 1_000_000) for scene in script_config.scenes)

        # 1. 添加底图（背景轨道）
        script.add_track(TrackType.video, "背景", relative_index=0)
        base_material = VideoMaterial(base_map_path)
        script.add_material(base_material)
        base_segment = VideoSegment(
            material=base_material,
            target_timerange=Timerange(0, total_duration_us)
        )
        script.add_segment(base_segment, "背景")

        # 2. 添加音频轨道
        script.add_track(TrackType.audio, "音频", relative_index=0)

        # 3. 添加高亮轨道
        script.add_track(TrackType.video, "高亮", relative_index=1)

        # 4. 添加字幕轨道
        script.add_track(TrackType.text, "字幕", relative_index=0)

        # 5. 添加场景
        current_time_us = 0

        for scene in script_config.scenes:
            scene_duration_us = int(scene.audio_duration * 1_000_000)

            # 添加音频
            audio_material = AudioMaterial(scene.audio_path)
            script.add_material(audio_material)
            audio_segment = AudioSegment(
                material=audio_material,
                target_timerange=Timerange(current_time_us, scene_duration_us)
            )
            script.add_segment(audio_segment, "音频")

            # 添加高亮图层
            highlight_path = highlight_paths[scene.city_name]
            highlight_material = VideoMaterial(highlight_path)
            script.add_material(highlight_material)
            highlight_segment = VideoSegment(
                material=highlight_material,
                target_timerange=Timerange(current_time_us, scene_duration_us)
            )
            script.add_segment(highlight_segment, "高亮")

            # 添加字幕
            text_segment = TextSegment(
                text=scene.subtitle_text,
                start_time=current_time_us,
                duration=scene_duration_us
            )

            # 设置字幕样式
            style = script_config.subtitle_style
            if style:
                if 'font_size' in style:
                    text_segment.set_font_size(style['font_size'])
                if 'color' in style:
                    color = style['color']
                    if isinstance(color, list) and len(color) == 3:
                        text_segment.set_font_color(tuple(color))
                if 'stroke_width' in style:
                    text_segment.set_stroke_width(style['stroke_width'])

            script.add_segment(text_segment, "字幕")

            # 更新时间
            current_time_us += scene_duration_us

        # 保存草稿
        script.save()

        return script.save_path

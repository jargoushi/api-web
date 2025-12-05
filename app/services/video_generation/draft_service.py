import sys
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

# 将 pyJianYingDraft 源码路径添加到 sys.path
PYJIANYING_PATH = os.path.join(os.path.dirname(__file__), "../../../pyJianYingDraft_source")
if PYJIANYING_PATH not in sys.path:
    sys.path.insert(0, PYJIANYING_PATH)

import pyJianYingDraft as draft
from pyJianYingDraft import trange, SEC

from app.core.config import settings
from app.core.logging import log
from app.core.exceptions import BusinessException


class DraftService:
    """
    剪映草稿生成服务

    负责创建和管理剪映草稿，包括添加素材、特效、字幕等
    """

    def __init__(self):
        """初始化服务"""
        self.draft_folder_path = getattr(settings, 'JIANYING_DRAFT_FOLDER', None)
        if not self.draft_folder_path:
            log.warning("未配置剪映草稿文件夹路径，部分功能将不可用")
        self.draft_folder = None

    def _ensure_draft_folder(self):
        """确保草稿文件夹已初始化"""
        if not self.draft_folder_path:
            raise BusinessException(message="未配置剪映草稿文件夹路径")

        if not self.draft_folder:
            self.draft_folder = draft.DraftFolder(self.draft_folder_path)

        return self.draft_folder

    async def create_draft(
        self,
        name: str,
        width: int = 1920,
        height: int = 1080
    ) -> Any:
        """
        创建新草稿

        Args:
            name: 草稿名称
            width: 视频宽度
            height: 视频高度

        Returns:
            草稿对象

        Raises:
            BusinessException: 创建失败
        """
        try:
            log.info(f"创建剪映草稿：{name}，分辨率：{width}x{height}")
            folder = self._ensure_draft_folder()
            script = folder.create_draft(name, width, height, allow_replace=True)

            # 添加默认轨道：音频、视频、文本
            script.add_track(draft.TrackType.audio).add_track(draft.TrackType.video).add_track(draft.TrackType.text)

            log.info(f"草稿 {name} 创建成功")
            return script
        except Exception as e:
            log.error(f"创建草稿失败：{str(e)}")
            raise BusinessException(message=f"创建草稿失败：{str(e)}")

    async def create_from_template(
        self,
        template_name: str,
        new_name: str
    ) -> Any:
        """
        从模板创建草稿

        Args:
            template_name: 模板草稿名称
            new_name: 新草稿名称

        Returns:
            草稿对象

        Raises:
            BusinessException: 创建失败
        """
        try:
            log.info(f"从模板 {template_name} 创建草稿：{new_name}")
            folder = self._ensure_draft_folder()
            script = folder.duplicate_as_template(template_name, new_name)
            log.info(f"草稿 {new_name} 从模板创建成功")
            return script
        except Exception as e:
            log.error(f"从模板创建草稿失败：{str(e)}")
            raise BusinessException(message=f"从模板创建草稿失败：{str(e)}")

    async def add_video_segment(
        self,
        script: Any,
        video_path: str,
        start_time: str = "0s",
        duration: Optional[str] = None,
        track_name: Optional[str] = None,
        speed: float = 1.0
    ) -> Any:
        """
        添加视频片段

        Args:
            script: 草稿对象
            video_path: 视频文件路径
            start_time: 片段开始时间
            duration: 片段持续时长（不指定则使用整个视频）
            track_name: 轨道名称
            speed: 播放速度

        Returns:
            视频片段对象

        Raises:
            BusinessException: 添加失败
        """
        try:
            log.info(f"添加视频片段：{video_path}")

            # 创建视频素材
            material = draft.VideoMaterial(video_path)

            # 计算时间范围
            if duration:
                target_range = trange(start_time, duration)
            else:
                target_range = trange(start_time, material.duration)

            # 创建视频片段
            segment = draft.VideoSegment(material, target_range, speed=speed)

            # 添加到轨道
            if track_name:
                script.add_segment(segment, track_name)
            else:
                script.add_segment(segment)

            log.info(f"视频片段添加成功")
            return segment
        except Exception as e:
            log.error(f"添加视频片段失败：{str(e)}")
            raise BusinessException(message=f"添加视频片段失败：{str(e)}")

    async def add_audio_segment(
        self,
        script: Any,
        audio_path: str,
        start_time: str = "0s",
        duration: Optional[str] = None,
        track_name: Optional[str] = None,
        volume: float = 1.0
    ) -> Any:
        """
        添加音频片段

        Args:
            script: 草稿对象
            audio_path: 音频文件路径
            start_time: 片段开始时间
            duration: 片段持续时长
            track_name: 轨道名称
            volume: 音量（0.0-1.0）

        Returns:
            音频片段对象

        Raises:
            BusinessException: 添加失败
        """
        try:
            log.info(f"添加音频片段：{audio_path}")

            material = draft.AudioMaterial(audio_path)

            if duration:
                target_range = trange(start_time, duration)
            else:
                target_range = trange(start_time, material.duration)

            segment = draft.AudioSegment(material, target_range)

            # 设置音量
            if volume != 1.0:
                segment.add_keyframe("0s", volume)

            if track_name:
                script.add_segment(segment, track_name)
            else:
                script.add_segment(segment)

            log.info(f"音频片段添加成功")
            return segment
        except Exception as e:
            log.error(f"添加音频片段失败：{str(e)}")
            raise BusinessException(message=f"添加音频片段失败：{str(e)}")

    async def add_text_segment(
        self,
        script: Any,
        text: str,
        start_time: str = "0s",
        duration: str = "5s",
        track_name: Optional[str] = None,
        font_type: Optional[Any] = None,
        style: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        添加文本片段

        Args:
            script: 草稿对象
            text: 文本内容
            start_time: 开始时间
            duration: 持续时长
            track_name: 轨道名称
            font_type: 字体类型
            style: 文本样式

        Returns:
            文本片段对象

        Raises:
            BusinessException: 添加失败
        """
        try:
            log.info(f"添加文本片段：{text[:20]}...")

            target_range = trange(start_time, duration)

            # 构建文本样式
            text_style = None
            if style:
                text_style = draft.TextStyle(**style)

            segment = draft.TextSegment(
                text,
                target_range,
                font=font_type,
                style=text_style
            )

            if track_name:
                script.add_segment(segment, track_name)
            else:
                script.add_segment(segment)

            log.info(f"文本片段添加成功")
            return segment
        except Exception as e:
            log.error(f"添加文本片段失败：{str(e)}")
            raise BusinessException(message=f"添加文本片段失败：{str(e)}")

    async def import_subtitle(
        self,
        script: Any,
        srt_path: str,
        track_name: str = "subtitle",
        time_offset: str = "0s",
        style: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        导入字幕文件

        Args:
            script: 草稿对象
            srt_path: SRT字幕文件路径
            track_name: 轨道名称
            time_offset: 时间偏移
            style: 字幕样式

        Raises:
            BusinessException: 导入失败
        """
        try:
            log.info(f"导入字幕文件：{srt_path}")

            text_style = None
            if style:
                text_style = draft.TextStyle(**style)

            script.import_srt(
                srt_path,
                track_name=track_name,
                time_offset=time_offset,
                text_style=text_style
            )

            log.info(f"字幕导入成功")
        except Exception as e:
            log.error(f"导入字幕失败：{str(e)}")
            raise BusinessException(message=f"导入字幕失败：{str(e)}")

    async def add_track(
        self,
        script: Any,
        track_type: str,
        track_name: str,
        relative_index: int = 1
    ) -> None:
        """
        添加轨道

        Args:
            script: 草稿对象
            track_type: 轨道类型（video/audio/text/effect/filter）
            track_name: 轨道名称
            relative_index: 相对位置

        Raises:
            BusinessException: 添加失败
        """
        try:
            log.info(f"添加轨道：{track_name}，类型：{track_type}")

            # 转换轨道类型
            track_type_enum = getattr(draft.TrackType, track_type)

            script.add_track(
                track_type_enum,
                track_name=track_name,
                relative_index=relative_index
            )

            log.info(f"轨道添加成功")
        except Exception as e:
            log.error(f"添加轨道失败：{str(e)}")
            raise BusinessException(message=f"添加轨道失败：{str(e)}")

    async def save_draft(self, script: Any) -> None:
        """
        保存草稿

        Args:
            script: 草稿对象

        Raises:
            BusinessException: 保存失败
        """
        try:
            log.info(f"保存草稿")
            script.save()
            log.info(f"草稿保存成功")
        except Exception as e:
            log.error(f"保存草稿失败：{str(e)}")
            raise BusinessException(message=f"保存草稿失败：{str(e)}")


# 创建服务实例
draft_service = DraftService()

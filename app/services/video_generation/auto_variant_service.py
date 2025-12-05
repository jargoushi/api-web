"""
自动多版本视频生成服务

根据一个视频素材，自动生成多个不同的剪辑版本
"""
import sys
import os
from typing import List, Dict, Any, Optional
import random
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
from app.services.video_generation.draft_service import draft_service
from app.services.video_generation.material_manager import material_manager


class AutoVariantService:
    """
    自动多版本视频生成服务

    根据一个视频素材，自动生成多个不同的剪辑版本
    包括：不同开头结尾、字幕风格、背景音乐、特效等
    """

    def __init__(self):
        """初始化服务"""
        self.draft_service = draft_service
        self.material_manager = material_manager

        # 预定义的变体配置
        self.variant_configs = {
            "openings": [
                {"text": "🔥 精彩内容即将开始", "duration": "3s", "style": {"size": 8.0, "color": (1.0, 0.2, 0.2)}},
                {"text": "✨ 今日推荐", "duration": "2s", "style": {"size": 10.0, "color": (1.0, 0.8, 0.0)}},
                {"text": "🎬 精选视频", "duration": "2.5s", "style": {"size": 9.0, "color": (0.2, 0.8, 1.0)}},
                {"text": "💎 不容错过", "duration": "3s", "style": {"size": 7.5, "color": (0.8, 0.2, 1.0)}},
                {"text": "🚀 热门推荐", "duration": "2s", "style": {"size": 8.5, "color": (0.2, 1.0, 0.2)}}
            ],
            "endings": [
                {"text": "👍 喜欢请点赞关注", "duration": "3s", "style": {"size": 6.0, "color": (1.0, 1.0, 1.0)}},
                {"text": "🔔 更多精彩内容请关注", "duration": "3s", "style": {"size": 5.5, "color": (1.0, 0.8, 0.0)}},
                {"text": "💬 评论区见", "duration": "2s", "style": {"size": 7.0, "color": (0.2, 0.8, 1.0)}},
                {"text": "📱 分享给朋友吧", "duration": "2.5s", "style": {"size": 6.5, "color": (0.8, 0.2, 1.0)}},
                {"text": "🎉 感谢观看", "duration": "2s", "style": {"size": 8.0, "color": (1.0, 0.2, 0.2)}}
            ],
            "subtitle_styles": [
                {"name": "经典白字", "style": {"size": 5.0, "color": (1.0, 1.0, 1.0)}},
                {"name": "活力橙色", "style": {"size": 5.5, "color": (1.0, 0.5, 0.0)}},
                {"name": "清新蓝色", "style": {"size": 5.0, "color": (0.2, 0.6, 1.0)}},
                {"name": "温暖黄色", "style": {"size": 5.2, "color": (1.0, 0.8, 0.2)}},
                {"name": "神秘紫色", "style": {"size": 4.8, "color": (0.8, 0.2, 1.0)}}
            ],
            "background_music_moods": [
                "轻松愉快", "激情澎湃", "温馨感人", "神秘悬疑", "清新自然"
            ]
        }

    async def generate_variants(
        self,
        source_video_path: str,
        base_name: str,
        variant_count: int = 5,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        生成多个视频变体

        Args:
            source_video_path: 源视频文件路径
            base_name: 基础名称
            variant_count: 生成变体数量
            custom_config: 自定义配置

        Returns:
            生成的变体信息列表

        Raises:
            BusinessException: 生成失败
        """
        try:
            log.info(f"开始生成 {variant_count} 个视频变体，基于：{source_video_path}")

            # 检查源视频是否存在
            if not os.path.exists(source_video_path):
                log.warning(f"源视频文件不存在：{source_video_path}，将创建仅包含文本的草稿")

            variants = []

            for i in range(variant_count):
                variant_name = f"{base_name}_变体{i+1}"
                log.info(f"生成变体 {i+1}/{variant_count}：{variant_name}")

                # 生成变体配置
                variant_config = self._generate_variant_config(custom_config)

                # 创建草稿
                script = await self.draft_service.create_draft(variant_name, 1920, 1080)

                # 添加开头
                if variant_config.get("opening"):
                    await self._add_opening(script, variant_config["opening"])

                # 添加主视频（如果存在）
                if os.path.exists(source_video_path):
                    main_video_start = variant_config.get("opening_duration", "3s")
                    await self._add_video(script, source_video_path, main_video_start, variant_config)

                # 添加字幕（如果有）
                if variant_config.get("subtitle_style"):
                    main_video_start = variant_config.get("opening_duration", "3s")
                    await self._add_subtitle_with_style(
                        script,
                        variant_config["subtitle_style"],
                        main_video_start
                    )

                # 添加背景音乐（如果有）
                if variant_config.get("background_music_mood"):
                    main_video_start = variant_config.get("opening_duration", "3s")
                    await self._add_background_music(
                        script,
                        variant_config["background_music_mood"],
                        main_video_start
                    )

                # 添加结尾
                if variant_config.get("ending"):
                    await self._add_ending(script, variant_config["ending"])

                # 保存草稿
                await self.draft_service.save_draft(script)

                # 记录变体信息
                variant_info = {
                    "name": variant_name,
                    "config": variant_config,
                    "script": script
                }
                variants.append(variant_info)

                log.info(f"变体 {variant_name} 生成完成")

            log.info(f"所有 {variant_count} 个变体生成完成")
            return variants

        except Exception as e:
            log.error(f"生成视频变体失败：{str(e)}")
            raise BusinessException(message=f"生成视频变体失败：{str(e)}")

    def _generate_variant_config(self, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成变体配置

        Args:
            custom_config: 自定义配置

        Returns:
            变体配置字典
        """
        config = {
            "opening": random.choice(self.variant_configs["openings"]),
            "ending": random.choice(self.variant_configs["endings"]),
            "subtitle_style": random.choice(self.variant_configs["subtitle_styles"]),
            "background_music_mood": random.choice(self.variant_configs["background_music_moods"]),
            "video_speed": random.choice([0.8, 0.9, 1.0, 1.1, 1.2]),
            "opening_duration": random.choice(["2s", "2.5s", "3s"]),
            "ending_duration": random.choice(["2s", "2.5s", "3s"])
        }

        # 应用自定义配置
        if custom_config:
            config.update(custom_config)

        return config

    async def _add_opening(self, script: Any, opening_config: Dict[str, Any]) -> None:
        """
        添加开头

        Args:
            script: 草稿对象
            opening_config: 开头配置
        """
        await self.draft_service.add_text_segment(
            script,
            opening_config["text"],
            start_time="0s",
            duration=opening_config["duration"],
            track_name="text",
            style=opening_config["style"]
        )

    async def _add_ending(self, script: Any, ending_config: Dict[str, Any]) -> None:
        """
        添加结尾

        Args:
            script: 草稿对象
            ending_config: 结尾配置
        """
        # 简化处理，假设在30秒后添加结尾
        await self.draft_service.add_text_segment(
            script,
            ending_config["text"],
            start_time="30s",
            duration=ending_config["duration"],
            track_name="text",
            style=ending_config["style"]
        )

    async def _add_video(
        self,
        script: Any,
        video_path: str,
        start_time: str,
        config: Dict[str, Any]
    ) -> None:
        """
        添加视频

        Args:
            script: 草稿对象
            video_path: 视频路径
            start_time: 开始时间
            config: 配置
        """
        try:
            await self.draft_service.add_video_segment(
                script,
                video_path,
                start_time=start_time,
                speed=config.get("video_speed", 1.0),
                track_name="video"
            )
        except Exception as e:
            log.warning(f"添加视频失败：{str(e)}")

    async def _add_subtitle_with_style(
        self,
        script: Any,
        subtitle_config: Dict[str, Any],
        start_time: str = "0s"
    ) -> None:
        """
        添加带样式的字幕

        Args:
            script: 草稿对象
            subtitle_config: 字幕配置
            start_time: 开始时间
        """
        # 检查是否有字幕文件
        subtitles = await self.material_manager.list_materials("subtitle", pattern=".srt")

        if subtitles:
            # 使用第一个找到的字幕文件
            subtitle_path = subtitles[0]['path']
            try:
                await self.draft_service.import_subtitle(
                    script,
                    subtitle_path,
                    track_name="text",
                    time_offset=start_time,
                    style=subtitle_config["style"]
                )
            except Exception as e:
                log.warning(f"导入字幕失败：{str(e)}")
        else:
            # 如果没有字幕文件，添加示例字幕
            try:
                await self.draft_service.add_text_segment(
                    script,
                    "这是示例字幕",
                    start_time=start_time,
                    duration="5s",
                    track_name="text",
                    style=subtitle_config["style"]
                )
            except Exception as e:
                log.warning(f"添加示例字幕失败：{str(e)}")

    async def _add_background_music(
        self,
        script: Any,
        music_mood: str,
        start_time: str = "0s"
    ) -> None:
        """
        添加背景音乐

        Args:
            script: 草稿对象
            music_mood: 音乐风格
            start_time: 开始时间
        """
        # 检查是否有音频文件
        audios = await self.material_manager.list_materials("audio", pattern=".mp3")

        if audios:
            # 随机选择一个音频文件
            audio_file = random.choice(audios)
            try:
                await self.draft_service.add_audio_segment(
                    script,
                    audio_file['path'],
                    start_time=start_time,
                    track_name="audio",
                    volume=0.3  # 降低音量作为背景音乐
                )
            except Exception as e:
                log.warning(f"添加背景音乐失败：{str(e)}")

    async def generate_themed_variants(
        self,
        source_video_path: str,
        base_name: str,
        themes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        生成主题化变体

        Args:
            source_video_path: 源视频文件路径
            base_name: 基础名称
            themes: 主题列表（如：\"商务\", \"活泼\", \"温馨\", \"科技\", \"复古\"）

        Returns:
            生成的主题变体信息列表

        Raises:
            BusinessException: 生成失败
        """
        try:
            log.info(f"开始生成 {len(themes)} 个主题变体")

            theme_configs = {
                "商务": {
                    "opening": {"text": "📊 专业内容", "duration": "2s", "style": {"size": 6.0, "color": (0.2, 0.2, 0.8)}},
                    "ending": {"text": "💼 感谢观看", "duration": "2s", "style": {"size": 5.0, "color": (0.2, 0.2, 0.8)}},
                    "subtitle_style": {"name": "商务蓝", "style": {"size": 4.5, "color": (0.2, 0.4, 0.8)}},
                    "video_speed": 1.0
                },
                "活泼": {
                    "opening": {"text": "🎉 超级有趣", "duration": "2s", "style": {"size": 8.0, "color": (1.0, 0.2, 0.5)}},
                    "ending": {"text": "🌟 记得点赞哦", "duration": "3s", "style": {"size": 6.0, "color": (1.0, 0.2, 0.5)}},
                    "subtitle_style": {"name": "活力粉", "style": {"size": 5.5, "color": (1.0, 0.3, 0.6)}},
                    "video_speed": 1.1
                },
                "温馨": {
                    "opening": {"text": "💕 温暖时光", "duration": "3s", "style": {"size": 7.0, "color": (1.0, 0.7, 0.3)}},
                    "ending": {"text": "🏠 家的感觉", "duration": "3s", "style": {"size": 5.5, "color": (1.0, 0.7, 0.3)}},
                    "subtitle_style": {"name": "温暖橙", "style": {"size": 5.0, "color": (1.0, 0.6, 0.2)}},
                    "video_speed": 0.9
                },
                "科技": {
                    "opening": {"text": "🚀 未来科技", "duration": "2s", "style": {"size": 7.5, "color": (0.0, 1.0, 0.8)}},
                    "ending": {"text": "⚡ 科技改变生活", "duration": "2.5s", "style": {"size": 5.0, "color": (0.0, 1.0, 0.8)}},
                    "subtitle_style": {"name": "科技绿", "style": {"size": 4.8, "color": (0.2, 1.0, 0.6)}},
                    "video_speed": 1.2
                },
                "复古": {
                    "opening": {"text": "📼 经典回忆", "duration": "3s", "style": {"size": 6.5, "color": (0.8, 0.6, 0.2)}},
                    "ending": {"text": "🎞️ 怀旧时光", "duration": "3s", "style": {"size": 5.5, "color": (0.8, 0.6, 0.2)}},
                    "subtitle_style": {"name": "复古金", "style": {"size": 5.2, "color": (0.9, 0.7, 0.3)}},
                    "video_speed": 0.8
                }
            }

            variants = []

            for theme in themes:
                if theme not in theme_configs:
                    log.warning(f"未知主题：{theme}，跳过")
                    continue

                variant_name = f"{base_name}_{theme}版"
                log.info(f"生成主题变体：{variant_name}")

                # 使用主题配置生成变体
                theme_config = theme_configs[theme]
                variants_result = await self.generate_variants(
                    source_video_path,
                    variant_name,
                    variant_count=1,
                    custom_config=theme_config
                )

                variants.extend(variants_result)

            log.info(f"所有主题变体生成完成，共 {len(variants)} 个")
            return variants

        except Exception as e:
            log.error(f"生成主题变体失败：{str(e)}")
            raise BusinessException(message=f"生成主题变体失败：{str(e)}")


# 创建服务实例
auto_variant_service = AutoVariantService()

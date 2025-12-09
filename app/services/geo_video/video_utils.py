"""
视频处理工具类
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Union
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4


class AudioSegment:
    """音频片段配置"""
    def __init__(
        self,
        start_time: Union[str, float],
        end_time: Union[str, float],
        output_name: str
    ):
        """
        初始化音频片段

        Args:
            start_time: 开始时间（秒或时间格式 "HH:MM:SS"）
            end_time: 结束时间（秒或时间格式 "HH:MM:SS"）
            output_name: 输出文件名（不含扩展名）
        """
        self.start_time = self._parse_time(start_time)
        self.end_time = self._parse_time(end_time)
        self.output_name = output_name

    @staticmethod
    def _parse_time(time_value: Union[str, float]) -> float:
        """解析时间为秒数"""
        if isinstance(time_value, (int, float)):
            return float(time_value)

        # 解析 "HH:MM:SS" 或 "MM:SS" 格式
        parts = time_value.split(':')
        if len(parts) == 3:  # HH:MM:SS
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:  # MM:SS
            m, s = parts
            return int(m) * 60 + float(s)
        else:
            return float(time_value)

    @property
    def duration(self) -> float:
        """获取片段时长"""
        return self.end_time - self.start_time


class VideoUtils:
    """视频处理工具类"""

    @staticmethod
    def extract_audio_from_video(
        video_path: str,
        output_path: Optional[str] = None,
        audio_format: str = "mp3"
    ) -> str:
        """
        从视频文件中提取音频

        Args:
            video_path: 视频文件路径
            output_path: 输出音频文件路径（可选）
            audio_format: 音频格式，默认 mp3

        Returns:
            输出的音频文件路径

        命名规则：
            - 如果未指定 output_path，则自动生成
            - 格式：{原文件名}_audio.{格式}
            - 例如：video.mp4 -> video_audio.mp3
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # 自动生成输出路径
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_audio.{audio_format}"
        else:
            output_path = Path(output_path)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用 ffmpeg 提取音频
        try:
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # 不处理视频
                '-acodec', 'libmp3lame' if audio_format == 'mp3' else 'copy',
                '-y',  # 覆盖已存在的文件
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            return str(output_path)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"音频提取失败: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "未找到 ffmpeg 命令。请确保已安装 ffmpeg 并添加到系统 PATH。\n"
                "安装方法：https://ffmpeg.org/download.html"
            )

    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        """
        获取音频文件时长（秒）

        Args:
            audio_path: 音频文件路径

        Returns:
            音频时长（秒）
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        suffix = audio_path.suffix.lower()

        try:
            if suffix == '.mp3':
                audio = MP3(audio_path)
                return audio.info.length
            elif suffix in ['.mp4', '.m4a']:
                audio = MP4(audio_path)
                return audio.info.length
            else:
                # 使用 ffmpeg 作为后备方案
                return VideoUtils._get_duration_with_ffmpeg(str(audio_path))
        except Exception as e:
            raise RuntimeError(f"获取音频时长失败: {e}")

    @staticmethod
    def _get_duration_with_ffmpeg(file_path: str) -> float:
        """使用 ffmpeg 获取媒体文件时长"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            return float(result.stdout.strip())

        except Exception as e:
            raise RuntimeError(f"使用 ffmpeg 获取时长失败: {e}")

    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        获取视频文件信息

        Args:
            video_path: 视频文件路径

        Returns:
            包含视频信息的字典
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,duration,r_frame_rate',
                '-of', 'json',
                str(video_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            import json
            data = json.loads(result.stdout)
            stream = data['streams'][0]

            return {
                'width': int(stream.get('width', 0)),
                'height': int(stream.get('height', 0)),
                'duration': float(stream.get('duration', 0)),
                'fps': eval(stream.get('r_frame_rate', '30/1'))
            }

        except Exception as e:
            raise RuntimeError(f"获取视频信息失败: {e}")

    @staticmethod
    def split_audio(
        audio_path: str,
        segments: List['AudioSegment'],
        output_dir: Optional[str] = None,
        audio_format: str = "mp3"
    ) -> Dict[str, str]:
        """
        分割音频文件为多个片段

        Args:
            audio_path: 源音频文件路径
            segments: 音频片段列表
            output_dir: 输出目录（可选，默认为源文件所在目录）
            audio_format: 输出音频格式，默认 mp3

        Returns:
            片段名称到文件路径的映射

        示例:
            from app.services.geo_video.video_utils import AudioSegment, VideoUtils

            segments = [
                AudioSegment(start_time=0, end_time=10, output_name="hefei"),
                AudioSegment(start_time="00:00:10", end_time="00:00:20", output_name="wuhu"),
                AudioSegment(start_time=20, end_time=30, output_name="huangshan"),
            ]

            result = VideoUtils.split_audio("audio.mp3", segments)
            # 返回: {"hefei": "path/to/hefei.mp3", ...}
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        # 确定输出目录
        if output_dir is None:
            output_dir = audio_path.parent
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        result = {}

        for i, segment in enumerate(segments, 1):
            # 生成输出文件路径
            output_filename = f"{segment.output_name}.{audio_format}"
            output_path = output_dir / output_filename

            print(f"  [{i}/{len(segments)}] 分割片段: {segment.output_name}")
            print(f"      时间: {segment.start_time:.2f}s - {segment.end_time:.2f}s (时长: {segment.duration:.2f}s)")

            try:
                # 使用 ffmpeg 分割音频
                cmd = [
                    'ffmpeg',
                    '-i', str(audio_path),
                    '-ss', str(segment.start_time),  # 开始时间
                    '-to', str(segment.end_time),    # 结束时间
                    '-acodec', 'libmp3lame' if audio_format == 'mp3' else 'copy',
                    '-y',  # 覆盖已存在的文件
                    str(output_path)
                ]

                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                result[segment.output_name] = str(output_path)
                print(f"      ✓ 已保存: {output_path}")

            except subprocess.CalledProcessError as e:
                print(f"      ✗ 分割失败: {e.stderr}")
                raise RuntimeError(f"音频分割失败: {e.stderr}")

        return result

    @staticmethod
    def split_audio_by_duration(
        audio_path: str,
        segment_duration: float,
        output_dir: Optional[str] = None,
        name_prefix: str = "segment",
        audio_format: str = "mp3"
    ) -> Dict[str, str]:
        """
        按固定时长分割音频

        Args:
            audio_path: 源音频文件路径
            segment_duration: 每个片段的时长（秒）
            output_dir: 输出目录
            name_prefix: 输出文件名前缀
            audio_format: 输出音频格式

        Returns:
            片段名称到文件路径的映射

        示例:
            # 将音频按每10秒分割
            result = VideoUtils.split_audio_by_duration("audio.mp3", 10)
            # 返回: {"segment_1": "path/to/segment_1.mp3", ...}
        """
        # 获取音频总时长
        total_duration = VideoUtils.get_audio_duration(audio_path)

        # 计算需要分割的片段数
        num_segments = int(total_duration / segment_duration) + 1

        # 生成片段列表
        segments = []
        for i in range(num_segments):
            start_time = i * segment_duration
            end_time = min((i + 1) * segment_duration, total_duration)

            if start_time >= total_duration:
                break

            segments.append(AudioSegment(
                start_time=start_time,
                end_time=end_time,
                output_name=f"{name_prefix}_{i+1}"
            ))

        print(f"\n将音频分割为 {len(segments)} 个片段（每段 {segment_duration} 秒）")

        return VideoUtils.split_audio(
            audio_path=audio_path,
            segments=segments,
            output_dir=output_dir,
            audio_format=audio_format
        )

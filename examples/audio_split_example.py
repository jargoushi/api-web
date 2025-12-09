"""
音频分割示例

演示如何使用 VideoUtils 分割音频文件
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo_video import VideoUtils, AudioSegment


def example_1_split_by_time_ranges():
    """示例1: 按指定时间范围分割音频"""
    print("=" * 60)
    print("示例1: 按指定时间范围分割音频")
    print("=" * 60)

    # 源音频文件
    audio_file = "materials/geo_video/audios/reference_full.mp3"

    if not Path(audio_file).exists():
        print(f"❌ 错误: 未找到音频文件 {audio_file}")
        print("请先运行 quick_start.py 提取音频")
        return

    # 获取音频时长
    duration = VideoUtils.get_audio_duration(audio_file)
    print(f"\n源音频时长: {duration:.2f} 秒")

    # 定义分割规则
    segments = [
        AudioSegment(
            start_time=0,           # 开始时间（秒）
            end_time=10,            # 结束时间（秒）
            output_name="hefei"     # 输出文件名
        ),
        AudioSegment(
            start_time=10,
            end_time=20,
            output_name="wuhu"
        ),
        AudioSegment(
            start_time=20,
            end_time=30,
            output_name="huangshan"
        ),
    ]

    print(f"\n将分割为 {len(segments)} 个片段:")
    for seg in segments:
        print(f"  - {seg.output_name}: {seg.start_time}s - {seg.end_time}s")

    # 执行分割
    print("\n开始分割...")
    result = VideoUtils.split_audio(
        audio_path=audio_file,
        segments=segments,
        output_dir="materials/geo_video/audios"
    )

    print(f"\n✅ 分割完成！生成了 {len(result)} 个文件:")
    for name, path in result.items():
        duration = VideoUtils.get_audio_duration(path)
        print(f"  - {name}: {path} ({duration:.2f}秒)")


def example_2_split_by_time_format():
    """示例2: 使用时间格式（HH:MM:SS）分割"""
    print("\n" + "=" * 60)
    print("示例2: 使用时间格式分割")
    print("=" * 60)

    audio_file = "materials/geo_video/audios/reference_full.mp3"

    if not Path(audio_file).exists():
        print(f"❌ 错误: 未找到音频文件 {audio_file}")
        return

    # 使用时间格式定义分割规则
    segments = [
        AudioSegment(
            start_time="00:00:00",  # HH:MM:SS 格式
            end_time="00:00:10",
            output_name="part1"
        ),
        AudioSegment(
            start_time="00:00:10",
            end_time="00:00:20",
            output_name="part2"
        ),
        AudioSegment(
            start_time="00:00:20",
            end_time="00:00:30",
            output_name="part3"
        ),
    ]

    print(f"\n将分割为 {len(segments)} 个片段")

    result = VideoUtils.split_audio(
        audio_path=audio_file,
        segments=segments,
        output_dir="materials/geo_video/audios/parts"
    )

    print(f"\n✅ 分割完成！")


def example_3_split_by_duration():
    """示例3: 按固定时长自动分割"""
    print("\n" + "=" * 60)
    print("示例3: 按固定时长自动分割")
    print("=" * 60)

    audio_file = "materials/geo_video/audios/reference_full.mp3"

    if not Path(audio_file).exists():
        print(f"❌ 错误: 未找到音频文件 {audio_file}")
        return

    # 获取音频时长
    duration = VideoUtils.get_audio_duration(audio_file)
    print(f"\n源音频时长: {duration:.2f} 秒")

    # 按每10秒自动分割
    segment_duration = 10  # 秒

    print(f"\n将按每 {segment_duration} 秒自动分割")

    result = VideoUtils.split_audio_by_duration(
        audio_path=audio_file,
        segment_duration=segment_duration,
        output_dir="materials/geo_video/audios/auto_split",
        name_prefix="segment"
    )

    print(f"\n✅ 分割完成！生成了 {len(result)} 个文件:")
    for name, path in result.items():
        seg_duration = VideoUtils.get_audio_duration(path)
        print(f"  - {name}: {seg_duration:.2f}秒")


def example_4_custom_split():
    """示例4: 自定义分割（混合使用秒和时间格式）"""
    print("\n" + "=" * 60)
    print("示例4: 自定义分割（实际场景）")
    print("=" * 60)

    audio_file = "materials/geo_video/audios/reference_full.mp3"

    if not Path(audio_file).exists():
        print(f"❌ 错误: 未找到音频文件 {audio_file}")
        return

    # 实际场景：根据方言内容手动标记时间点
    segments = [
        AudioSegment(
            start_time=0,
            end_time=8.5,           # 可以使用小数
            output_name="hefei"
        ),
        AudioSegment(
            start_time=8.5,
            end_time="00:00:17.2",  # 也可以混合使用
            output_name="wuhu"
        ),
        AudioSegment(
            start_time=17.2,
            end_time=25,
            output_name="huangshan"
        ),
    ]

    print("\n自定义分割规则:")
    for seg in segments:
        print(f"  - {seg.output_name}: {seg.start_time:.2f}s - {seg.end_time:.2f}s (时长: {seg.duration:.2f}s)")

    result = VideoUtils.split_audio(
        audio_path=audio_file,
        segments=segments,
        output_dir="materials/geo_video/audios"
    )

    print(f"\n✅ 分割完成！")


def main():
    """运行示例"""
    print("\n🎵 音频分割工具 - 使用示例\n")
    print("请选择示例:")
    print("1. 按指定时间范围分割（秒）")
    print("2. 使用时间格式分割（HH:MM:SS）")
    print("3. 按固定时长自动分割")
    print("4. 自定义分割（实际场景）")
    print("5. 运行所有示例")

    choice = input("\n请输入选项 (1-5): ").strip()

    if choice == "1":
        example_1_split_by_time_ranges()
    elif choice == "2":
        example_2_split_by_time_format()
    elif choice == "3":
        example_3_split_by_duration()
    elif choice == "4":
        example_4_custom_split()
    elif choice == "5":
        example_1_split_by_time_ranges()
        example_2_split_by_time_format()
        example_3_split_by_duration()
        example_4_custom_split()
    else:
        print("无效选项")


if __name__ == "__main__":
    main()

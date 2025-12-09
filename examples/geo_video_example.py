"""
地理视频生成示例

演示如何使用地理视频生成服务创建方言视频
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.geo_video import GeoVideoPipeline
from app.services.geo_video.models import VideoScript, Scene


async def example_anhui_dialect():
    """示例：安徽方言视频"""
    print("=" * 60)
    print("地理视频生成示例 - 安徽方言视频")
    print("=" * 60)

    # GeoJSON 文件路径
    geojson_path = "中国geo.json"

    if not Path(geojson_path).exists():
        print(f"❌ 错误: 未找到 GeoJSON 文件: {geojson_path}")
        print("请确保文件存在于项目根目录")
        return

    # 创建流程
    pipeline = GeoVideoPipeline(geojson_path)

    # 列出安徽省的所有城市
    print("\n📋 安徽省可用城市:")
    cities = pipeline.list_available_cities("安徽省")
    for city in cities[:5]:  # 只显示前5个
        print(f"   - {city['name']} (adcode: {city['adcode']})")
    print(f"   ... 共 {len(cities)} 个城市\n")

    # 配置视频脚本（最小可用版本：3个城市）
    script_config = VideoScript(
        video_title="安徽哪里的姑娘说话最温柔？",
        geojson_path=geojson_path,
        province_name="安徽省",
        resolution={"width": 1080, "height": 1920},
        scenes=[
            Scene(
                city_name="合肥市",
                pinyin="hefei",
                audio_path="materials/geo_video/audios/hefei.mp3",
                subtitle_text="我们合肥小大姐都长在花里的...",
                transition_duration=1.5
            ),
            Scene(
                city_name="芜湖市",
                pinyin="wuhu",
                audio_path="materials/geo_video/audios/wuhu.mp3",
                subtitle_text="芜湖的姑娘说话温柔又好听...",
                transition_duration=1.5
            ),
            Scene(
                city_name="黄山市",
                pinyin="huangshan",
                audio_path="materials/geo_video/audios/huangshan.mp3",
                subtitle_text="黄山姑娘的声音像山泉一样清澈...",
                transition_duration=1.5
            ),
        ],
        subtitle_style={
            "font_size": 60,
            "color": [1.0, 1.0, 1.0],
            "stroke_width": 2,
            "position": "bottom"
        },
        highlight_style={
            "color": "#ff6b6b",
            "opacity": 0.6
        }
    )

    # 检查音频文件是否存在
    print("🔍 检查音频文件...")
    missing_files = []
    for scene in script_config.scenes:
        if not Path(scene.audio_path).exists():
            missing_files.append(scene.audio_path)
            print(f"   ⚠️  缺失: {scene.audio_path}")

    if missing_files:
        print(f"\n❌ 错误: 缺少 {len(missing_files)} 个音频文件")
        print("请将音频文件放置到指定路径，或使用 VideoUtils 从视频中提取音频")
        print("\n示例代码:")
        print("from app.services.geo_video import VideoUtils")
        print("VideoUtils.extract_audio_from_video('video.mp4', 'output.mp3')")
        return

    # 生成视频
    try:
        draft_path = await pipeline.generate_video(
            script_config=script_config,
            draft_name="安徽方言视频_测试",
            output_dir="materials/geo_video/output"
        )

        print(f"\n🎉 成功！草稿已保存到: {draft_path}")
        print("\n📝 后续步骤:")
        print("1. 打开剪映专业版")
        print("2. 在草稿列表中找到 '安徽方言视频_测试'")
        print("3. 预览效果并导出视频")

    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()


async def example_extract_audio():
    """示例：从视频中提取音频"""
    print("=" * 60)
    print("视频工具示例 - 提取音频")
    print("=" * 60)

    from app.services.geo_video import VideoUtils

    # 示例视频文件
    video_file = "20251204_175900_安徽哪里的姑娘说话最温柔？.mp4"

    if not Path(video_file).exists():
        print(f"❌ 错误: 未找到视频文件: {video_file}")
        return

    try:
        # 提取音频
        print(f"\n🎵 正在从视频中提取音频...")
        audio_path = VideoUtils.extract_audio_from_video(
            video_path=video_file,
            output_path="materials/geo_video/audios/reference_audio.mp3"
        )

        print(f"✓ 音频已提取: {audio_path}")

        # 获取音频时长
        duration = VideoUtils.get_audio_duration(audio_path)
        print(f"✓ 音频时长: {duration:.2f} 秒")

    except Exception as e:
        print(f"❌ 提取失败: {e}")


async def main():
    """运行示例"""
    print("\n请选择示例:")
    print("1. 生成安徽方言视频（需要音频文件）")
    print("2. 从视频中提取音频")

    choice = input("\n请输入选项 (1/2): ").strip()

    if choice == "1":
        await example_anhui_dialect()
    elif choice == "2":
        await example_extract_audio()
    else:
        print("无效选项")


if __name__ == "__main__":
    asyncio.run(main())

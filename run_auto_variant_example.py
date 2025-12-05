"""
自动多版本视频生成示例运行脚本
"""
import sys
import os
import asyncio

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.video_generation.auto_variant_service import auto_variant_service
from app.services.video_generation.material_manager import material_manager


async def example_1_random_variants():
    """示例1: 生成随机变体"""
    print("\n" + "=" * 60)
    print("示例1: 生成随机变体")
    print("=" * 60)

    # 检查是否有视频素材
    videos = await material_manager.list_materials("video", pattern=".mp4")
    if not videos:
        print("⚠️  未找到视频素材，将创建仅包含文本的草稿")
        source_video = "materials/videos/demo.mp4"  # 虚拟路径
    else:
        source_video = videos[0]['path']
        print(f"✓ 使用视频素材: {videos[0]['filename']}")

    try:
        # 生成3个随机变体
        variants = await auto_variant_service.generate_variants(
            source_video_path=source_video,
            base_name="随机变体测试",
            variant_count=3
        )

        print(f"✓ 成功生成 {len(variants)} 个随机变体")

        # 显示变体信息
        for i, variant in enumerate(variants, 1):
            config = variant['config']
            print(f"\n变体 {i}: {variant['name']}")
            print(f"  - 开头: {config['opening']['text']}")
            print(f"  - 结尾: {config['ending']['text']}")
            print(f"  - 字幕风格: {config['subtitle_style']['name']}")
            print(f"  - 视频速度: {config['video_speed']}x")
            print(f"  - 背景音乐风格: {config['background_music_mood']}")

    except Exception as e:
        print(f"✗ 生成随机变体失败: {e}")


async def example_2_themed_variants():
    """示例2: 生成主题化变体"""
    print("\n" + "=" * 60)
    print("示例2: 生成主题化变体")
    print("=" * 60)

    # 检查是否有视频素材
    videos = await material_manager.list_materials("video", pattern=".mp4")
    if not videos:
        print("⚠️  未找到视频素材，将创建仅包含文本的草稿")
        source_video = "materials/videos/demo.mp4"
    else:
        source_video = videos[0]['path']
        print(f"✓ 使用视频素材: {videos[0]['filename']}")

    try:
        # 定义主题
        themes = ["商务", "活泼", "温馨"]

        # 生成主题化变体
        variants = await auto_variant_service.generate_themed_variants(
            source_video_path=source_video,
            base_name="主题变体测试",
            themes=themes
        )

        print(f"✓ 成功生成 {len(variants)} 个主题变体")

        # 显示变体信息
        for variant in variants:
            config = variant['config']
            print(f"\n{variant['name']}:")
            print(f"  - 开头: {config['opening']['text']}")
            print(f"  - 结尾: {config['ending']['text']}")
            print(f"  - 字幕风格: {config['subtitle_style']['name']}")
            print(f"  - 视频速度: {config['video_speed']}x")

    except Exception as e:
        print(f"✗ 生成主题变体失败: {e}")


async def main():
    """运行所有示例"""
    print("=" * 60)
    print("自动多版本视频生成示例")
    print("=" * 60)
    print("\n本示例将演示如何自动生成多个视频变体")
    print("包括：随机变体、主题变体等")

    print("\n💡 提示：")
    print("  - 可以在 materials/videos/ 目录下放入测试视频")
    print("  - 可以在 materials/audios/ 目录下放入背景音乐")
    print("  - 可以在 materials/subtitles/ 目录下放入字幕文件")

    try:
        # 运行示例
        await example_1_random_variants()
        await example_2_themed_variants()

        print("\n" + "=" * 60)
        print("✓ 所有示例运行完成！")
        print("=" * 60)
        print("\n🎬 生成的草稿：")
        print("  - 可以在剪映中查看所有生成的变体草稿")
        print("  - 每个变体都有不同的开头、结尾、字幕风格等")
        print("  - 可以根据需要进一步编辑或直接导出")

    except Exception as e:
        print(f"\n✗ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

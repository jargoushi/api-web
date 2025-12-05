"""
视频生成服务使用示例

展示如何使用视频生成服务创建自动化视频
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.video_generation import (
    draft_service,
    template_manager,
    material_manager,
    export_service
)


async def example_1_basic_draft():
    """示例1: 创建基础草稿"""
    print("\n" + "=" * 60)
    print("示例1: 创建基础草稿")
    print("=" * 60)

    # 创建草稿
    script = await draft_service.create_draft("示例_基础草稿", 1920, 1080)
    print("✓ 草稿创建成功")

    # 添加文本
    await draft_service.add_text_segment(
        script,
        "欢迎使用视频生成服务",
        start_time="0s",
        duration="5s",
        style={
            "size": 8.0,
            "color": (1.0, 1.0, 1.0)
        }
    )
    print("✓ 文本添加成功")

    # 保存草稿
    await draft_service.save_draft(script)
    print("✓ 草稿保存成功")


async def example_2_with_materials():
    """示例2: 使用素材创建视频"""
    print("\n" + "=" * 60)
    print("示例2: 使用素材创建视频")
    print("=" * 60)

    # 检查素材
    videos = await material_manager.list_materials("video", pattern=".mp4")
    if not videos:
        print("⚠️  未找到视频素材，跳过此示例")
        return

    # 创建草稿
    script = await draft_service.create_draft("示例_素材视频", 1920, 1080)
    print("✓ 草稿创建成功")

    # 添加视频
    video_path = videos[0]['path']
    await draft_service.add_video_segment(
        script,
        video_path,
        start_time="0s",
        duration="10s",
        speed=1.0
    )
    print(f"✓ 视频添加成功: {videos[0]['filename']}")

    # 添加标题
    await draft_service.add_text_segment(
        script,
        "这是一个示例视频",
        start_time="0s",
        duration="3s",
        style={
            "size": 10.0,
            "color": (1.0, 0.8, 0.0)
        }
    )
    print("✓ 标题添加成功")

    # 保存草稿
    await draft_service.save_draft(script)
    print("✓ 草稿保存成功")


async def example_3_with_subtitle():
    """示例3: 创建带字幕的视频"""
    print("\n" + "=" * 60)
    print("示例3: 创建带字幕的视频")
    print("=" * 60)

    # 创建测试字幕
    srt_content = """1
00:00:00,000 --> 00:00:03,000
这是第一句字幕

2
00:00:03,000 --> 00:00:06,000
这是第二句字幕

3
00:00:06,000 --> 00:00:09,000
这是第三句字幕
"""
    await material_manager.save_material(
        "subtitle",
        "example_subtitle.srt",
        srt_content.encode('utf-8')
    )
    print("✓ 字幕文件创建成功")

    # 创建草稿
    script = await draft_service.create_draft("示例_字幕视频", 1920, 1080)
    print("✓ 草稿创建成功")

    # 导入字幕
    srt_path = await material_manager.get_material_path("subtitle", "example_subtitle.srt")
    await draft_service.import_subtitle(
        script,
        srt_path,
        track_name="字幕",
        time_offset="0s",
        style={
            "size": 5.0,
            "color": (1.0, 1.0, 1.0)
        }
    )
    print("✓ 字幕导入成功")

    # 保存草稿
    await draft_service.save_draft(script)
    print("✓ 草稿保存成功")


async def example_4_multi_track():
    """示例4: 创建多轨道视频"""
    print("\n" + "=" * 60)
    print("示例4: 创建多轨道视频")
    print("=" * 60)

    # 创建草稿
    script = await draft_service.create_draft("示例_多轨道", 1920, 1080)
    print("✓ 草稿创建成功")

    # 添加多个轨道
    await draft_service.add_track(script, "video", "主视频", relative_index=1)
    await draft_service.add_track(script, "video", "画中画", relative_index=2)
    await draft_service.add_track(script, "audio", "背景音乐", relative_index=1)
    await draft_service.add_track(script, "text", "标题", relative_index=2)
    await draft_service.add_track(script, "text", "字幕", relative_index=1)
    print("✓ 多轨道添加成功")

    # 在不同轨道添加文本
    await draft_service.add_text_segment(
        script,
        "这是标题",
        start_time="0s",
        duration="5s",
        track_name="标题",
        style={"size": 10.0, "color": (1.0, 0.0, 0.0)}
    )

    await draft_service.add_text_segment(
        script,
        "这是字幕",
        start_time="0s",
        duration="5s",
        track_name="字幕",
        style={"size": 5.0, "color": (1.0, 1.0, 1.0)}
    )
    print("✓ 文本添加成功")

    # 保存草稿
    await draft_service.save_draft(script)
    print("✓ 草稿保存成功")


async def example_5_template():
    """示例5: 使用模板创建视频"""
    print("\n" + "=" * 60)
    print("示例5: 使用模板创建视频")
    print("=" * 60)

    try:
        # 从模板创建草稿（使用前面创建的草稿作为模板）
        script = await template_manager.duplicate_template(
            "示例_基础草稿",
            "示例_从模板创建"
        )
        print("✓ 从模板创建草稿成功")

        # 替换文本
        await template_manager.replace_text(
            script,
            track_name="text",
            segment_index=0,
            new_text="这是替换后的文本"
        )
        print("✓ 文本替换成功")

        # 保存草稿
        await draft_service.save_draft(script)
        print("✓ 草稿保存成功")

    except Exception as e:
        print(f"⚠️  模板示例失败: {e}")
        print("   提示: 请先运行示例1创建模板草稿")


async def main():
    """运行所有示例"""
    print("=" * 60)
    print("视频生成服务使用示例")
    print("=" * 60)
    print("\n本示例将演示如何使用视频生成服务")
    print("包括：基础草稿、素材视频、字幕、多轨道、模板等")

    try:
        # 运行所有示例
        await example_1_basic_draft()
        await example_2_with_materials()
        await example_3_with_subtitle()
        await example_4_multi_track()
        await example_5_template()

        print("\n" + "=" * 60)
        print("✓ 所有示例运行完成！")
        print("=" * 60)
        print("\n提示：")
        print("  - 可以在剪映中查看生成的草稿")
        print("  - 修改示例代码以适应你的需求")
        print("  - 查看 README.md 了解更多功能")

    except Exception as e:
        print(f"\n✗ 示例运行失败: {e}")
        print("\n可能的原因:")
        print("  1. 未配置 JIANYING_DRAFT_FOLDER")
        print("  2. 剪映草稿文件夹路径不正确")
        print("  3. 缺少必要的素材文件")


if __name__ == "__main__":
    asyncio.run(main())

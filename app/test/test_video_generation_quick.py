"""
视频生成服务快速测试

快速验证核心功能是否正常
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.video_generation import (
    draft_service,
    material_manager
)


async def quick_test():
    """快速测试"""
    print("=" * 60)
    print("视频生成服务快速测试")
    print("=" * 60)

    # 测试1: 素材管理
    print("\n[1/3] 测试素材管理...")
    try:
        videos = await material_manager.list_materials("video")
        audios = await material_manager.list_materials("audio")
        print(f"✓ 找到 {len(videos)} 个视频, {len(audios)} 个音频")
    except Exception as e:
        print(f"✗ 素材管理测试失败: {e}")
        return

    # 测试2: 创建草稿
    print("\n[2/3] 测试创建草稿...")
    try:
        script = await draft_service.create_draft("快速测试草稿", 1920, 1080)
        print("✓ 草稿创建成功")
    except Exception as e:
        print(f"✗ 创建草稿失败: {e}")
        print("\n可能的原因:")
        print("  1. 未配置 JIANYING_DRAFT_FOLDER")
        print("  2. 剪映草稿文件夹路径不正确")
        print("  3. 没有访问权限")
        return

    # 测试3: 添加文本并保存
    print("\n[3/3] 测试添加文本并保存...")
    try:
        await draft_service.add_text_segment(
            script,
            "快速测试文本",
            start_time="0s",
            duration="5s"
        )
        await draft_service.save_draft(script)
        print("✓ 文本添加并保存成功")
    except Exception as e:
        print(f"✗ 添加文本失败: {e}")
        return

    print("\n" + "=" * 60)
    print("✓ 快速测试全部通过！")
    print("=" * 60)
    print("\n提示：")
    print("  - 可以在剪映中查看 '快速测试草稿'")
    print("  - 运行完整测试: python -m app.test.test_video_generation")


if __name__ == "__main__":
    asyncio.run(quick_test())

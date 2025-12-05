"""
视频导出功能测试脚本
"""
import sys
import os
import asyncio

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.video_generation.export_service import export_service
from app.services.video_generation.draft_service import draft_service


async def test_export():
    """测试导出功能"""
    print("=" * 60)
    print("视频导出功能测试")
    print("=" * 60)

    print("\n⚠️  重要提示：")
    print("  1. 请确保剪映已经打开")
    print("  2. 请确保剪映在【草稿】页面（不是在编辑页面）")
    print("  3. 导出过程中请不要操作剪映")
    print("  4. 导出可能需要几分钟时间，请耐心等待")

    input("\n按 Enter 键开始测试...")

    # 测试草稿列表
    test_drafts = [
        "快速测试草稿",
        "示例_基础草稿",
        "随机变体测试_变体1"
    ]

    print("\n" + "=" * 60)
    print("测试1: 单个草稿导出")
    print("=" * 60)

    draft_name = test_drafts[0]
    export_folder = "./exports"

    # 确保导出文件夹存在
    os.makedirs(export_folder, exist_ok=True)

    print(f"\n准备导出草稿：{draft_name}")
    print(f"导出路径：{export_folder}")
    print(f"分辨率：1080p")
    print(f"帧率：30fps")

    try:
        export_path = await export_service.export_draft(
            draft_name=draft_name,
            export_path=os.path.join(export_folder, f"{draft_name}.mp4"),
            resolution="1080p",
            framerate=30
        )

        print(f"\n✓ 导出成功！")
        print(f"  文件路径：{export_path}")

        # 检查文件是否存在
        if os.path.exists(export_path):
            file_size = os.path.getsize(export_path) / (1024 * 1024)  # MB
            print(f"  文件大小：{file_size:.2f} MB")
        else:
            print(f"  ⚠️  文件不存在，可能导出失败")

    except Exception as e:
        print(f"\n✗ 导出失败：{e}")
        print("\n可能的原因：")
        print("  1. 剪映未打开或不在草稿页面")
        print("  2. 草稿名称不存在")
        print("  3. 导出路径无权限")
        print("  4. 剪映版本不兼容")
        return

    print("\n" + "=" * 60)
    print("测试2: 批量导出（可选）")
    print("=" * 60)

    choice = input("\n是否测试批量导出？(y/n): ")

    if choice.lower() == 'y':
        print(f"\n准备批量导出 {len(test_drafts)} 个草稿...")

        try:
            exported_paths = await export_service.batch_export(
                draft_names=test_drafts,
                export_folder=export_folder,
                resolution="1080p",
                framerate=30
            )

            print(f"\n✓ 批量导出成功！")
            print(f"  共导出 {len(exported_paths)} 个视频")

            for i, path in enumerate(exported_paths, 1):
                if os.path.exists(path):
                    file_size = os.path.getsize(path) / (1024 * 1024)
                    print(f"  {i}. {os.path.basename(path)} ({file_size:.2f} MB)")
                else:
                    print(f"  {i}. {os.path.basename(path)} (文件不存在)")

        except Exception as e:
            print(f"\n✗ 批量导出失败：{e}")
    else:
        print("\n跳过批量导出测试")

    print("\n" + "=" * 60)
    print("✓ 导出功能测试完成！")
    print("=" * 60)

    print("\n📁 导出文件位置：")
    print(f"  {os.path.abspath(export_folder)}")

    print("\n💡 提示：")
    print("  - 可以在导出文件夹中查看生成的视频")
    print("  - 如果导出失败，请检查剪映是否在草稿页面")
    print("  - 导出大文件可能需要较长时间")


async def main():
    """主函数"""
    try:
        await test_export()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n\n测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

"""
批量导出变体视频
"""
import sys
import os
import asyncio

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.video_generation.export_service import export_service


async def export_all_variants():
    """导出所有变体"""
    print("=" * 60)
    print("批量导出变体视频")
    print("=" * 60)

    print("\n⚠️  重要提示：")
    print("  1. 请确保剪映已经打开")
    print("  2. 请确保剪映在【草稿】页面")
    print("  3. 导出过程中请不要操作剪映")
    print("  4. 批量导出可能需要较长时间")

    input("\n按 Enter 键开始批量导出...")

    # 所有变体草稿名称
    variant_drafts = [
        # 随机变体
        "随机变体测试_变体1",
        "随机变体测试_变体2",
        "随机变体测试_变体3",
        # 主题变体
        "主题变体测试_商务版_变体1",
        "主题变体测试_活泼版_变体1",
        "主题变体测试_温馨版_变体1",
    ]

    export_folder = "./exports/variants"

    print(f"\n准备导出 {len(variant_drafts)} 个变体草稿")
    print(f"导出路径：{export_folder}")
    print(f"分辨率：1080p")
    print(f"帧率：30fps")
    print("\n草稿列表：")
    for i, name in enumerate(variant_drafts, 1):
        print(f"  {i}. {name}")

    print("\n开始导出...")
    print("-" * 60)

    try:
        exported_paths = await export_service.batch_export(
            draft_names=variant_drafts,
            export_folder=export_folder,
            resolution="1080p",
            framerate=30
        )

        print("\n" + "=" * 60)
        print("✓ 批量导出完成！")
        print("=" * 60)

        print(f"\n共导出 {len(exported_paths)} 个视频：")

        total_size = 0
        for i, path in enumerate(exported_paths, 1):
            if os.path.exists(path):
                file_size = os.path.getsize(path) / (1024 * 1024)
                total_size += file_size
                print(f"  {i}. {os.path.basename(path)}")
                print(f"     大小：{file_size:.2f} MB")
            else:
                print(f"  {i}. {os.path.basename(path)}")
                print(f"     ⚠️  文件不存在")

        print(f"\n总大小：{total_size:.2f} MB")
        print(f"\n📁 导出位置：{os.path.abspath(export_folder)}")

        print("\n🎬 变体对比：")
        print("  - 随机变体：不同的开头、结尾、字幕风格")
        print("  - 商务版：专业稳重的风格")
        print("  - 活泼版：年轻活力的风格")
        print("  - 温馨版：温馨感人的风格")

    except Exception as e:
        print(f"\n✗ 批量导出失败：{e}")
        print("\n可能的原因：")
        print("  1. 剪映未打开或不在草稿页面")
        print("  2. 某些草稿不存在")
        print("  3. 导出过程中剪映被操作")
        import traceback
        traceback.print_exc()


async def export_selected_variants():
    """导出选定的变体"""
    print("=" * 60)
    print("选择性导出变体")
    print("=" * 60)

    print("\n可用的变体类型：")
    print("  1. 随机变体（3个）")
    print("  2. 主题变体（3个）")
    print("  3. 全部变体（6个）")

    choice = input("\n请选择要导出的类型 (1/2/3): ")

    if choice == "1":
        drafts = [
            "随机变体测试_变体1",
            "随机变体测试_变体2",
            "随机变体测试_变体3",
        ]
        folder_name = "random_variants"
    elif choice == "2":
        drafts = [
            "主题变体测试_商务版_变体1",
            "主题变体测试_活泼版_变体1",
            "主题变体测试_温馨版_变体1",
        ]
        folder_name = "themed_variants"
    elif choice == "3":
        drafts = [
            "随机变体测试_变体1",
            "随机变体测试_变体2",
            "随机变体测试_变体3",
            "主题变体测试_商务版_变体1",
            "主题变体测试_活泼版_变体1",
            "主题变体测试_温馨版_变体1",
        ]
        folder_name = "all_variants"
    else:
        print("无效的选择")
        return

    export_folder = f"./exports/{folder_name}"

    print(f"\n准备导出 {len(drafts)} 个草稿到 {export_folder}")

    print("\n⚠️  请确保剪映已打开并在草稿页面")
    input("按 Enter 键开始...")

    try:
        exported_paths = await export_service.batch_export(
            draft_names=drafts,
            export_folder=export_folder,
            resolution="1080p",
            framerate=30
        )

        print(f"\n✓ 导出完成！共 {len(exported_paths)} 个视频")
        print(f"📁 位置：{os.path.abspath(export_folder)}")

    except Exception as e:
        print(f"\n✗ 导出失败：{e}")


async def main():
    """主函数"""
    print("=" * 60)
    print("变体视频导出工具")
    print("=" * 60)

    print("\n选择导出模式：")
    print("  1. 导出所有变体")
    print("  2. 选择性导出")

    mode = input("\n请选择模式 (1/2): ")

    try:
        if mode == "1":
            await export_all_variants()
        elif mode == "2":
            await export_selected_variants()
        else:
            print("无效的选择")
    except KeyboardInterrupt:
        print("\n\n导出已取消")
    except Exception as e:
        print(f"\n\n导出失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

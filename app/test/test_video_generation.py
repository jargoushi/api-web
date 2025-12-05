"""
视频生成服务测试

测试所有视频生成相关功能
"""
import os
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.video_generation import (
    draft_service,
    template_manager,
    material_manager,
    export_service
)
from app.core.logging import log


class VideoGenerationTester:
    """视频生成测试类"""

    def __init__(self):
        self.test_results = []
        self.test_materials_path = Path("test_materials")
        self.test_materials_path.mkdir(exist_ok=True)

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✓ 成功" if success else "✗ 失败"
        self.test_results.append({
            "name": test_name,
            "success": success,
            "message": message
        })
        print(f"\n{test_name}: {status}")
        if message:
            print(f"  {message}")

    async def test_material_manager(self):
        """测试素材管理服务"""
        print("\n" + "=" * 80)
        print("测试1: 素材管理服务")
        print("=" * 80)

        try:
            # 测试1.1: 列出素材
            print("\n测试1.1: 列出视频素材")
            videos = await material_manager.list_materials("video")
            self.log_test(
                "列出视频素材",
                True,
                f"找到 {len(videos)} 个视频素材"
            )

            # 测试1.2: 列出音频素材
            print("\n测试1.2: 列出音频素材")
            audios = await material_manager.list_materials("audio")
            self.log_test(
                "列出音频素材",
                True,
                f"找到 {len(audios)} 个音频素材"
            )

            # 测试1.3: 保存测试素材
            print("\n测试1.3: 保存测试素材")
            test_content = b"test content"
            saved_path = await material_manager.save_material(
                "video",
                "test_video.txt",
                test_content
            )
            self.log_test(
                "保存测试素材",
                os.path.exists(saved_path),
                f"保存路径: {saved_path}"
            )

            # 测试1.4: 获取素材路径
            print("\n测试1.4: 获取素材路径")
            try:
                path = await material_manager.get_material_path("video", "test_video.txt")
                self.log_test(
                    "获取素材路径",
                    True,
                    f"路径: {path}"
                )
            except Exception as e:
                self.log_test("获取素材路径", False, str(e))

            # 测试1.5: 删除测试素材
            print("\n测试1.5: 删除测试素材")
            deleted = await material_manager.delete_material("video", "test_video.txt")
            self.log_test(
                "删除测试素材",
                deleted,
                "素材已删除"
            )

            # 测试1.6: 获取临时路径
            print("\n测试1.6: 获取临时路径")
            temp_path = await material_manager.get_temp_path("temp_file.txt")
            self.log_test(
                "获取临时路径",
                True,
                f"临时路径: {temp_path}"
            )

            # 测试1.7: 清理临时文件
            print("\n测试1.7: 清理临时文件")
            count = await material_manager.cleanup_temp()
            self.log_test(
                "清理临时文件",
                True,
                f"清理了 {count} 个文件"
            )

        except Exception as e:
            self.log_test("素材管理服务", False, str(e))

    async def test_draft_service_basic(self):
        """测试草稿服务基础功能"""
        print("\n" + "=" * 80)
        print("测试2: 草稿服务基础功能")
        print("=" * 80)

        try:
            # 测试2.1: 创建草稿
            print("\n测试2.1: 创建新草稿")
            try:
                script = await draft_service.create_draft(
                    "测试草稿_基础",
                    1920,
                    1080
                )
                self.log_test(
                    "创建新草稿",
                    script is not None,
                    "草稿对象创建成功"
                )

                # 测试2.2: 添加轨道
                print("\n测试2.2: 添加视频轨道")
                await draft_service.add_track(
                    script,
                    "video",
                    "主视频轨道",
                    relative_index=1
                )
                self.log_test("添加视频轨道", True, "视频轨道添加成功")

                # 测试2.3: 添加音频轨道
                print("\n测试2.3: 添加音频轨道")
                await draft_service.add_track(
                    script,
                    "audio",
                    "背景音乐",
                    relative_index=1
                )
                self.log_test("添加音频轨道", True, "音频轨道添加成功")

                # 测试2.4: 添加文本轨道
                print("\n测试2.4: 添加文本轨道")
                await draft_service.add_track(
                    script,
                    "text",
                    "字幕轨道",
                    relative_index=1
                )
                self.log_test("添加文本轨道", True, "文本轨道添加成功")

                # 测试2.5: 保存草稿
                print("\n测试2.5: 保存草稿")
                await draft_service.save_draft(script)
                self.log_test("保存草稿", True, "草稿保存成功")

            except Exception as e:
                self.log_test("草稿服务基础功能", False, str(e))

        except Exception as e:
            self.log_test("草稿服务基础功能", False, str(e))

    async def test_draft_service_with_materials(self):
        """测试草稿服务添加素材功能"""
        print("\n" + "=" * 80)
        print("测试3: 草稿服务添加素材功能")
        print("=" * 80)

        print("\n⚠️  注意：此测试需要实际的视频/音频素材文件")
        print("请确保在 materials 目录下有测试素材，或跳过此测试")

        try:
            # 检查是否有测试素材
            videos = await material_manager.list_materials("video", pattern=".mp4")
            audios = await material_manager.list_materials("audio", pattern=".mp3")

            if not videos:
                self.log_test(
                    "添加素材功能",
                    False,
                    "未找到测试视频素材（.mp4），跳过测试"
                )
                return

            # 测试3.1: 创建草稿
            print("\n测试3.1: 创建带素材的草稿")
            script = await draft_service.create_draft(
                "测试草稿_素材",
                1920,
                1080
            )

            # 测试3.2: 添加视频片段
            print("\n测试3.2: 添加视频片段")
            video_path = videos[0]['path']
            await draft_service.add_video_segment(
                script,
                video_path,
                start_time="0s",
                duration="5s",
                speed=1.0
            )
            self.log_test(
                "添加视频片段",
                True,
                f"视频: {videos[0]['filename']}"
            )

            # 测试3.3: 添加音频片段
            if audios:
                print("\n测试3.3: 添加音频片段")
                audio_path = audios[0]['path']
                await draft_service.add_audio_segment(
                    script,
                    audio_path,
                    start_time="0s",
                    duration="5s",
                    volume=0.8
                )
                self.log_test(
                    "添加音频片段",
                    True,
                    f"音频: {audios[0]['filename']}"
                )

            # 测试3.4: 添加文本片段
            print("\n测试3.4: 添加文本片段")
            await draft_service.add_text_segment(
                script,
                "这是测试文本",
                start_time="0s",
                duration="5s",
                style={
                    "size": 5.0,
                    "color": (1.0, 1.0, 1.0)
                }
            )
            self.log_test("添加文本片段", True, "文本片段添加成功")

            # 测试3.5: 保存草稿
            print("\n测试3.5: 保存带素材的草稿")
            await draft_service.save_draft(script)
            self.log_test("保存带素材的草稿", True, "草稿保存成功")

        except Exception as e:
            self.log_test("添加素材功能", False, str(e))

    async def test_draft_service_subtitle(self):
        """测试字幕导入功能"""
        print("\n" + "=" * 80)
        print("测试4: 字幕导入功能")
        print("=" * 80)

        print("\n⚠️  注意：此测试需要 SRT 字幕文件")

        try:
            # 检查是否有字幕文件
            subtitles = await material_manager.list_materials("subtitle", pattern=".srt")

            if not subtitles:
                # 创建测试字幕文件
                print("\n创建测试字幕文件")
                test_srt_content = """1
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
                    "test_subtitle.srt",
                    test_srt_content.encode('utf-8')
                )
                self.log_test("创建测试字幕", True, "测试字幕文件已创建")

            # 测试4.1: 创建草稿
            print("\n测试4.1: 创建带字幕的草稿")
            script = await draft_service.create_draft(
                "测试草稿_字幕",
                1920,
                1080
            )

            # 测试4.2: 导入字幕
            print("\n测试4.2: 导入SRT字幕")
            srt_path = await material_manager.get_material_path("subtitle", "test_subtitle.srt")
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
            self.log_test("导入SRT字幕", True, "字幕导入成功")

            # 测试4.3: 保存草稿
            print("\n测试4.3: 保存带字幕的草稿")
            await draft_service.save_draft(script)
            self.log_test("保存带字幕的草稿", True, "草稿保存成功")

        except Exception as e:
            self.log_test("字幕导入功能", False, str(e))

    async def test_template_manager(self):
        """测试模板管理功能"""
        print("\n" + "=" * 80)
        print("测试5: 模板管理功能")
        print("=" * 80)

        print("\n⚠️  注意：此测试需要已有的剪映草稿作为模板")
        print("请确保剪映草稿文件夹中有可用的草稿，或跳过此测试")

        try:
            # 测试5.1: 加载模板
            print("\n测试5.1: 加载模板（需要已有草稿）")
            try:
                # 这里需要替换为实际存在的草稿名称
                template_name = "测试草稿_基础"  # 使用前面创建的草稿
                script = await template_manager.load_template(template_name)
                self.log_test(
                    "加载模板",
                    script is not None,
                    f"模板 {template_name} 加载成功"
                )
            except Exception as e:
                self.log_test("加载模板", False, f"未找到模板或加载失败: {str(e)}")

            # 测试5.2: 复制模板
            print("\n测试5.2: 复制模板创建新草稿")
            try:
                new_script = await template_manager.duplicate_template(
                    "测试草稿_基础",
                    "测试草稿_复制"
                )
                self.log_test(
                    "复制模板",
                    new_script is not None,
                    "模板复制成功"
                )
            except Exception as e:
                self.log_test("复制模板", False, str(e))

            # 测试5.3: 提取素材元数据
            print("\n测试5.3: 提取素材元数据")
            try:
                metadata = await template_manager.inspect_material("测试草稿_基础")
                self.log_test(
                    "提取素材元数据",
                    True,
                    "元数据提取成功"
                )
            except Exception as e:
                self.log_test("提取素材元数据", False, str(e))

        except Exception as e:
            self.log_test("模板管理功能", False, str(e))

    async def test_export_service(self):
        """测试视频导出功能"""
        print("\n" + "=" * 80)
        print("测试6: 视频导出功能")
        print("=" * 80)

        print("\n⚠️  警告：此测试需要剪映已打开并位于目录页")
        print("⚠️  导出过程会控制鼠标，建议在测试环境运行")
        print("⚠️  如果不想测试导出功能，请跳过此测试")

        user_input = input("\n是否执行导出测试？(y/n): ")
        if user_input.lower() != 'y':
            self.log_test("视频导出功能", False, "用户跳过测试")
            return

        try:
            # 测试6.1: 单个草稿导出
            print("\n测试6.1: 导出单个草稿")
            try:
                export_path = await export_service.export_draft(
                    draft_name="测试草稿_基础",
                    export_path="./output/test_export.mp4",
                    resolution="1080p",
                    framerate=30
                )
                self.log_test(
                    "导出单个草稿",
                    os.path.exists(export_path),
                    f"导出路径: {export_path}"
                )
            except Exception as e:
                self.log_test("导出单个草稿", False, str(e))

            # 测试6.2: 批量导出
            print("\n测试6.2: 批量导出草稿")
            try:
                export_paths = await export_service.batch_export(
                    draft_names=["测试草稿_基础", "测试草稿_素材"],
                    export_folder="./output",
                    resolution="720p",
                    framerate=30
                )
                self.log_test(
                    "批量导出草稿",
                    len(export_paths) > 0,
                    f"导出了 {len(export_paths)} 个视频"
                )
            except Exception as e:
                self.log_test("批量导出草稿", False, str(e))

        except Exception as e:
            self.log_test("视频导出功能", False, str(e))

    async def test_advanced_features(self):
        """测试高级功能"""
        print("\n" + "=" * 80)
        print("测试7: 高级功能")
        print("=" * 80)

        try:
            # 测试7.1: 创建复杂草稿
            print("\n测试7.1: 创建包含多轨道的复杂草稿")
            script = await draft_service.create_draft(
                "测试草稿_复杂",
                1920,
                1080
            )

            # 添加多个视频轨道
            await draft_service.add_track(script, "video", "前景", relative_index=2)
            await draft_service.add_track(script, "video", "背景", relative_index=1)

            # 添加多个音频轨道
            await draft_service.add_track(script, "audio", "背景音乐", relative_index=1)
            await draft_service.add_track(script, "audio", "音效", relative_index=2)

            # 添加文本轨道
            await draft_service.add_track(script, "text", "标题", relative_index=2)
            await draft_service.add_track(script, "text", "字幕", relative_index=1)

            self.log_test("创建多轨道草稿", True, "多轨道草稿创建成功")

            # 测试7.2: 添加多个文本片段
            print("\n测试7.2: 添加多个文本片段")
            for i in range(3):
                await draft_service.add_text_segment(
                    script,
                    f"文本片段 {i+1}",
                    start_time=f"{i*3}s",
                    duration="3s",
                    track_name="字幕"
                )
            self.log_test("添加多个文本片段", True, "添加了3个文本片段")

            # 测试7.3: 保存复杂草稿
            print("\n测试7.3: 保存复杂草稿")
            await draft_service.save_draft(script)
            self.log_test("保存复杂草稿", True, "复杂草稿保存成功")

        except Exception as e:
            self.log_test("高级功能", False, str(e))

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("测试结果汇总")
        print("=" * 80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed

        print(f"\n总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {passed/total*100:.1f}%")

        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['message']}")

        print("\n" + "=" * 80)
        print("视频生成服务测试完成")
        print("=" * 80)


async def main():
    """主测试函数"""
    print("=" * 80)
    print("视频生成服务完整测试")
    print("=" * 80)
    print("\n本测试将覆盖所有视频生成功能")
    print("包括：素材管理、草稿生成、模板管理、视频导出等")
    print("\n注意事项：")
    print("1. 请确保已在 .env 文件中配置 JIANYING_DRAFT_FOLDER")
    print("2. 部分测试需要实际的素材文件（视频/音频/字幕）")
    print("3. 导出测试需要剪映已打开并位于目录页")
    print("4. 建议在测试环境运行，避免影响正式数据")

    input("\n按 Enter 键开始测试...")

    tester = VideoGenerationTester()

    # 执行所有测试
    await tester.test_material_manager()
    await tester.test_draft_service_basic()
    await tester.test_draft_service_with_materials()
    await tester.test_draft_service_subtitle()
    await tester.test_template_manager()
    await tester.test_export_service()
    await tester.test_advanced_features()

    # 打印测试总结
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())

# 用户配置模块测试文件
import asyncio
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.config import init_db, close_db
from app.models.account.setting import Setting
from app.enums.settings import (
    SettingGroupEnum,
    GeneralSettingEnum,
    NotificationSettingEnum,
    AdvancedSettingEnum
)
from app.schemas.account.setting import SettingUpdateRequest
from app.services.account.setting_service import SettingService


class SettingTester:
    """用户配置模块测试类"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_user_id = 1
        self.service = SettingService()

    @staticmethod
    async def setup_test_database():
        print("正在初始化测试数据库...")
        await init_db()
        print("测试数据库初始化完成")

    @staticmethod
    async def cleanup_test_database():
        print("正在清理测试数据库...")
        await Setting.all().delete()
        await close_db()
        print("测试数据库清理完成")

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({"test_name": test_name, "success": success})

    async def test_get_all_settings_default(self):
        """测试1: 获取所有配置（默认值）"""
        print("\n测试1: 获取所有配置（默认值）")
        try:
            result = await self.service.get_all_settings(self.test_user_id)
            assert len(result.groups) == 4, f"应该有4个分组"
            for group in result.groups:
                for setting in group.settings:
                    assert setting.is_default is True
            self.log_test_result("获取所有配置（默认值）", True, f"成功获取{len(result.groups)}个分组")
        except Exception as e:
            self.log_test_result("获取所有配置（默认值）", False, str(e))

    async def test_get_single_setting(self):
        """测试2: 获取单个配置"""
        print("\n测试2: 获取单个配置")
        try:
            result = await self.service.get_setting(self.test_user_id, GeneralSettingEnum.AUTO_DOWNLOAD.code)
            assert result.setting_key == GeneralSettingEnum.AUTO_DOWNLOAD.code
            assert result.is_default is True
            self.log_test_result("获取单个配置", True, f"{result.setting_key_name}={result.setting_value}")
        except Exception as e:
            self.log_test_result("获取单个配置", False, str(e))

    async def test_get_invalid_setting(self):
        """测试3: 获取不存在的配置项"""
        print("\n测试3: 获取不存在的配置项")
        try:
            await self.service.get_setting(self.test_user_id, 99999)
            self.log_test_result("获取不存在的配置项", False, "应该抛出异常")
        except Exception as e:
            if "不支持的配置项编码" in str(e):
                self.log_test_result("获取不存在的配置项", True, "正确抛出异常")
            else:
                self.log_test_result("获取不存在的配置项", False, str(e))

    async def test_update_setting(self):
        """测试4: 更新配置"""
        print("\n测试4: 更新配置")
        try:
            request = SettingUpdateRequest(setting_key=AdvancedSettingEnum.MAX_CONCURRENT_TASKS.code, setting_value=5)
            result = await self.service.update_setting(self.test_user_id, request)
            assert result.setting_value == 5
            assert result.is_default is False
            self.log_test_result("更新配置", True, f"最大并发数=5")
        except Exception as e:
            self.log_test_result("更新配置", False, str(e))

    async def test_update_setting_type_validation(self):
        """测试5: 更新配置（类型验证）"""
        print("\n测试5: 更新配置（类型验证）")
        try:
            request = SettingUpdateRequest(setting_key=AdvancedSettingEnum.MAX_CONCURRENT_TASKS.code, setting_value="not_a_number")
            await self.service.update_setting(self.test_user_id, request)
            self.log_test_result("更新配置（类型验证）", False, "应该抛出类型错误")
        except Exception as e:
            if "配置值类型错误" in str(e):
                self.log_test_result("更新配置（类型验证）", True, "正确验证类型")
            else:
                self.log_test_result("更新配置（类型验证）", False, str(e))

    async def test_reset_setting(self):
        """测试6: 重置配置"""
        print("\n测试6: 重置配置")
        try:
            # 先更新
            request = SettingUpdateRequest(setting_key=AdvancedSettingEnum.MAX_CONCURRENT_TASKS.code, setting_value=10)
            await self.service.update_setting(self.test_user_id, request)
            # 重置
            result = await self.service.reset_setting(self.test_user_id, AdvancedSettingEnum.MAX_CONCURRENT_TASKS.code)
            assert result.is_default is True
            assert result.setting_value == AdvancedSettingEnum.MAX_CONCURRENT_TASKS.default
            self.log_test_result("重置配置", True, f"重置为默认值 {result.setting_value}")
        except Exception as e:
            self.log_test_result("重置配置", False, str(e))

    async def test_get_settings_by_group(self):
        """测试7: 按分组获取配置"""
        print("\n测试7: 按分组获取配置")
        try:
            result = await self.service.get_settings_by_group(self.test_user_id, SettingGroupEnum.GENERAL.code)
            assert result.group_code == SettingGroupEnum.GENERAL.code
            assert len(result.settings) == 2
            self.log_test_result("按分组获取配置", True, f"{result.group} 有 {len(result.settings)} 个配置")
        except Exception as e:
            self.log_test_result("按分组获取配置", False, str(e))

    async def test_get_invalid_group(self):
        """测试8: 获取不存在的分组"""
        print("\n测试8: 获取不存在的分组")
        try:
            await self.service.get_settings_by_group(self.test_user_id, 99999)
            self.log_test_result("获取不存在的分组", False, "应该抛出异常")
        except Exception as e:
            if "不支持的分组编码" in str(e):
                self.log_test_result("获取不存在的分组", True, "正确抛出异常")
            else:
                self.log_test_result("获取不存在的分组", False, str(e))

    async def test_group_enum_structure(self):
        """测试9: 分组枚举结构"""
        print("\n测试9: 分组枚举结构")
        try:
            # 验证分组
            assert len(list(SettingGroupEnum)) == 4
            # 验证每个分组都有配置项
            for group in SettingGroupEnum:
                assert len(group.get_settings()) > 0
            # 验证 get_all_settings
            all_settings = SettingGroupEnum.get_all_settings()
            assert len(all_settings) == 9
            self.log_test_result("分组枚举结构", True, f"4个分组，9个配置项")
        except Exception as e:
            self.log_test_result("分组枚举结构", False, str(e))

    async def test_find_setting_by_code(self):
        """测试10: 根据code查找配置"""
        print("\n测试10: 根据code查找配置")
        try:
            group, setting = SettingGroupEnum.find_setting_by_code(GeneralSettingEnum.AUTO_DOWNLOAD.code)
            assert group == SettingGroupEnum.GENERAL
            assert setting == GeneralSettingEnum.AUTO_DOWNLOAD
            self.log_test_result("根据code查找配置", True, f"找到 {group.desc}/{setting.desc}")
        except Exception as e:
            self.log_test_result("根据code查找配置", False, str(e))

    async def run_all_tests(self):
        print("=" * 80)
        print("开始用户配置模块测试")
        print("=" * 80)

        try:
            await self.setup_test_database()

            await self.test_get_all_settings_default()
            await self.test_get_single_setting()
            await self.test_get_invalid_setting()
            await self.test_update_setting()
            await self.test_update_setting_type_validation()
            await self.test_reset_setting()
            await self.test_get_settings_by_group()
            await self.test_get_invalid_group()
            await self.test_group_enum_structure()
            await self.test_find_setting_by_code()

            total = len(self.test_results)
            passed = sum(1 for r in self.test_results if r["success"])
            print("\n" + "=" * 80)
            print(f"测试结果: {passed}/{total} 通过，成功率 {passed/total*100:.0f}%")
            print("=" * 80)

        finally:
            await self.cleanup_test_database()


async def main():
    tester = SettingTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

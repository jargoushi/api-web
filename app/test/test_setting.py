# 用户配置模块测试文件
import asyncio
import os
import sys
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.config import init_db, close_db
from app.models.account.user_setting import UserSetting
from app.enums.common.setting_key import SettingKeyEnum
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
        """初始化测试数据库"""
        print("正在初始化测试数据库...")
        await init_db()
        print("测试数据库初始化完成")

    @staticmethod
    async def cleanup_test_database():
        """清理测试数据库"""
        print("正在清理测试数据库...")
        await UserSetting.all().delete()
        await close_db()
        print("测试数据库清理完成")

    def log_test_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data
        }
        self.test_results.append(result)

        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")

    async def test_get_all_settings_default(self):
        """测试1: 获取所有配置（默认值）"""
        print("\n测试1: 获取所有配置（默认值）")

        try:
            result = await self.service.get_all_settings(self.test_user_id)

            # 验证返回了分组
            assert len(result.groups) > 0, "应该至少有一个分组"

            # 验证所有配置项都是默认值
            for group in result.groups:
                for setting in group.settings:
                    assert setting.is_default is True, f"配置{setting.setting_key}应该是默认值"

            self.log_test_result(
                "获取所有配置（默认值）",
                True,
                f"成功获取{len(result.groups)}个分组的配置",
                {"groups": [g.group for g in result.groups]}
            )

        except Exception as e:
            self.log_test_result("获取所有配置（默认值）", False, str(e))

    async def test_get_single_setting(self):
        """测试2: 获取单个配置"""
        print("\n测试2: 获取单个配置")

        try:
            setting_key = SettingKeyEnum.AUTO_DOWNLOAD.code
            result = await self.service.get_setting(self.test_user_id, setting_key)

            assert result.setting_key == setting_key, "配置项编码不匹配"
            assert result.setting_key_name == SettingKeyEnum.AUTO_DOWNLOAD.desc, "配置项名称不匹配"
            assert result.is_default is True, "应该是默认值"
            assert result.setting_value == SettingKeyEnum.AUTO_DOWNLOAD.default, "默认值不匹配"

            self.log_test_result(
                "获取单个配置",
                True,
                f"成功获取配置 {result.setting_key_name}={result.setting_value}",
                {"setting_key": setting_key, "value": result.setting_value}
            )

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
                self.log_test_result("获取不存在的配置项", False, f"异常类型不对: {e}")

    async def test_update_setting(self):
        """测试4: 更新配置"""
        print("\n测试4: 更新配置")

        try:
            setting_key = SettingKeyEnum.MAX_CONCURRENT_TASKS.code
            new_value = 5

            request = SettingUpdateRequest(
                setting_key=setting_key,
                setting_value=new_value
            )
            result = await self.service.update_setting(self.test_user_id, request)

            assert result.setting_key == setting_key, "配置项编码不匹配"
            assert result.setting_value == new_value, "配置值未更新"
            assert result.is_default is False, "不应该是默认值"

            # 验证数据库中的更新
            db_setting = await UserSetting.get_or_none(
                user_id=self.test_user_id,
                setting_key=setting_key
            )
            assert db_setting is not None, "数据库中应该有记录"
            assert db_setting.setting_value == new_value, "数据库值不匹配"

            self.log_test_result(
                "更新配置",
                True,
                f"成功更新配置 最大并发数={new_value}",
                {"setting_key": setting_key, "new_value": new_value}
            )

        except Exception as e:
            self.log_test_result("更新配置", False, str(e))

    async def test_update_setting_type_validation(self):
        """测试5: 更新配置（类型验证）"""
        print("\n测试5: 更新配置（类型验证）")

        try:
            # 尝试用字符串更新整数类型的配置
            request = SettingUpdateRequest(
                setting_key=SettingKeyEnum.MAX_CONCURRENT_TASKS.code,
                setting_value="not_a_number"
            )
            await self.service.update_setting(self.test_user_id, request)
            self.log_test_result("更新配置（类型验证）", False, "应该抛出类型错误")
        except Exception as e:
            if "配置值类型错误" in str(e):
                self.log_test_result("更新配置（类型验证）", True, "正确验证类型")
            else:
                self.log_test_result("更新配置（类型验证）", False, f"异常类型不对: {e}")

    async def test_reset_setting(self):
        """测试6: 重置配置"""
        print("\n测试6: 重置配置")

        try:
            setting_key = SettingKeyEnum.MAX_CONCURRENT_TASKS.code

            # 先更新配置
            request = SettingUpdateRequest(
                setting_key=setting_key,
                setting_value=10
            )
            await self.service.update_setting(self.test_user_id, request)

            # 重置配置
            result = await self.service.reset_setting(self.test_user_id, setting_key)

            assert result.is_default is True, "应该是默认值"
            assert result.setting_value == SettingKeyEnum.MAX_CONCURRENT_TASKS.default, "值应该恢复为默认"

            # 验证数据库中已删除
            db_setting = await UserSetting.get_or_none(
                user_id=self.test_user_id,
                setting_key=setting_key
            )
            assert db_setting is None, "数据库中应该没有记录"

            self.log_test_result(
                "重置配置",
                True,
                f"成功重置配置为默认值 {result.setting_value}",
                {"setting_key": setting_key, "default_value": result.setting_value}
            )

        except Exception as e:
            self.log_test_result("重置配置", False, str(e))

    async def test_get_settings_by_group(self):
        """测试7: 按分组获取配置"""
        print("\n测试7: 按分组获取配置")

        try:
            group = "general"
            result = await self.service.get_settings_by_group(self.test_user_id, group)

            assert result.group == group, "分组名称不匹配"
            assert len(result.settings) > 0, "应该有配置项"

            # 验证所有配置项都属于该分组
            for setting in result.settings:
                assert setting.group == group, f"配置{setting.setting_key}不属于{group}分组"

            self.log_test_result(
                "按分组获取配置",
                True,
                f"成功获取 {group} 分组的 {len(result.settings)} 个配置",
                {"group": group, "count": len(result.settings)}
            )

        except Exception as e:
            self.log_test_result("按分组获取配置", False, str(e))

    async def test_get_invalid_group(self):
        """测试8: 获取不存在的分组"""
        print("\n测试8: 获取不存在的分组")

        try:
            await self.service.get_settings_by_group(self.test_user_id, "invalid_group")
            self.log_test_result("获取不存在的分组", False, "应该抛出异常")
        except Exception as e:
            if "不支持的配置分组" in str(e):
                self.log_test_result("获取不存在的分组", True, "正确抛出异常")
            else:
                self.log_test_result("获取不存在的分组", False, f"异常类型不对: {e}")

    async def test_multiple_settings_update(self):
        """测试9: 批量更新配置"""
        print("\n测试9: 批量更新配置")

        try:
            updates = [
                (SettingKeyEnum.AUTO_DOWNLOAD.code, False),
                (SettingKeyEnum.NOTIFY_ON_SUCCESS.code, False),
                (SettingKeyEnum.TASK_RETRY_COUNT.code, 5),
            ]

            for setting_key, value in updates:
                request = SettingUpdateRequest(setting_key=setting_key, setting_value=value)
                await self.service.update_setting(self.test_user_id, request)

            # 获取所有配置验证
            all_settings = await self.service.get_all_settings(self.test_user_id)

            updated_count = 0
            for group in all_settings.groups:
                for setting in group.settings:
                    if not setting.is_default:
                        updated_count += 1

            assert updated_count == len(updates), f"应该有{len(updates)}个非默认配置"

            self.log_test_result(
                "批量更新配置",
                True,
                f"成功更新{updated_count}个配置",
                {"updated_count": updated_count}
            )

        except Exception as e:
            self.log_test_result("批量更新配置", False, str(e))

    async def test_enum_completeness(self):
        """测试10: 枚举完整性检查"""
        print("\n测试10: 枚举完整性检查")

        try:
            # 检查所有枚举成员都有必要的属性
            for setting_enum in SettingKeyEnum:
                assert hasattr(setting_enum, 'code'), f"{setting_enum.name} 缺少 code"
                assert hasattr(setting_enum, 'desc'), f"{setting_enum.name} 缺少 desc"
                assert hasattr(setting_enum, 'group'), f"{setting_enum.name} 缺少 group"
                assert hasattr(setting_enum, 'default'), f"{setting_enum.name} 缺少 default"
                assert hasattr(setting_enum, 'value_type'), f"{setting_enum.name} 缺少 value_type"

            # 检查所有分组
            groups = SettingKeyEnum.get_all_groups()
            assert len(groups) > 0, "应该至少有一个分组"
            assert "general" in groups, "应该有 general 分组"
            assert "notification" in groups, "应该有 notification 分组"
            assert "advanced" in groups, "应该有 advanced 分组"

            self.log_test_result(
                "枚举完整性检查",
                True,
                f"枚举共有{len(list(SettingKeyEnum))}个配置项，{len(groups)}个分组",
                {"total_settings": len(list(SettingKeyEnum)), "groups": groups}
            )

        except Exception as e:
            self.log_test_result("枚举完整性检查", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("开始用户配置模块测试")
        print("=" * 80)

        try:
            # 初始化测试环境
            await self.setup_test_database()

            # 运行所有测试
            await self.test_get_all_settings_default()
            await self.test_get_single_setting()
            await self.test_get_invalid_setting()
            await self.test_update_setting()
            await self.test_update_setting_type_validation()
            await self.test_reset_setting()
            await self.test_get_settings_by_group()
            await self.test_get_invalid_group()
            await self.test_multiple_settings_update()
            await self.test_enum_completeness()

            # 统计测试结果
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results if result["success"])
            failed_tests = total_tests - passed_tests

            print("\n" + "=" * 80)
            print("测试结果汇总")
            print("=" * 80)
            print(f"总测试数: {total_tests}")
            print(f"通过: {passed_tests}")
            print(f"失败: {failed_tests}")
            print(f"成功率: {passed_tests / total_tests * 100:.1f}%")

            if failed_tests > 0:
                print("\n失败的测试:")
                for result in self.test_results:
                    if not result["success"]:
                        print(f"  ✗ {result['test_name']}: {result['message']}")

        except Exception as e:
            print(f"测试执行过程中出现错误: {e}")

        finally:
            # 清理测试环境
            await self.cleanup_test_database()

        print("\n" + "=" * 80)
        print("用户配置模块测试完成")
        print("=" * 80)


# 测试入口函数
async def main():
    """主测试入口"""
    tester = SettingTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

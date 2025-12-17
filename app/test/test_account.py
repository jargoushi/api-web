# 账号模块测试文件
import asyncio
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.config import init_db, close_db
from app.models.account.account import Account, AccountProjectChannel
from app.models.account.setting import Setting
from app.enums.common.channel import ChannelEnum
from app.enums.common.project import ProjectEnum
from app.enums.settings import SettingGroupEnum, GeneralSettingEnum
from app.schemas.account.account import (
    AccountCreateRequest, AccountUpdateRequest,
    BindingRequest
)
from app.schemas.account.setting import SettingUpdateRequest
from app.services.account.account_service import AccountService
from app.services.account.setting_service import SettingService


class AccountTester:
    """账号模块测试类"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_user_id = 1
        self.account_service = AccountService()
        self.setting_service = SettingService()
        self.created_account_id = None

    @staticmethod
    async def setup_test_database():
        print("正在初始化测试数据库...")
        await init_db()
        print("测试数据库初始化完成")

    @staticmethod
    async def cleanup_test_database():
        print("正在清理测试数据库...")
        await Setting.all().delete()
        await AccountProjectChannel.all().delete()
        await Account.all().delete()
        await close_db()
        print("测试数据库清理完成")

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({"test_name": test_name, "success": success})

    # ========== 枚举测试 ==========

    async def test_channel_enum(self):
        """测试1: 渠道枚举"""
        print("\n测试1: 渠道枚举")
        try:
            assert len(list(ChannelEnum)) == 4, "应该有4个渠道"
            assert ChannelEnum.BILIBILI.code == 3
            assert ChannelEnum.WECHAT_VIDEO.code == 4
            self.log_test_result("渠道枚举", True, f"共{len(list(ChannelEnum))}个渠道")
        except Exception as e:
            self.log_test_result("渠道枚举", False, str(e))

    async def test_project_enum(self):
        """测试2: 项目枚举"""
        print("\n测试2: 项目枚举")
        try:
            project = ProjectEnum.AI_LANDSCAPE
            assert project.code == 1
            assert project.desc == "AI风景号"
            assert len(project.channels) == 3
            assert ChannelEnum.BILIBILI in project.channels
            self.log_test_result("项目枚举", True, f"AI风景号支持{len(project.channels)}个渠道")
        except Exception as e:
            self.log_test_result("项目枚举", False, str(e))

    async def test_project_to_dict(self):
        """测试3: 项目枚举序列化"""
        print("\n测试3: 项目枚举序列化")
        try:
            project = ProjectEnum.AI_LANDSCAPE
            data = project.to_dict()
            assert "code" in data
            assert "desc" in data
            assert "channels" in data
            assert len(data["channels"]) == 3
            self.log_test_result("项目枚举序列化", True, f"序列化成功")
        except Exception as e:
            self.log_test_result("项目枚举序列化", False, str(e))

    # ========== 账号管理测试 ==========

    async def test_create_account(self):
        """测试4: 创建账号"""
        print("\n测试4: 创建账号")
        try:
            request = AccountCreateRequest(
                name="测试账号",
                platform_account="test_user",
                platform_password="test_pass",
                description="测试描述"
            )
            result = await self.account_service.create_account(self.test_user_id, request)
            assert result.name == "测试账号"
            assert result.platform_account == "test_user"
            self.created_account_id = result.id
            self.log_test_result("创建账号", True, f"账号ID={result.id}")
        except Exception as e:
            self.log_test_result("创建账号", False, str(e))

    async def test_get_accounts(self):
        """测试5: 获取账号列表"""
        print("\n测试5: 获取账号列表")
        try:
            accounts = await self.account_service.get_accounts(self.test_user_id)
            assert len(accounts) >= 1
            self.log_test_result("获取账号列表", True, f"共{len(accounts)}个账号")
        except Exception as e:
            self.log_test_result("获取账号列表", False, str(e))

    async def test_update_account(self):
        """测试6: 更新账号"""
        print("\n测试6: 更新账号")
        try:
            request = AccountUpdateRequest(
                id=self.created_account_id,
                name="更新后账号名",
                description="更新后描述"
            )
            result = await self.account_service.update_account(self.test_user_id, request)
            assert result.name == "更新后账号名"
            self.log_test_result("更新账号", True, f"名称更新为: {result.name}")
        except Exception as e:
            self.log_test_result("更新账号", False, str(e))

    async def test_get_nonexistent_account(self):
        """测试7: 获取不存在的账号"""
        print("\n测试7: 获取不存在的账号")
        try:
            await self.account_service.get_bindings(self.test_user_id, 99999)
            self.log_test_result("获取不存在的账号", False, "应该抛出异常")
        except Exception as e:
            if "账号不存在" in str(e):
                self.log_test_result("获取不存在的账号", True, "正确抛出异常")
            else:
                self.log_test_result("获取不存在的账号", False, str(e))

    # ========== 绑定测试 ==========

    async def test_bindding(self):
        """测试8: 绑定项目渠道"""
        print("\n测试8: 绑定项目渠道")
        try:
            request = BindingRequest(
                project_code=ProjectEnum.AI_LANDSCAPE.code,
                channel_code=ChannelEnum.BILIBILI.code,
                browser_id="test_browser_001"
            )
            result = await self.account_service.bindding(
                self.test_user_id, self.created_account_id, request
            )
            assert result.project_code == ProjectEnum.AI_LANDSCAPE.code
            assert result.channel_code == ChannelEnum.BILIBILI.code
            assert result.browser_id == "test_browser_001"
            self.log_test_result("绑定项目渠道", True, f"{result.project_name}/{result.channel_name}")
        except Exception as e:
            self.log_test_result("绑定项目渠道", False, str(e))

    async def test_bindding_invalid_channel(self):
        """测试9: 绑定不支持的渠道"""
        print("\n测试9: 绑定不支持的渠道")
        try:
            request = BindingRequest(
                project_code=ProjectEnum.AI_LANDSCAPE.code,
                channel_code=ChannelEnum.YOUTUBE.code,  # AI风景号不支持YouTube
                browser_id="test_browser"
            )
            await self.account_service.bindding(
                self.test_user_id, self.created_account_id, request
            )
            self.log_test_result("绑定不支持的渠道", False, "应该抛出异常")
        except Exception as e:
            if "不支持渠道" in str(e):
                self.log_test_result("绑定不支持的渠道", True, "正确抛出异常")
            else:
                self.log_test_result("绑定不支持的渠道", False, str(e))

    async def test_get_bindings(self):
        """测试10: 获取绑定列表"""
        print("\n测试10: 获取绑定列表")
        try:
            bindings = await self.account_service.get_bindings(
                self.test_user_id, self.created_account_id
            )
            assert len(bindings) >= 1
            self.log_test_result("获取绑定列表", True, f"共{len(bindings)}个绑定")
        except Exception as e:
            self.log_test_result("获取绑定列表", False, str(e))

    # ========== 账号配置测试 ==========

    async def test_account_setting_inherit(self):
        """测试11: 账号配置继承用户配置"""
        print("\n测试11: 账号配置继承用户配置")
        try:
            # 先设置用户配置
            user_request = SettingUpdateRequest(
                setting_key=GeneralSettingEnum.AUTO_DOWNLOAD.code,
                setting_value=True
            )
            await self.setting_service.update_setting(self.test_user_id, user_request)

            # 获取账号配置（应继承用户配置）
            result = await self.setting_service.get_account_all_settings(
                self.created_account_id, self.test_user_id
            )
            # 找到对应配置项
            found = False
            for group in result.groups:
                for setting in group.settings:
                    if setting.setting_key == GeneralSettingEnum.AUTO_DOWNLOAD.code:
                        assert setting.setting_value == True
                        found = True
            assert found, "应该找到配置项"
            self.log_test_result("账号配置继承用户配置", True, "继承成功")
        except Exception as e:
            self.log_test_result("账号配置继承用户配置", False, str(e))

    async def test_account_setting_override(self):
        """测试12: 账号配置覆盖用户配置"""
        print("\n测试12: 账号配置覆盖用户配置")
        try:
            # 设置账号配置（覆盖用户配置）
            request = SettingUpdateRequest(
                setting_key=GeneralSettingEnum.AUTO_DOWNLOAD.code,
                setting_value=False
            )
            result = await self.setting_service.update_account_setting(
                self.created_account_id, request
            )
            assert result.setting_value == False
            assert result.is_default == False
            self.log_test_result("账号配置覆盖用户配置", True, f"覆盖为: {result.setting_value}")
        except Exception as e:
            self.log_test_result("账号配置覆盖用户配置", False, str(e))

    async def test_account_setting_reset(self):
        """测试13: 重置账号配置"""
        print("\n测试13: 重置账号配置")
        try:
            result = await self.setting_service.reset_account_setting(
                self.created_account_id,
                GeneralSettingEnum.AUTO_DOWNLOAD.code
            )
            assert result.is_default == True
            self.log_test_result("重置账号配置", True, "重置成功")
        except Exception as e:
            self.log_test_result("重置账号配置", False, str(e))

    async def test_effective_setting(self):
        """测试14: 获取有效配置"""
        print("\n测试14: 获取有效配置")
        try:
            value = await self.setting_service.get_effective_setting(
                self.created_account_id,
                self.test_user_id,
                GeneralSettingEnum.AUTO_DOWNLOAD.code
            )
            # 账号配置已重置，应该继承用户配置
            assert value == True
            self.log_test_result("获取有效配置", True, f"有效值: {value}")
        except Exception as e:
            self.log_test_result("获取有效配置", False, str(e))

    # ========== 删除测试 ==========

    async def test_delete_account(self):
        """测试15: 删除账号"""
        print("\n测试15: 删除账号")
        try:
            await self.account_service.delete_account(self.test_user_id, self.created_account_id)
            # 验证已删除（软删除）
            accounts = await self.account_service.get_accounts(self.test_user_id)
            for acc in accounts:
                assert acc.id != self.created_account_id, "账号应该已被删除"
            self.log_test_result("删除账号", True, "软删除成功")
        except Exception as e:
            self.log_test_result("删除账号", False, str(e))

    async def run_all_tests(self):
        print("=" * 80)
        print("开始账号模块测试")
        print("=" * 80)

        try:
            await self.setup_test_database()

            # 枚举测试
            await self.test_channel_enum()
            await self.test_project_enum()
            await self.test_project_to_dict()

            # 账号管理测试
            await self.test_create_account()
            await self.test_get_accounts()
            await self.test_update_account()
            await self.test_get_nonexistent_account()

            # 绑定测试
            await self.test_bindding()
            await self.test_bindding_invalid_channel()
            await self.test_get_bindings()

            # 账号配置测试
            await self.test_account_setting_inherit()
            await self.test_account_setting_override()
            await self.test_account_setting_reset()
            await self.test_effective_setting()

            # 删除测试
            await self.test_delete_account()

            total = len(self.test_results)
            passed = sum(1 for r in self.test_results if r["success"])
            print("\n" + "=" * 80)
            print(f"测试结果: {passed}/{total} 通过，成功率 {passed/total*100:.0f}%")
            print("=" * 80)

        finally:
            await self.cleanup_test_database()


async def main():
    tester = AccountTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

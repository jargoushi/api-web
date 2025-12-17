# 认证功能测试文件
import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi.testclient import TestClient
from app.db.config import init_db, close_db
from app.models.account.user import User
from app.models.account.activation_code import ActivationCode
from app.schemas.account.user import UserRegisterRequest
from app.schemas.account.auth import LoginRequest
from app.schemas.account.activation import ActivationCodeBatchCreateRequest, ActivationCodeCreateItem, ActivationCodeGetRequest
from app.services.account.user_service import UserService
from app.services.account.activation_service import ActivationCodeService
from app.util.jwt import jwt_manager
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum


class AuthModuleTester:
    """认证模块测试类"""

    def __init__(self):
        self.test_results: list = []
        self.test_users: list = []
        self.test_activation_codes: list = []
        self.client = None

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
        # 清理所有测试数据
        await User.all().delete()
        await ActivationCode.all().delete()
        await close_db()
        print("测试数据库清理完成")

    def log_test_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now()
        }
        self.test_results.append(result)

        status = "✓ 成功" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
        if message:
            print(f"    {message}")

    async def setup_test_activation_codes(self):
        """设置测试用的激活码"""
        print("正在设置测试激活码...")

        # 创建测试激活码
        batch_request = ActivationCodeBatchCreateRequest(
            items=[
                ActivationCodeCreateItem(type=ActivationTypeEnum.DAY.code, count=20)
            ]
        )

        batch_result = await ActivationCodeService.init_activation_codes(batch_request)

        # 派发所有激活码
        distribute_request = ActivationCodeGetRequest(type=ActivationTypeEnum.DAY.code, count=20)
        day_codes = await ActivationCodeService.distribute_activation_codes(distribute_request)

        self.test_activation_codes = day_codes
        print(f"成功设置 {len(self.test_activation_codes)} 个测试激活码")

    async def setup_test_users(self):
        """设置测试用户"""
        print("正在设置测试用户...")

        # 创建测试用户
        for i in range(3):
            register_request = UserRegisterRequest(
                username=f"testuser_auth_{i}",
                password="TestPass123",
                activation_code=self.test_activation_codes[i]
            )
            user = await UserService.register_user(register_request)
            self.test_users.append({
                "id": user.id,
                "username": user.username,
                "password": "TestPass123",
                "activation_code": user.activation_code
            })

        print(f"成功设置 {len(self.test_users)} 个测试用户")

    def create_mock_request(self, headers: Dict[str, str] = None) -> Any:
        """创建模拟请求对象"""
        class MockRequest:
            def __init__(self, headers=None):
                self.headers = headers or {}
                self.client = type('Client', (), {'host': '127.0.0.1'})()

        return MockRequest(headers)

    async def test_jwt_token_generation(self):
        """测试JWT token生成"""
        print("\n测试1: JWT Token生成功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[0]

            # 生成token
            token_info = jwt_manager.create_access_token(test_user["id"])

            # 验证token结构
            assert "access_token" in token_info, "缺少access_token"
            assert "token_type" in token_info, "缺少token_type"
            assert "expires_in" in token_info, "缺少expires_in"

            # 验证token值
            assert token_info["token_type"] == "bearer", "token类型错误"
            assert token_info["expires_in"] > 0, "过期时间错误"

            self.log_test_result(
                "JWT Token生成",
                True,
                f"成功生成token",
                token_info
            )

        except Exception as e:
            self.log_test_result("JWT Token生成", False, str(e))

    async def test_jwt_token_verification(self):
        """测试JWT token验证"""
        print("\n测试2: JWT Token验证功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[1]

            # 生成token
            token_info = jwt_manager.create_access_token(test_user["id"])
            token = token_info["access_token"]

            # 验证token
            payload = jwt_manager.verify_token(token)

            # 验证载荷内容
            assert payload["user_id"] == test_user["id"], "用户ID不匹配"

            self.log_test_result(
                "JWT Token验证",
                True,
                f"成功验证token，用户ID: {payload['user_id']}",
                payload
            )

        except Exception as e:
            self.log_test_result("JWT Token验证", False, str(e))

    async def test_user_login(self):
        """测试用户登录"""
        print("\n测试3: 用户登录功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[2]
            mock_request = self.create_mock_request()

            # 用户登录
            from app.services.account.auth_service import auth_service
            access_token = await auth_service.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request
            )

            # 验证登录结果
            assert access_token is not None, "登录失败，未返回token"
            assert len(access_token) > 0, "token不能为空"

            self.log_test_result(
                "用户登录",
                True,
                f"用户 {test_user['username']} 登录成功",
                {"access_token": access_token[:20] + "..."}
            )

        except Exception as e:
            self.log_test_result("用户登录", False, str(e))

    async def test_user_logout(self):
        """测试用户注销"""
        print("\n测试4: 用户注销功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[1]

            # 先登录
            mock_request = self.create_mock_request()
            from app.services.account.auth_service import auth_service
            token = await auth_service.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request
            )

            # 注销用户（无状态JWT只需记录日志）
            await auth_service.logout_user(token)

            self.log_test_result(
                "用户注销",
                True,
                f"用户 {test_user['username']} 注销成功"
            )

        except Exception as e:
            self.log_test_result("用户注销", False, str(e))

    async def test_password_authentication(self):
        """测试密码认证功能"""
        print("\n测试5: 密码认证功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[1]
            from app.services.account.auth_service import auth_service

            # 测试正确的密码
            correct_auth = await auth_service.authenticate_user(
                test_user["username"],
                test_user["password"]
            )
            assert correct_auth.username == test_user["username"], "正确密码认证应该成功"

            # 测试错误的密码
            try:
                await auth_service.authenticate_user(
                    test_user["username"],
                    "WrongPassword123"
                )
                wrong_password_success = True  # 不应该成功
            except Exception:
                wrong_password_success = False

            # 测试不存在的用户
            try:
                await auth_service.authenticate_user(
                    "nonexistentuser",
                    "SomePassword123"
                )
                nonexistent_user_success = True  # 不应该成功
            except Exception:
                nonexistent_user_success = False

            # 验证结果
            assert wrong_password_success is False, "错误密码应该认证失败"
            assert nonexistent_user_success is False, "不存在用户应该认证失败"

            self.log_test_result(
                "密码认证",
                True,
                "密码认证功能正常",
                {
                    "correct_password": True,
                    "wrong_password_rejected": not wrong_password_success,
                    "nonexistent_user_rejected": not nonexistent_user_success
                }
            )

        except Exception as e:
            self.log_test_result("密码认证", False, str(e))

    async def test_complete_auth_flow(self):
        """测试完整认证流程"""
        print("\n测试6: 完整认证流程测试")

        try:
            if not self.test_activation_codes:
                raise Exception("没有可用的测试激活码")

            # 使用新的激活码创建用户
            register_request = UserRegisterRequest(
                username="flow_test_user",
                password="FlowTest123",
                activation_code=self.test_activation_codes[10]
            )
            user = await UserService.register_user(register_request)

            # 1. 用户登录
            mock_request = self.create_mock_request()

            from app.services.account.auth_service import auth_service
            token = await auth_service.login_user(
                username=user.username,
                password="FlowTest123",
                request=mock_request
            )
            assert token is not None, "登录应该返回token"

            # 2. 验证token
            payload = jwt_manager.verify_token(token)
            assert payload["user_id"] == user.id, "token用户ID应该匹配"

            # 3. 注销用户
            await auth_service.logout_user(token)

            self.log_test_result(
                "完整认证流程",
                True,
                f"用户 {user.username} 完成完整认证流程",
                {"login": True, "token_valid": True, "logout": True}
            )

        except Exception as e:
            self.log_test_result("完整认证流程", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("开始认证模块完整测试")
        print("=" * 80)

        try:
            # 初始化测试环境
            await self.setup_test_database()
            await self.setup_test_activation_codes()
            await self.setup_test_users()

            # 运行所有测试
            await self.test_jwt_token_generation()
            await self.test_jwt_token_verification()
            await self.test_user_login()
            await self.test_user_logout()
            await self.test_password_authentication()
            await self.test_complete_auth_flow()

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
            print(f"成功率: {passed_tests/total_tests*100:.1f}%")

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
        print("认证模块测试完成")
        print("=" * 80)


# 测试入口函数
async def main():
    """主测试入口"""
    tester = AuthModuleTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(main())

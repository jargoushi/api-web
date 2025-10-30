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
from app.models.user import User
from app.models.user_session import UserSession
from app.models.activation_code import ActivationCode
from app.schemas.user import UserRegisterRequest
from app.schemas.auth import LoginRequest
from app.schemas.activation_code import ActivationCodeBatchCreateRequest, ActivationCodeCreateItem, ActivationCodeGetRequest
from app.services.user_service import UserService
from app.services.activation_code_service import ActivationCodeService
from app.util.jwt import get_jwt_manager
from app.enums.activation_code_enum import ActivationTypeEnum
from app.enums.activation_code_status_enum import ActivationCodeStatusEnum


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
        await UserSession.all().delete()
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
            mock_request = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "X-Forwarded-For": "192.168.1.100"
            })

            # 生成token
            from app.util.jwt import create_user_token
            token_info = create_user_token(test_user["id"], mock_request)

            # 验证token结构
            assert "access_token" in token_info, "缺少access_token"
            assert "token_type" in token_info, "缺少token_type"
            assert "expires_in" in token_info, "缺少expires_in"
            assert "device_id" in token_info, "缺少device_id"

            # 验证token值
            assert token_info["token_type"] == "bearer", "token类型错误"
            assert token_info["expires_in"] > 0, "过期时间错误"
            assert len(token_info["device_id"]) > 0, "设备ID不能为空"

            self.log_test_result(
                "JWT Token生成",
                True,
                f"成功生成token，设备ID: {token_info['device_id'][:8]}...",
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
            mock_request = self.create_mock_request()

            # 生成token
            from app.util.jwt import create_user_token, verify_user_token
            token_info = create_user_token(test_user["id"], mock_request)
            token = token_info["access_token"]

            # 验证token
            payload = verify_user_token(token)

            # 验证载荷内容
            assert payload["user_id"] == test_user["id"], "用户ID不匹配"
            assert "device_id" in payload, "缺少设备ID"
            assert "exp" in payload, "缺少过期时间"

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
            mock_request = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "X-Forwarded-For": "10.0.0.50"
            })

            # 用户登录
            login_info = await UserService.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request
            )

            # 验证登录结果
            assert "access_token" in login_info, "缺少access_token"
            assert "user" in login_info, "缺少用户信息"
            assert "device_info" in login_info, "缺少设备信息"

            # UserResponse是对象，需要用属性访问
            assert login_info["user"].username == test_user["username"], "用户名不匹配"
            assert login_info["device_info"]["ip_address"] == "10.0.0.50", "IP地址不匹配"

            # 验证会话创建
            session = await UserSession.get_session_by_token(login_info["access_token"])
            assert session is not None, "会话未创建"
            assert session.user_id == test_user["id"], "会话用户ID不匹配"

            self.log_test_result(
                "用户登录",
                True,
                f"用户 {test_user['username']} 登录成功，设备: {login_info['device_info']['device_name']}",
                login_info
            )

        except Exception as e:
            self.log_test_result("用户登录", False, str(e))

    async def test_single_device_login(self):
        """测试单设备登录限制"""
        print("\n测试4: 单设备登录限制")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[0]

            # 第一次登录
            mock_request1 = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                "X-Forwarded-For": "192.168.1.10"
            })

            login_info1 = await UserService.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request1
            )

            token1 = login_info1["access_token"]
            session1 = await UserSession.get_session_by_token(token1)
            assert session1 is not None, "第一次登录会话未创建"

            # 第二次登录（不同设备）
            mock_request2 = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0",
                "X-Forwarded-For": "192.168.1.20"
            })

            login_info2 = await UserService.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request2
            )

            token2 = login_info2["access_token"]
            session2 = await UserSession.get_session_by_token(token2)
            assert session2 is not None, "第二次登录会话未创建"

            # 验证第一个会话被踢出
            old_session1 = await UserSession.get_session_by_token(token1)
            assert old_session1 is None, "旧会话应该被踢出"

            # 验证数据库中只有一个活跃会话
            active_sessions = await UserSession.filter(
                user_id=test_user["id"],
                is_active=True
            )
            assert len(active_sessions) == 1, "应该只有一个活跃会话"

            self.log_test_result(
                "单设备登录限制",
                True,
                "新设备登录成功，旧设备会话被踢出",
                {
                    "new_session_device": session2.device_name,
                    "old_session_invalidated": True
                }
            )

        except Exception as e:
            self.log_test_result("单设备登录限制", False, str(e))

    async def test_user_logout(self):
        """测试用户注销"""
        print("\n测试5: 用户注销功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[1]

            # 先登录
            mock_request = self.create_mock_request()
            login_info = await UserService.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request
            )

            token = login_info["access_token"]

            # 验证会话存在
            session = await UserSession.get_session_by_token(token)
            assert session is not None, "登录后应该存在会话"

            # 注销用户
            logout_success = await UserService.logout_user(token, test_user["id"])
            assert logout_success is True, "注销应该成功"

            # 验证会话被删除
            deleted_session = await UserSession.get_session_by_token(token)
            assert deleted_session is None, "注销后会话应该被删除"

            self.log_test_result(
                "用户注销",
                True,
                f"用户 {test_user['username']} 注销成功",
                {"logout_success": logout_success}
            )

        except Exception as e:
            self.log_test_result("用户注销", False, str(e))

    async def test_activation_code_expiration(self):
        """测试激活码过期检测"""
        print("\n测试6: 激活码过期检测")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[2]

            # 获取用户的激活码
            activation_code_obj = await ActivationCode.get(activation_code=test_user["activation_code"])
            if not activation_code_obj:
                raise Exception("找不到激活码")

            # 测试正常情况（未过期）
            try:
                await UserService.authenticate_user(test_user["username"], test_user["password"])
                auth_success = True
            except:
                auth_success = False

            # 手动设置激活码为过期状态（用于测试）
            from app.util.time_util import get_utc_now
            original_expire_time = activation_code_obj.expire_time
            activation_code_obj.expire_time = get_utc_now() - timedelta(hours=1)
            await activation_code_obj.save()

            # 测试过期情况
            try:
                await UserService.authenticate_user(test_user["username"], test_user["password"])
                expired_auth_success = True  # 不应该成功
            except Exception as auth_error:
                expired_auth_success = False
                error_message = str(auth_error)

            # 恢复激活码状态
            activation_code_obj.expire_time = original_expire_time
            await activation_code_obj.save()

            # 验证结果
            assert auth_success is True, "正常情况下应该认证成功"
            assert expired_auth_success is False, "过期情况下应该认证失败"
            assert "激活码已过期" in error_message, "错误消息应该包含过期信息"

            self.log_test_result(
                "激活码过期检测",
                True,
                "成功检测到激活码过期",
                {
                    "normal_auth": auth_success,
                    "expired_auth": expired_auth_success,
                    "error_message": error_message
                }
            )

        except Exception as e:
            self.log_test_result("激活码过期检测", False, str(e))

    async def test_token_refresh(self):
        """测试Token刷新功能"""
        print("\n测试7: Token刷新功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[0]

            # 先登录获取token
            mock_request1 = self.create_mock_request({
                "User-Agent": "TestAgent/1.0",
                "X-Forwarded-For": "10.0.0.100"
            })

            login_info = await UserService.login_user(
                username=test_user["username"],
                password=test_user["password"],
                request=mock_request1
            )

            old_token = login_info["access_token"]

            # 刷新token
            mock_request2 = self.create_mock_request({
                "User-Agent": "TestAgent/1.0",
                "X-Forwarded-For": "10.0.0.100"
            })

            refresh_info = await UserService.refresh_token(old_token, mock_request2)
            new_token = refresh_info["access_token"]

            # 验证新token
            assert new_token != old_token, "新token应该不同于旧token"
            assert "access_token" in refresh_info, "刷新响应应该包含新token"

            # 验证新token有效
            from app.util.jwt import verify_user_token
            payload = verify_user_token(new_token)
            assert payload["user_id"] == test_user["id"], "新token用户ID应该匹配"

            # 验证旧token被加入黑名单
            jwt_manager = get_jwt_manager()
            is_blacklisted = jwt_manager.is_blacklisted(old_token)
            assert is_blacklisted is True, "旧token应该被加入黑名单"

            # 验证旧会话被删除
            old_session = await UserSession.get_session_by_token(old_token)
            assert old_session is None, "旧会话应该被删除"

            # 验证新会话被创建
            new_session = await UserSession.get_session_by_token(new_token)
            assert new_session is not None, "新会话应该被创建"
            assert new_session.user_id == test_user["id"], "新会话用户ID应该匹配"

            self.log_test_result(
                "Token刷新",
                True,
                "Token刷新成功，旧token失效，新token生效",
                {
                    "old_token_blacklisted": is_blacklisted,
                    "new_token_valid": True,
                    "session_rotated": True
                }
            )

        except Exception as e:
            self.log_test_result("Token刷新", False, str(e))

    async def test_password_authentication(self):
        """测试密码认证功能"""
        print("\n测试8: 密码认证功能")

        try:
            if not self.test_users:
                raise Exception("没有可用的测试用户")

            test_user = self.test_users[1]

            # 测试正确的密码
            correct_auth = await UserService.authenticate_user(
                test_user["username"],
                test_user["password"]
            )
            assert correct_auth.username == test_user["username"], "正确密码认证应该成功"

            # 测试错误的密码
            try:
                await UserService.authenticate_user(
                    test_user["username"],
                    "WrongPassword123"
                )
                wrong_password_success = True  # 不应该成功
            except Exception:
                wrong_password_success = False

            # 测试不存在的用户
            try:
                await UserService.authenticate_user(
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

    async def test_device_fingerprint_generation(self):
        """测试设备指纹生成"""
        print("\n测试9: 设备指纹生成")

        try:
            jwt_manager = get_jwt_manager()

            # 测试相同请求应该生成相同指纹
            mock_request1 = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "X-Forwarded-For": "192.168.1.100"
            })

            mock_request2 = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "X-Forwarded-For": "192.168.1.100"
            })

            fingerprint1 = jwt_manager.generate_device_fingerprint(mock_request1)
            fingerprint2 = jwt_manager.generate_device_fingerprint(mock_request2)

            assert fingerprint1 == fingerprint2, "相同请求应该生成相同指纹"
            assert len(fingerprint1) == 64, "指纹长度应该是64位（SHA256）"

            # 测试不同请求应该生成不同指纹
            mock_request3 = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "X-Forwarded-For": "192.168.1.100"
            })

            fingerprint3 = jwt_manager.generate_device_fingerprint(mock_request3)
            assert fingerprint1 != fingerprint3, "不同User-Agent应该生成不同指纹"

            mock_request4 = self.create_mock_request({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "X-Forwarded-For": "192.168.1.200"
            })

            fingerprint4 = jwt_manager.generate_device_fingerprint(mock_request4)
            assert fingerprint1 != fingerprint4, "不同IP地址应该生成不同指纹"

            self.log_test_result(
                "设备指纹生成",
                True,
                "设备指纹生成功能正常",
                {
                    "fingerprint_length": len(fingerprint1),
                    "same_request_same_fingerprint": fingerprint1 == fingerprint2,
                    "different_ua_different_fingerprint": fingerprint1 != fingerprint3,
                    "different_ip_different_fingerprint": fingerprint1 != fingerprint4
                }
            )

        except Exception as e:
            self.log_test_result("设备指纹生成", False, str(e))

    async def test_complete_auth_flow(self):
        """测试完整认证流程"""
        print("\n测试10: 完整认证流程测试")

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
            mock_request = self.create_mock_request({
                "User-Agent": "FlowTest Agent/1.0",
                "X-Forwarded-For": "10.10.10.10"
            })

            login_info = await UserService.login_user(
                username=user.username,
                password="FlowTest123",
                request=mock_request
            )

            token = login_info["access_token"]
            assert token is not None, "登录应该返回token"

            # 2. 验证token
            from app.util.jwt import verify_user_token
            payload = verify_user_token(token)
            assert payload["user_id"] == user.id, "token用户ID应该匹配"

            # 3. 检查会话
            session = await UserSession.get_session_by_token(token)
            assert session is not None, "应该存在活跃会话"
            assert session.is_active is True, "会话应该是活跃的"

            # 4. 刷新token
            refresh_info = await UserService.refresh_token(token, mock_request)
            new_token = refresh_info["access_token"]
            assert new_token != token, "新token应该不同于旧token"

            # 5. 注销用户
            logout_success = await UserService.logout_user(new_token, user.id)
            assert logout_success is True, "注销应该成功"

            # 6. 验证注销后状态
            final_session = await UserSession.get_session_by_token(new_token)
            assert final_session is None, "注销后会话应该被删除"

            jwt_manager = get_jwt_manager()
            is_token_blacklisted = jwt_manager.is_blacklisted(new_token)
            assert is_token_blacklisted is True, "注销后token应该被加入黑名单"

            self.log_test_result(
                "完整认证流程",
                True,
                f"用户 {user.username} 完成完整认证流程",
                {
                    "login": True,
                    "token_valid": True,
                    "session_created": True,
                    "token_refreshed": True,
                    "logout": True,
                    "session_cleaned": True,
                    "token_blacklisted": True
                }
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
            await self.test_single_device_login()
            await self.test_user_logout()
            await self.test_activation_code_expiration()
            await self.test_token_refresh()
            await self.test_password_authentication()
            await self.test_device_fingerprint_generation()
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
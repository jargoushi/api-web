# 用户模块测试文件
import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.config import init_db, close_db
from app.models.account.user import User
from app.models.account.activation_code import ActivationCode
from app.schemas.account.user import (
    UserRegisterRequest,
    UserUpdateRequest,
    UserQueryRequest
)
from app.schemas.account.activation import (
    ActivationCodeBatchCreateRequest,
    ActivationCodeCreateItem,
    ActivationCodeGetRequest
)
from app.services.account.user_service import UserService
from app.services.account.activation_service import ActivationCodeService
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum


class UserModuleTester:
    """用户模块测试类"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_users: List[Dict[str, Any]] = []
        self.test_activation_codes: List[str] = []

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

        # 创建更多测试激活码，确保足够测试使用
        batch_request = ActivationCodeBatchCreateRequest(
            items=[
                ActivationCodeCreateItem(type=ActivationTypeEnum.DAY.code, count=15),
                ActivationCodeCreateItem(type=ActivationTypeEnum.MONTH.code, count=5),
                ActivationCodeCreateItem(type=ActivationTypeEnum.YEAR.code, count=5)
            ]
        )

        batch_result = await ActivationCodeService.init_activation_codes(batch_request)

        # 派发所有激活码
        distribute_request = ActivationCodeGetRequest(type=ActivationTypeEnum.DAY.code, count=15)
        day_codes = await ActivationCodeService.distribute_activation_codes(distribute_request)

        distribute_request = ActivationCodeGetRequest(type=ActivationTypeEnum.MONTH.code, count=5)
        month_codes = await ActivationCodeService.distribute_activation_codes(distribute_request)

        distribute_request = ActivationCodeGetRequest(type=ActivationTypeEnum.YEAR.code, count=5)
        year_codes = await ActivationCodeService.distribute_activation_codes(distribute_request)

        self.test_activation_codes = day_codes + month_codes + year_codes
        print(f"成功设置 {len(self.test_activation_codes)} 个测试激活码")

    async def test_user_registration(self):
        """测试用户注册功能"""
        print("\n测试1: 用户注册功能")

        try:
            if not self.test_activation_codes:
                raise Exception("没有可用的测试激活码")

            test_activation_code = self.test_activation_codes[0]

            # 创建注册请求
            register_request = UserRegisterRequest(
                username="testuser1",
                password="TestPass123",
                activation_code=test_activation_code
            )

            # 执行注册
            user_result = await UserService.register_user(register_request)

            # 验证注册结果
            assert user_result.username == "testuser1", "用户名不匹配"
            assert user_result.activation_code == test_activation_code, "激活码不匹配"
            assert user_result.id is not None, "用户ID不能为空"

            # 验证数据库中的用户记录
            user = await User.get(id=user_result.id)
            assert user.username == "testuser1", "数据库用户名不匹配"
            assert user.password == "TestPass123", "数据库密码不匹配"
            assert user.activation_code == test_activation_code, "数据库激活码不匹配"

            # 验证激活码状态
            activation_code_obj = await ActivationCode.get(activation_code=test_activation_code)
            assert activation_code_obj.status == ActivationCodeStatusEnum.ACTIVATED.code, "激活码状态不正确"

            # 保存测试用户
            self.test_users.append({
                "id": user_result.id,
                "username": "testuser1",
                "activation_code": test_activation_code
            })

            self.log_test_result(
                "用户注册",
                True,
                f"成功注册用户 testuser1，激活码 {test_activation_code}",
                {"user_id": user_result.id, "username": user_result.username}
            )

        except Exception as e:
            self.log_test_result("用户注册", False, str(e))

    async def test_password_complexity_validation(self):
        """测试密码复杂度校验"""
        print("\n测试2: 密码复杂度校验")

        if len(self.test_activation_codes) < 8:
            self.log_test_result("密码复杂度校验", False, "测试激活码不足")
            return

        # 测试各种不符合要求的密码
        invalid_passwords = [
            ("short", "密码太短"),
            ("toolongpassword123456", "密码太长"),
            ("nouppercase", "缺少大写字母"),
            ("NOLOWERCASE", "缺少小写字母"),
            ("NoNumbers", "缺少数字"),
            ("12345678", "缺少字母")
        ]

        for i, (password, reason) in enumerate(invalid_passwords):
            try:
                register_request = UserRegisterRequest(
                    username=f"testuser_invalid_{i}",
                    password=password,
                    activation_code=self.test_activation_codes[i + 1]  # 使用不同的激活码
                )
                await UserService.register_user(register_request)
                self.log_test_result(
                    f"密码复杂度校验 - {reason}",
                    False,
                    f"密码 '{password}' 应该被拒绝但没有"
                )
            except Exception as e:
                if ("validation error" in str(e).lower() or
                        "密码" in str(e) and ("长度" in str(e) or "包含" in str(e))):
                    self.log_test_result(
                        f"密码复杂度校验 - {reason}",
                        True,
                        f"正确拒绝了不符合要求的密码: {password}"
                    )
                else:
                    self.log_test_result(
                        f"密码复杂度校验 - {reason}",
                        False,
                        f"错误的异常信息: {str(e)}"
                    )

        # 测试符合要求的密码
        try:
            register_request = UserRegisterRequest(
                username="testuser_valid",
                password="ValidPass123",
                activation_code=self.test_activation_codes[7]  # 使用新的激活码
            )
            user_result = await UserService.register_user(register_request)

            self.test_users.append({
                "id": user_result.id,
                "username": "testuser_valid",
                "activation_code": self.test_activation_codes[7]
            })

            self.log_test_result(
                "密码复杂度校验 - 有效密码",
                True,
                "正确接受了符合要求的密码"
            )
        except Exception as e:
            self.log_test_result("密码复杂度校验 - 有效密码", False, str(e))

    async def test_username_uniqueness(self):
        """测试用户名唯一性校验"""
        print("\n测试3: 用户名唯一性校验")

        if len(self.test_activation_codes) < 2:
            self.log_test_result("用户名唯一性校验", False, "测试激活码不足")
            return

        # 使用不同的激活码
        test_activation_code = self.test_activation_codes[-1]  # 使用最后一个激活码

        # 尝试使用已存在的用户名注册
        try:
            register_request = UserRegisterRequest(
                username="testuser1",  # 已存在的用户名
                password="AnotherPass123",
                activation_code=test_activation_code
            )
            await UserService.register_user(register_request)
            self.log_test_result("用户名唯一性校验", False, "应该拒绝重复的用户名但没有")
        except Exception as e:
            if "用户名已存在" in str(e):
                self.log_test_result("用户名唯一性校验", True, "正确拒绝了重复的用户名")
            else:
                self.log_test_result("用户名唯一性校验", False, f"错误的异常信息: {str(e)}")

    async def test_activation_code_validation(self):
        """测试激活码验证"""
        print("\n测试4: 激活码验证")

        # 测试无效的激活码
        invalid_activation_codes = [
            ("nonexistent_code", "不存在的激活码"),
            ("", "空激活码"),
            ("123", "无效格式激活码")
        ]

        for invalid_code, reason in invalid_activation_codes:
            try:
                register_request = UserRegisterRequest(
                    username=f"testuser_invalid_{reason}",
                    password="TestPass123",
                    activation_code=invalid_code
                )
                await UserService.register_user(register_request)
                self.log_test_result(
                    f"激活码验证 - {reason}",
                    False,
                    f"应该拒绝无效激活码 '{invalid_code}' 但没有"
                )
            except Exception as e:
                if ("激活码" in str(e) or
                        "validation error" in str(e).lower() or
                        "String should have at least" in str(e)):
                    self.log_test_result(
                        f"激活码验证 - {reason}",
                        True,
                        f"正确拒绝了无效激活码: {invalid_code}"
                    )
                else:
                    self.log_test_result(
                        f"激活码验证 - {reason}",
                        False,
                        f"错误的异常信息: {str(e)}"
                    )

    async def test_user_update(self):
        """测试用户信息更新"""
        print("\n测试5: 用户信息更新")

        if not self.test_users:
            self.log_test_result("用户信息更新", False, "没有可用的测试用户")
            return

        test_user = self.test_users[0]

        try:
            # 更新手机号和邮箱
            update_request = UserUpdateRequest(
                phone="13812345678",
                email="test@example.com"
            )

            updated_user = await UserService.update_user(test_user["id"], update_request)

            # 验证更新结果
            assert updated_user.phone == "13812345678", "手机号更新失败"
            assert updated_user.email == "test@example.com", "邮箱更新失败"

            # 验证数据库中的更新
            user = await User.get(id=test_user["id"])
            assert user.phone == "13812345678", "数据库手机号更新失败"
            assert user.email == "test@example.com", "数据库邮箱更新失败"

            self.log_test_result(
                "用户信息更新",
                True,
                f"成功更新用户 {test_user['username']} 的手机号和邮箱",
                {"phone": updated_user.phone, "email": updated_user.email}
            )

        except Exception as e:
            self.log_test_result("用户信息更新", False, str(e))

    async def test_phone_number_validation(self):
        """测试手机号格式校验"""
        print("\n测试6: 手机号格式校验")

        if not self.test_users:
            self.log_test_result("手机号格式校验", False, "没有可用的测试用户")
            return

        test_user = self.test_users[0]

        # 测试无效的手机号格式
        invalid_phones = [
            ("12345678901", "不以1开头"),
            ("1234567890", "长度不正确"),
            ("1881234567", "长度不正确"),
            ("10812345678", "第二位不是3-9"),
            ("abcdefghijk", "包含非数字字符")
        ]

        for invalid_phone, reason in invalid_phones:
            try:
                update_request = UserUpdateRequest(phone=invalid_phone)
                await UserService.update_user(test_user["id"], update_request)
                self.log_test_result(
                    f"手机号格式校验 - {reason}",
                    False,
                    f"应该拒绝无效手机号 '{invalid_phone}' 但没有"
                )
            except Exception as e:
                if "手机号格式" in str(e):
                    self.log_test_result(
                        f"手机号格式校验 - {reason}",
                        True,
                        f"正确拒绝了无效手机号: {invalid_phone}"
                    )
                else:
                    self.log_test_result(
                        f"手机号格式校验 - {reason}",
                        False,
                        f"错误的异常信息: {str(e)}"
                    )

        # 测试有效的手机号格式
        valid_phones = ["13812345678", "15987654321", "18812345678"]

        for valid_phone in valid_phones:
            try:
                update_request = UserUpdateRequest(phone=valid_phone)
                updated_user = await UserService.update_user(test_user["id"], update_request)

                self.log_test_result(
                    f"手机号格式校验 - 有效号码",
                    True,
                    f"正确接受了有效手机号: {valid_phone}"
                )
            except Exception as e:
                self.log_test_result(
                    f"手机号格式校验 - 有效号码",
                    False,
                    f"应该接受有效手机号 '{valid_phone}' 但被拒绝: {str(e)}"
                )
                break

    async def test_user_query(self):
        """测试用户查询功能"""
        print("\n测试7: 用户查询功能")

        try:
            # 测试按用户名查询
            query_request = UserQueryRequest(username="testuser1")
            queryset = UserService.get_user_queryset(query_request)
            results = await queryset

            found_testuser = False
            for result in results:
                if "testuser1" in result.username.lower():
                    found_testuser = True
                    break

            assert found_testuser, "按用户名查询失败"

            # 测试按激活码查询
            if self.test_users:
                query_request = UserQueryRequest(activation_code=self.test_users[0]["activation_code"])
                queryset = UserService.get_user_queryset(query_request)
                results = await queryset

                assert len(results) >= 1, "按激活码查询失败"
                assert results[0].activation_code == self.test_users[0]["activation_code"], "激活码匹配失败"

            self.log_test_result(
                "用户查询",
                True,
                f"查询功能正常，测试了用户名和激活码查询",
                {"found_users": len(results) if 'results' in locals() else 0}
            )

        except Exception as e:
            self.log_test_result("用户查询", False, str(e))

    async def test_unique_fields_validation(self):
        """测试唯一性字段校验"""
        print("\n测试8: 唯性字段校验")

        if len(self.test_users) < 2:
            self.log_test_result("唯一性字段校验", False, "测试用户数量不足")
            return

        user1, user2 = self.test_users[0], self.test_users[1]

        try:
            # 尝试使用相同的手机号
            update_request = UserUpdateRequest(phone="13812345678")
            await UserService.update_user(user1["id"], update_request)

            # 尝试为第二个用户设置相同的手机号
            update_request = UserUpdateRequest(phone="13812345678")
            await UserService.update_user(user2["id"], update_request)

            self.log_test_result("唯一性字段校验 - 手机号", False, "应该拒绝重复的手机号但没有")

        except Exception as e:
            if "已被使用" in str(e):
                self.log_test_result("唯一性字段校验 - 手机号", True, "正确拒绝了重复的手机号")
            else:
                self.log_test_result("唯一性字段校验 - 手机号", False, f"错误的异常信息: {str(e)}")

    async def test_exception_scenarios(self):
        """测试异常场景"""
        print("\n测试9: 异常场景测试")

        exception_tests = []

        # 测试1: 更新不存在的用户
        try:
            update_request = UserUpdateRequest(phone="13812345678")
            await UserService.update_user(99999, update_request)
            exception_tests.append({"test": "更新不存在用户", "success": False, "reason": "应该抛出异常但没有"})
        except Exception:
            exception_tests.append({"test": "更新不存在用户", "success": True})

        # 测试2: 查询不存在的用户
        try:
            await UserService.get_user_by_id(99999)
            exception_tests.append({"test": "查询不存在用户", "success": False, "reason": "应该抛出异常但没有"})
        except Exception:
            exception_tests.append({"test": "查询不存在用户", "success": True})

        # 测试3: 注册时用户名为空
        try:
            register_request = UserRegisterRequest(
                username="",
                password="TestPass123",
                activation_code="nonexistent"
            )
            await UserService.register_user(register_request)
            exception_tests.append({"test": "用户名为空注册", "success": False, "reason": "应该抛出异常但没有"})
        except Exception:
            exception_tests.append({"test": "用户名为空注册", "success": True})

        # 统计异常测试结果
        success_count = sum(1 for test in exception_tests if test["success"])
        total_count = len(exception_tests)

        self.log_test_result(
            "异常场景测试",
            success_count == total_count,
            f"通过 {success_count}/{total_count} 个异常测试",
            {"tests": exception_tests}
        )

    async def test_complete_business_flow(self):
        """测试完整的业务流程"""
        print("\n测试10: 完整业务流程测试")

        try:
            if len(self.test_activation_codes) < 5:
                raise Exception("测试激活码不足")

            # 确保使用一个未被使用的激活码
            test_activation_code = self.test_activation_codes[15]  # 使用第16个激活码

            # 1. 用户注册
            register_request = UserRegisterRequest(
                username="flow_test_user",
                password="FlowTest123",
                activation_code=test_activation_code
            )
            user_result = await UserService.register_user(register_request)

            # 2. 验证用户创建成功
            assert user_result.username == "flow_test_user"
            assert user_result.activation_code == test_activation_code

            # 3. 更新用户信息
            update_request = UserUpdateRequest(
                phone="15987654321",
                email="flowtest@example.com"
            )
            updated_user = await UserService.update_user(user_result.id, update_request)

            # 4. 验证更新成功
            assert updated_user.phone == "15987654321"
            assert updated_user.email == "flowtest@example.com"

            # 5. 查询用户信息
            queried_user = await UserService.get_user_by_id(user_result.id)
            assert queried_user.username == "flow_test_user"
            assert queried_user.phone == "15987654321"
            assert queried_user.email == "flowtest@example.com"

            # 6. 验证激活码状态
            activation_code_obj = await ActivationCode.get(activation_code=test_activation_code)
            assert activation_code_obj.status == ActivationCodeStatusEnum.ACTIVATED.code

            self.log_test_result(
                "完整业务流程",
                True,
                f"用户 flow_test_user 完成完整业务流程",
                {
                    "registered": True,
                    "updated": True,
                    "queried": True,
                    "activation_code_activated": True
                }
            )

        except Exception as e:
            self.log_test_result("完整业务流程", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("开始用户模块完整测试")
        print("=" * 80)

        try:
            # 初始化测试环境
            await self.setup_test_database()
            await self.setup_test_activation_codes()

            # 运行所有测试
            await self.test_user_registration()
            await self.test_password_complexity_validation()
            await self.test_username_uniqueness()
            await self.test_activation_code_validation()
            await self.test_user_update()
            await self.test_phone_number_validation()
            await self.test_user_query()
            await self.test_unique_fields_validation()
            await self.test_exception_scenarios()
            await self.test_complete_business_flow()

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
        print("用户模块测试完成")
        print("=" * 80)


# 测试入口函数
async def main():
    """主测试入口"""
    tester = UserModuleTester()
    await tester.run_all_tests()


# 特定测试函数
async def test_only_registration():
    """仅测试注册功能"""
    tester = UserModuleTester()
    await tester.setup_test_database()
    await tester.setup_test_activation_codes()
    await tester.test_user_registration()
    await tester.cleanup_test_database()


async def test_only_validation():
    """仅测试校验功能"""
    tester = UserModuleTester()
    await tester.setup_test_database()
    await tester.setup_test_activation_codes()
    await tester.test_password_complexity_validation()
    await tester.test_phone_number_validation()
    await tester.test_username_uniqueness()
    await tester.cleanup_test_database()


async def test_only_update():
    """仅测试更新功能"""
    tester = UserModuleTester()
    await tester.setup_test_database()
    await tester.setup_test_activation_codes()
    await tester.test_user_registration()  # 先创建用户
    await tester.test_user_update()
    await tester.cleanup_test_database()


async def test_only_complete_flow():
    """仅测试完整流程"""
    tester = UserModuleTester()
    await tester.setup_test_database()
    await tester.setup_test_activation_codes()
    await tester.test_complete_business_flow()
    await tester.cleanup_test_database()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(main())

    # 或者运行特定测试
    # asyncio.run(test_only_registration())
    # asyncio.run(test_only_validation())
    # asyncio.run(test_only_update())
    # asyncio.run(test_only_complete_flow())

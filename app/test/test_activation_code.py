# 激活码模块测试文件
import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.config import init_db, close_db
from app.models.account.activation_code import ActivationCode
from app.schemas.account.activation import (
    ActivationCodeBatchCreateRequest,
    ActivationCodeCreateItem,
    ActivationCodeGetRequest,
    ActivationCodeInvalidateRequest,
    ActivationCodeQueryRequest
)
from app.services.account.activation_service import ActivationCodeService
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum


class ActivationCodeTester:
    """激活码模块测试类"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.created_codes: List[str] = []

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

    async def test_activation_code_initialization(self):
        """测试激活码初始化功能"""
        print("\n测试1: 激活码初始化功能")

        try:
            # 创建批量初始化请求
            request = ActivationCodeBatchCreateRequest(
                items=[
                    ActivationCodeCreateItem(type=ActivationTypeEnum.DAY.code, count=3),
                    ActivationCodeCreateItem(type=ActivationTypeEnum.MONTH.code, count=2),
                    ActivationCodeCreateItem(type=ActivationTypeEnum.YEAR.code, count=1)
                ]
            )

            # 执行初始化
            result = await ActivationCodeService.init_activation_codes(request)

            # 验证结果
            assert result.total_count == 6, f"期望创建6个激活码，实际创建{result.total_count}个"
            assert len(result.results) == 3, f"期望3种类型，实际{len(result.results)}种"
            assert result.summary["日卡"] == 3, f"日卡数量错误"
            assert result.summary["月卡"] == 2, f"月卡数量错误"
            assert result.summary["年卡"] == 1, f"年卡数量错误"

            # 保存创建的激活码用于后续测试
            for type_result in result.results:
                self.created_codes.extend(type_result.activation_codes)

            self.log_test_result(
                "激活码批量初始化",
                True,
                f"成功创建{result.total_count}个激活码",
                {"total": result.total_count, "summary": result.summary}
            )

        except Exception as e:
            self.log_test_result("激活码批量初始化", False, str(e))

    async def test_activation_code_distribution(self):
        """测试激活码分发功能"""
        print("\n测试2: 激活码分发功能")

        try:
            # 分发日卡激活码
            request = ActivationCodeGetRequest(type=ActivationTypeEnum.DAY.code, count=2)
            distributed_codes = await ActivationCodeService.distribute_activation_codes(request)

            # 验证分发结果
            assert len(distributed_codes) == 2, f"期望分发2个激活码，实际分发{len(distributed_codes)}个"

            # 验证数据库中的状态更新
            for code_str in distributed_codes:
                code = await ActivationCode.get_or_none(activation_code=code_str)
                assert code is not None, f"激活码{code_str}未找到"
                assert code.status == ActivationCodeStatusEnum.DISTRIBUTED.code, f"激活码状态错误"
                assert code.distributed_at is not None, f"分发时间未设置"
                assert code.activated_at is None, f"激活时间不应设置"

            self.log_test_result(
                "激活码分发",
                True,
                f"成功分发{len(distributed_codes)}个激活码",
                {"distributed_count": len(distributed_codes)}
            )

        except Exception as e:
            self.log_test_result("激活码分发", False, str(e))

    async def test_activation_code_activation(self):
        """测试激活码激活功能"""
        print("\n测试3: 激活码激活功能")

        try:
            # 获取一个已分发的激活码进行激活
            distributed_code = await ActivationCode.filter(
                status=ActivationCodeStatusEnum.DISTRIBUTED.code
            ).first()

            assert distributed_code is not None, "没有找到已分发的激活码"

            # 执行激活
            result = await ActivationCodeService.activate_activation_code(distributed_code.activation_code)

            # 验证激活结果
            assert result.activation_code == distributed_code.activation_code, "激活码不匹配"
            assert result.status == ActivationCodeStatusEnum.ACTIVATED.code, "激活后状态错误"

            # 验证数据库中的更新
            updated_code = await ActivationCode.get(id=distributed_code.id)
            assert updated_code.status == ActivationCodeStatusEnum.ACTIVATED.code, "数据库状态未更新"
            assert updated_code.activated_at is not None, "激活时间未设置"
            assert updated_code.expire_time is not None, "过期时间未设置"

            self.log_test_result(
                "激活码激活",
                True,
                f"成功激活激活码 {distributed_code.activation_code}",
                {
                    "activated_at": updated_code.activated_at,
                    "expire_time": updated_code.expire_time
                }
            )

        except Exception as e:
            self.log_test_result("激活码激活", False, str(e))

    async def test_activation_code_invalidation(self):
        """测试激活码作废功能"""
        print("\n测试4: 激活码作废功能")

        try:
            # 获取一个已分发的激活码进行作废
            distributed_code = await ActivationCode.filter(
                status=ActivationCodeStatusEnum.DISTRIBUTED.code
            ).first()

            if distributed_code is None:
                # 如果没有已分发的激活码，先分发一个
                request = ActivationCodeGetRequest(type=ActivationTypeEnum.MONTH.code, count=1)
                codes = await ActivationCodeService.distribute_activation_codes(request)
                distributed_code = await ActivationCode.get(activation_code=codes[0])

            # 执行作废
            invalidate_request = ActivationCodeInvalidateRequest(
                activation_code=distributed_code.activation_code
            )
            result = await ActivationCodeService.invalidate_activation_code(invalidate_request)

            # 验证作废结果
            assert result is True, "作废操作失败"

            # 验证数据库中的更新
            invalidated_code = await ActivationCode.get(id=distributed_code.id)
            assert invalidated_code.status == ActivationCodeStatusEnum.INVALID.code, "作废后状态错误"

            self.log_test_result(
                "激活码作废",
                True,
                f"成功作废激活码 {distributed_code.activation_code}",
                {"original_status": distributed_code.status, "new_status": invalidated_code.status}
            )

        except Exception as e:
            self.log_test_result("激活码作废", False, str(e))

    async def test_activation_code_query(self):
        """测试激活码查询功能"""
        print("\n测试5: 激活码查询功能")

        try:
            # 测试分页查询
            query_request = ActivationCodeQueryRequest(
                page=1,
                size=5,
                type=ActivationTypeEnum.DAY.code,
                status=ActivationCodeStatusEnum.UNUSED.code
            )

            queryset = ActivationCodeService.get_activation_code_queryset(query_request)
            results = await queryset

            # 验证查询结果
            for result in results:
                assert result.type == ActivationTypeEnum.DAY.code, "类型过滤错误"
                assert result.status == ActivationCodeStatusEnum.UNUSED.code, "状态过滤错误"

            # 测试按激活码查询
            if self.created_codes:
                single_query = ActivationCodeQueryRequest(
                    activation_code=self.created_codes[0]
                )
                single_queryset = ActivationCodeService.get_activation_code_queryset(single_query)
                single_results = await single_queryset

                assert len(single_results) <= 1, "精确查询结果过多"
                if single_results:
                    assert single_results[0].activation_code == self.created_codes[0], "激活码匹配错误"

            self.log_test_result(
                "激活码查询",
                True,
                f"查询功能正常，找到{len(results)}条记录",
                {"query_count": len(results)}
            )

        except Exception as e:
            self.log_test_result("激活码查询", False, str(e))

    async def test_complete_business_flow(self):
        """测试完整的业务流程"""
        print("\n测试6: 完整业务流程测试")

        try:
            # 1. 初始化永久卡激活码
            batch_request = ActivationCodeBatchCreateRequest(
                items=[ActivationCodeCreateItem(type=ActivationTypeEnum.PERMANENT.code, count=1)]
            )
            batch_result = await ActivationCodeService.init_activation_codes(batch_request)

            test_code = batch_result.results[0].activation_codes[0]

            # 2. 分发激活码
            get_request = ActivationCodeGetRequest(
                type=ActivationTypeEnum.PERMANENT.code,
                count=1
            )
            distributed_codes = await ActivationCodeService.distribute_activation_codes(get_request)

            assert test_code in distributed_codes, "分发失败"

            # 3. 激活激活码
            activate_result = await ActivationCodeService.activate_activation_code(test_code)

            assert activate_result.status == ActivationCodeStatusEnum.ACTIVATED.code, "激活失败"

            # 4. 查询激活码详情
            detail_result = await ActivationCodeService.get_activation_code_by_code(test_code)

            assert detail_result.activation_code == test_code, "详情查询失败"
            assert detail_result.distributed_at is not None, "分发时间缺失"
            assert detail_result.activated_at is not None, "激活时间缺失"
            assert detail_result.expire_time is not None, "过期时间缺失"

            # 5. 作废激活码
            invalidate_request = ActivationCodeInvalidateRequest(activation_code=test_code)
            invalidate_result = await ActivationCodeService.invalidate_activation_code(invalidate_request)

            assert invalidate_result is True, "作废失败"

            self.log_test_result(
                "完整业务流程",
                True,
                f"激活码 {test_code} 完成完整生命周期测试",
                {
                    "initialized": True,
                    "distributed": True,
                    "activated": True,
                    "queried": True,
                    "invalidated": True
                }
            )

        except Exception as e:
            self.log_test_result("完整业务流程", False, str(e))

    async def test_exception_scenarios(self):
        """测试异常场景"""
        print("\n测试7: 异常场景测试")

        exception_tests = []

        # 测试1: 分发不存在的激活码类型
        try:
            request = ActivationCodeGetRequest(type=999, count=1)
            await ActivationCodeService.distribute_activation_codes(request)
            exception_tests.append({"test": "分发不存在类型", "success": False, "reason": "应该抛出异常但没有"})
        except Exception:
            exception_tests.append({"test": "分发不存在类型", "success": True})

        # 测试2: 激活未分发的激活码
        try:
            unused_code = await ActivationCode.filter(
                status=ActivationCodeStatusEnum.UNUSED.code
            ).first()
            if unused_code:
                await ActivationCodeService.activate_activation_code(unused_code.activation_code)
                exception_tests.append({"test": "激活未分发激活码", "success": False, "reason": "应该抛出异常但没有"})
            else:
                exception_tests.append({"test": "激活未分发激活码", "success": True, "reason": "没有未分发的激活码"})
        except Exception:
            exception_tests.append({"test": "激活未分发激活码", "success": True})

        # 测试3: 作废未分发的激活码
        try:
            unused_code = await ActivationCode.filter(
                status=ActivationCodeStatusEnum.UNUSED.code
            ).first()
            if unused_code:
                request = ActivationCodeInvalidateRequest(activation_code=unused_code.activation_code)
                await ActivationCodeService.invalidate_activation_code(request)
                exception_tests.append({"test": "作废未分发激活码", "success": False, "reason": "应该抛出异常但没有"})
            else:
                exception_tests.append({"test": "作废未分发激活码", "success": True, "reason": "没有未分发的激活码"})
        except Exception:
            exception_tests.append({"test": "作废未分发激活码", "success": True})

        # 测试4: 激活不存在的激活码
        try:
            await ActivationCodeService.activate_activation_code("non_existent_code")
            exception_tests.append({"test": "激活不存在激活码", "success": False, "reason": "应该抛出异常但没有"})
        except Exception:
            exception_tests.append({"test": "激活不存在激活码", "success": True})

        # 统计异常测试结果
        success_count = sum(1 for test in exception_tests if test["success"])
        total_count = len(exception_tests)

        self.log_test_result(
            "异常场景测试",
            success_count == total_count,
            f"通过 {success_count}/{total_count} 个异常测试",
            {"tests": exception_tests}
        )

    async def test_inventory_management(self):
        """测试库存管理功能"""
        print("\n测试8: 库存管理功能")

        try:
            # 获取各类型激活码的库存状态
            inventory_status = {}

            for enum_type in ActivationTypeEnum:
                unused_count = await ActivationCode.filter(
                    type=enum_type.code,
                    status=ActivationCodeStatusEnum.UNUSED.code
                ).count()

                distributed_count = await ActivationCode.filter(
                    type=enum_type.code,
                    status=ActivationCodeStatusEnum.DISTRIBUTED.code
                ).count()

                activated_count = await ActivationCode.filter(
                    type=enum_type.code,
                    status=ActivationCodeStatusEnum.ACTIVATED.code
                ).count()

                invalid_count = await ActivationCode.filter(
                    type=enum_type.code,
                    status=ActivationCodeStatusEnum.INVALID.code
                ).count()

                inventory_status[enum_type.desc] = {
                    "unused": unused_count,
                    "distributed": distributed_count,
                    "activated": activated_count,
                    "invalid": invalid_count,
                    "total": unused_count + distributed_count + activated_count + invalid_count
                }

            # 验证库存统计的准确性
            total_from_db = await ActivationCode.all().count()
            total_from_stats = sum(
                status["total"] for status in inventory_status.values()
            )

            assert total_from_db == total_from_stats, "库存统计不准确"

            self.log_test_result(
                "库存管理",
                True,
                f"库存统计正常，总计{total_from_db}个激活码",
                {"inventory": inventory_status}
            )

        except Exception as e:
            self.log_test_result("库存管理", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("开始激活码模块完整测试")
        print("=" * 80)

        try:
            # 初始化测试环境
            await self.setup_test_database()

            # 运行所有测试
            await self.test_activation_code_initialization()
            await self.test_activation_code_distribution()
            await self.test_activation_code_activation()
            await self.test_activation_code_invalidation()
            await self.test_activation_code_query()
            await self.test_complete_business_flow()
            await self.test_exception_scenarios()
            await self.test_inventory_management()

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
        print("激活码模块测试完成")
        print("=" * 80)


# 测试入口函数
async def main():
    """主测试入口"""
    tester = ActivationCodeTester()
    await tester.run_all_tests()


# 特定测试函数
async def test_only_initialization():
    """仅测试初始化功能"""
    tester = ActivationCodeTester()
    await tester.setup_test_database()
    await tester.test_activation_code_initialization()
    await tester.cleanup_test_database()


async def test_only_distribution():
    """仅测试分发功能"""
    tester = ActivationCodeTester()
    await tester.setup_test_database()

    # 先创建一些激活码
    await tester.test_activation_code_initialization()
    await tester.test_activation_code_distribution()

    await tester.cleanup_test_database()


async def test_only_activation():
    """仅测试激活功能"""
    tester = ActivationCodeTester()
    await tester.setup_test_database()

    # 先创建和分发激活码
    await tester.test_activation_code_initialization()
    await tester.test_activation_code_distribution()
    await tester.test_activation_code_activation()

    await tester.cleanup_test_database()


async def test_only_full_workflow():
    """仅测试完整工作流"""
    tester = ActivationCodeTester()
    await tester.setup_test_database()
    await tester.test_complete_business_flow()
    await tester.cleanup_test_database()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(main())

    # 或者运行特定测试
    # asyncio.run(test_only_initialization())
    # asyncio.run(test_only_distribution())
    # asyncio.run(test_only_activation())
    # asyncio.run(test_only_full_workflow())

# 监控模块测试文件
import asyncio
import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.db.config import init_db, close_db
from app.models.monitor.monitor_config import MonitorConfig
from app.models.monitor.monitor_daily_stats import MonitorDailyStats
from app.models.monitor_task import MonitorTask
from app.schemas.monitor.monitor import (
    MonitorConfigCreateRequest,
    MonitorConfigUpdateRequest,
    MonitorConfigToggleRequest,
    MonitorConfigQueryRequest,
    MonitorDailyStatsQueryRequest,
    MonitorTaskQueryRequest
)
from app.services.monitor.monitor_service import MonitorService
from app.services.monitor_task_service import MonitorTaskService
from app.enums.common.channel import ChannelEnum
from app.enums.monitor.task_type import TaskTypeEnum
from app.enums.monitor.task_status import TaskStatusEnum


class MonitorTester:
    """监控模块测试类"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_user_id = 1
        self.created_config_ids: List[int] = []

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
        await MonitorConfig.all().delete()
        await MonitorDailyStats.all().delete()
        await MonitorTask.all().delete()
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

    async def test_create_monitor_config(self):
        """测试创建监控配置"""
        print("\n测试1: 创建监控配置")

        try:
            # 创建抖音监控配置
            request = MonitorConfigCreateRequest(
                channel_code=ChannelEnum.DOUYIN.code,
                target_url="https://www.douyin.com/user/test123"
            )

            result = await MonitorService.create_monitor_config(self.test_user_id, request)

            # 验证结果
            assert result.user_id == self.test_user_id, "用户ID不匹配"
            assert result.channel_code == ChannelEnum.DOUYIN.code, "渠道编码不匹配"
            assert result.channel_name == "抖音", "渠道名称不匹配"
            assert result.target_url == request.target_url, "目标链接不匹配"
            assert result.is_active == 1, "默认应该启用"

            self.created_config_ids.append(result.id)

            self.log_test_result(
                "创建监控配置",
                True,
                f"成功创建配置ID: {result.id}",
                {"config_id": result.id, "channel": result.channel_name}
            )

        except Exception as e:
            self.log_test_result("创建监控配置", False, str(e))

    async def test_create_multiple_configs(self):
        """测试创建多个监控配置"""
        print("\n测试2: 创建多个监控配置")

        try:
            channels = [
                (ChannelEnum.DOUYIN.code, "https://www.douyin.com/user/456789"),
                (ChannelEnum.YOUTUBE.code, "https://www.youtube.com/@testchannel"),
            ]

            created_count = 0
            for channel_code, url in channels:
                request = MonitorConfigCreateRequest(
                    channel_code=channel_code,
                    target_url=url
                )
                result = await MonitorService.create_monitor_config(self.test_user_id, request)
                self.created_config_ids.append(result.id)
                created_count += 1

            self.log_test_result(
                "创建多个监控配置",
                True,
                f"成功创建{created_count}个配置",
                {"count": created_count}
            )

        except Exception as e:
            self.log_test_result("创建多个监控配置", False, str(e))

    async def test_query_monitor_configs(self):
        """测试查询监控配置列表"""
        print("\n测试3: 查询监控配置列表")

        try:
            # 测试基础分页查询
            params = MonitorConfigQueryRequest(page=1, size=10)
            queryset = MonitorService.get_monitor_config_queryset(self.test_user_id, params)
            results = await queryset

            assert len(results) > 0, "应该有配置记录"

            # 测试按渠道筛选
            params_channel = MonitorConfigQueryRequest(
                page=1,
                size=10,
                channel_code=ChannelEnum.DOUYIN.code
            )
            queryset_channel = MonitorService.get_monitor_config_queryset(self.test_user_id, params_channel)
            results_channel = await queryset_channel

            for config in results_channel:
                assert config.channel_code == ChannelEnum.DOUYIN.code, "渠道筛选失败"

            # 测试按启用状态筛选
            params_active = MonitorConfigQueryRequest(
                page=1,
                size=10,
                is_active=1
            )
            queryset_active = MonitorService.get_monitor_config_queryset(self.test_user_id, params_active)
            results_active = await queryset_active

            for config in results_active:
                assert config.is_active == 1, "状态筛选失败"

            self.log_test_result(
                "查询监控配置列表",
                True,
                f"查询成功，共{len(results)}条记录",
                {"total": len(results), "filtered_by_channel": len(results_channel)}
            )

        except Exception as e:
            self.log_test_result("查询监控配置列表", False, str(e))

    async def test_update_monitor_config(self):
        """测试修改监控配置"""
        print("\n测试4: 修改监控配置")

        try:
            if not self.created_config_ids:
                raise Exception("没有可用的配置ID")

            config_id = self.created_config_ids[0]
            new_url = "https://www.douyin.com/user/updated123"

            request = MonitorConfigUpdateRequest(target_url=new_url)
            result = await MonitorService.update_monitor_config(
                self.test_user_id,
                config_id,
                request
            )

            # 验证更新结果
            assert result.id == config_id, "配置ID不匹配"
            assert result.target_url == new_url, "链接未更新"

            # 验证数据库中的更新
            updated_config = await MonitorConfig.get(id=config_id)
            assert updated_config.target_url == new_url, "数据库未更新"

            self.log_test_result(
                "修改监控配置",
                True,
                f"成功修改配置ID: {config_id}",
                {"config_id": config_id, "new_url": new_url}
            )

        except Exception as e:
            self.log_test_result("修改监控配置", False, str(e))

    async def test_toggle_monitor_config(self):
        """测试切换监控状态"""
        print("\n测试5: 切换监控状态")

        try:
            if not self.created_config_ids:
                raise Exception("没有可用的配置ID")

            config_id = self.created_config_ids[0]

            # 禁用监控
            disable_request = MonitorConfigToggleRequest(is_active=0)
            result = await MonitorService.toggle_monitor_config(
                self.test_user_id,
                config_id,
                disable_request
            )

            assert result.is_active == 0, "禁用失败"

            # 启用监控
            enable_request = MonitorConfigToggleRequest(is_active=1)
            result = await MonitorService.toggle_monitor_config(
                self.test_user_id,
                config_id,
                enable_request
            )

            assert result.is_active == 1, "启用失败"

            self.log_test_result(
                "切换监控状态",
                True,
                f"成功切换配置ID: {config_id} 的状态",
                {"config_id": config_id}
            )

        except Exception as e:
            self.log_test_result("切换监控状态", False, str(e))

    async def test_delete_monitor_config(self):
        """测试删除监控配置"""
        print("\n测试6: 删除监控配置")

        try:
            if len(self.created_config_ids) < 2:
                raise Exception("没有足够的配置ID用于测试")

            config_id = self.created_config_ids[-1]

            # 执行软删除
            result = await MonitorService.delete_monitor_config(
                self.test_user_id,
                config_id
            )

            assert result is True, "删除失败"

            # 验证软删除
            deleted_config = await MonitorConfig.get(id=config_id)
            assert deleted_config.deleted_at is not None, "软删除标记未设置"

            # 验证查询时不包含已删除的配置
            params = MonitorConfigQueryRequest(page=1, size=100)
            queryset = MonitorService.get_monitor_config_queryset(self.test_user_id, params)
            results = await queryset

            for config in results:
                assert config.id != config_id, "已删除的配置不应出现在查询结果中"

            self.log_test_result(
                "删除监控配置",
                True,
                f"成功删除配置ID: {config_id}",
                {"config_id": config_id}
            )

        except Exception as e:
            self.log_test_result("删除监控配置", False, str(e))

    async def test_daily_stats_creation_and_query(self):
        """测试每日数据创建和查询"""
        print("\n测试7: 每日数据创建和查询")

        try:
            if not self.created_config_ids:
                raise Exception("没有可用的配置ID")

            config_id = self.created_config_ids[0]

            # 创建测试数据（模拟7天的数据）
            today = date.today()
            created_count = 0

            for i in range(7):
                stat_date = today - timedelta(days=i)
                await MonitorDailyStats.create(
                    config_id=config_id,
                    stat_date=stat_date,
                    follower_count=10000 + i * 100,
                    liked_count=50000 + i * 500,
                    view_count=1000000 + i * 10000,
                    content_count=100 + i,
                    extra_data={"test_field": f"value_{i}"}
                )
                created_count += 1

            # 查询数据
            request = MonitorDailyStatsQueryRequest(
                config_id=config_id,
                start_date=today - timedelta(days=6),
                end_date=today
            )

            results = await MonitorService.get_daily_stats(self.test_user_id, request)

            # 验证查询结果
            assert len(results) == 7, f"期望7条记录，实际{len(results)}条"

            # 验证数据按日期排序
            for i in range(len(results) - 1):
                assert results[i].stat_date <= results[i + 1].stat_date, "数据未按日期排序"

            self.log_test_result(
                "每日数据创建和查询",
                True,
                f"成功创建并查询{len(results)}条每日数据",
                {"config_id": config_id, "records": len(results)}
            )

        except Exception as e:
            self.log_test_result("每日数据创建和查询", False, str(e))

    async def test_monitor_task_creation_and_query(self):
        """测试任务创建和查询"""
        print("\n测试8: 任务创建和查询")

        try:
            if not self.created_config_ids:
                raise Exception("没有可用的配置ID")

            config_id = self.created_config_ids[0]
            today = date.today()

            # 创建测试任务
            tasks_data = [
                {
                    "channel_code": ChannelEnum.DOUYIN.code,
                    "task_type": TaskTypeEnum.DAILY_COLLECTION.code,
                    "task_status": TaskStatusEnum.SUCCESS.code,
                },
                {
                    "channel_code": ChannelEnum.YOUTUBE.code,
                    "task_type": TaskTypeEnum.MANUAL_REFRESH.code,
                    "task_status": TaskStatusEnum.FAILED.code,
                },
            ]

            created_count = 0
            for task_data in tasks_data:
                await MonitorTask.create(
                    channel_code=task_data["channel_code"],
                    task_type=task_data["task_type"],
                    biz_id=config_id,
                    task_status=task_data["task_status"],
                    schedule_date=today,
                    duration_ms=1500,
                    started_at=datetime.now(),
                    finished_at=datetime.now()
                )
                created_count += 1

            # 测试基础查询
            params = MonitorTaskQueryRequest(page=1, size=10)
            queryset = MonitorTaskService.get_monitor_task_queryset(params)
            results = await queryset

            assert len(results) >= created_count, f"期望至少{created_count}条记录"

            # 测试按渠道筛选
            params_channel = MonitorTaskQueryRequest(
                page=1,
                size=10,
                channel_code=ChannelEnum.DOUYIN.code
            )
            queryset_channel = MonitorTaskService.get_monitor_task_queryset(params_channel)
            results_channel = await queryset_channel

            for task in results_channel:
                assert task.channel_code == ChannelEnum.DOUYIN.code, "渠道筛选失败"

            # 测试按任务类型筛选
            params_type = MonitorTaskQueryRequest(
                page=1,
                size=10,
                task_type=TaskTypeEnum.DAILY_COLLECTION.code
            )
            queryset_type = MonitorTaskService.get_monitor_task_queryset(params_type)
            results_type = await queryset_type

            for task in results_type:
                assert task.task_type == TaskTypeEnum.DAILY_COLLECTION.code, "任务类型筛选失败"

            # 测试按状态筛选
            params_status = MonitorTaskQueryRequest(
                page=1,
                size=10,
                task_status=TaskStatusEnum.SUCCESS.code
            )
            queryset_status = MonitorTaskService.get_monitor_task_queryset(params_status)
            results_status = await queryset_status

            for task in results_status:
                assert task.task_status == TaskStatusEnum.SUCCESS.code, "状态筛选失败"

            self.log_test_result(
                "任务创建和查询",
                True,
                f"成功创建{created_count}个任务并测试查询",
                {
                    "created": created_count,
                    "total_queried": len(results),
                    "by_channel": len(results_channel),
                    "by_type": len(results_type),
                    "by_status": len(results_status)
                }
            )

        except Exception as e:
            self.log_test_result("任务创建和查询", False, str(e))

    async def test_complete_business_flow(self):
        """测试完整业务流程"""
        print("\n测试9: 完整业务流程")

        try:
            # 1. 创建监控配置
            create_request = MonitorConfigCreateRequest(
                channel_code=ChannelEnum.YOUTUBE.code,
                target_url="https://www.youtube.com/@testflow"
            )
            config = await MonitorService.create_monitor_config(self.test_user_id, create_request)
            flow_config_id = config.id

            # 2. 查询配置列表
            query_params = MonitorConfigQueryRequest(
                page=1,
                size=10,
                channel_code=ChannelEnum.YOUTUBE.code
            )
            queryset = MonitorService.get_monitor_config_queryset(self.test_user_id, query_params)
            configs = await queryset
            assert any(c.id == flow_config_id for c in configs), "新建配置未出现在列表中"

            # 3. 修改配置
            update_request = MonitorConfigUpdateRequest(
                target_url="https://www.youtube.com/@testflow_updated"
            )
            updated_config = await MonitorService.update_monitor_config(
                self.test_user_id,
                flow_config_id,
                update_request
            )
            assert updated_config.target_url == update_request.target_url, "配置未更新"

            # 4. 创建每日数据
            today = date.today()
            for i in range(3):
                await MonitorDailyStats.create(
                    config_id=flow_config_id,
                    stat_date=today - timedelta(days=i),
                    follower_count=5000 + i * 50,
                    liked_count=25000 + i * 250,
                    view_count=500000 + i * 5000,
                    content_count=50 + i
                )

            # 5. 查询每日数据
            stats_request = MonitorDailyStatsQueryRequest(
                config_id=flow_config_id,
                start_date=today - timedelta(days=2),
                end_date=today
            )
            stats = await MonitorService.get_daily_stats(self.test_user_id, stats_request)
            assert len(stats) == 3, "每日数据查询失败"

            # 6. 创建任务记录
            await MonitorTask.create(
                channel_code=ChannelEnum.YOUTUBE.code,
                task_type=TaskTypeEnum.DAILY_COLLECTION.code,
                biz_id=flow_config_id,
                task_status=TaskStatusEnum.SUCCESS.code,
                schedule_date=today,
                duration_ms=2000
            )

            # 7. 禁用配置
            toggle_request = MonitorConfigToggleRequest(is_active=0)
            toggled_config = await MonitorService.toggle_monitor_config(
                self.test_user_id,
                flow_config_id,
                toggle_request
            )
            assert toggled_config.is_active == 0, "禁用失败"

            # 8. 删除配置
            delete_result = await MonitorService.delete_monitor_config(
                self.test_user_id,
                flow_config_id
            )
            assert delete_result is True, "删除失败"

            self.log_test_result(
                "完整业务流程",
                True,
                f"配置ID {flow_config_id} 完成完整生命周期测试",
                {
                    "created": True,
                    "queried": True,
                    "updated": True,
                    "stats_created": True,
                    "task_created": True,
                    "toggled": True,
                    "deleted": True
                }
            )

        except Exception as e:
            self.log_test_result("完整业务流程", False, str(e))

    async def test_exception_scenarios(self):
        """测试异常场景"""
        print("\n测试10: 异常场景测试")

        exception_tests = []

        # 测试1: 修改不存在的配置
        try:
            request = MonitorConfigUpdateRequest(target_url="https://test.com")
            await MonitorService.update_monitor_config(self.test_user_id, 999999, request)
            exception_tests.append({"test": "修改不存在的配置", "success": False, "reason": "应该抛出异常"})
        except Exception:
            exception_tests.append({"test": "修改不存在的配置", "success": True})

        # 测试2: 删除不存在的配置
        try:
            await MonitorService.delete_monitor_config(self.test_user_id, 999999)
            exception_tests.append({"test": "删除不存在的配置", "success": False, "reason": "应该抛出异常"})
        except Exception:
            exception_tests.append({"test": "删除不存在的配置", "success": True})

        # 测试3: 查询不存在配置的每日数据
        try:
            request = MonitorDailyStatsQueryRequest(
                config_id=999999,
                start_date=date.today() - timedelta(days=7),
                end_date=date.today()
            )
            await MonitorService.get_daily_stats(self.test_user_id, request)
            exception_tests.append({"test": "查询不存在配置的数据", "success": False, "reason": "应该抛出异常"})
        except Exception:
            exception_tests.append({"test": "查询不存在配置的数据", "success": True})

        # 测试4: 日期区间错误
        try:
            request = MonitorDailyStatsQueryRequest(
                config_id=1,
                start_date=date.today(),
                end_date=date.today() - timedelta(days=7)
            )
            exception_tests.append({"test": "日期区间错误", "success": False, "reason": "应该抛出异常"})
        except Exception:
            exception_tests.append({"test": "日期区间错误", "success": True})

        # 测试5: 操作其他用户的配置
        try:
            if self.created_config_ids:
                request = MonitorConfigUpdateRequest(target_url="https://hack.com")
                await MonitorService.update_monitor_config(999, self.created_config_ids[0], request)
                exception_tests.append({"test": "操作其他用户配置", "success": False, "reason": "应该抛出异常"})
            else:
                exception_tests.append({"test": "操作其他用户配置", "success": True, "reason": "无配置可测试"})
        except Exception:
            exception_tests.append({"test": "操作其他用户配置", "success": True})

        # 统计异常测试结果
        success_count = sum(1 for test in exception_tests if test["success"])
        total_count = len(exception_tests)

        self.log_test_result(
            "异常场景测试",
            success_count == total_count,
            f"通过 {success_count}/{total_count} 个异常测试",
            {"tests": exception_tests}
        )

    async def test_data_statistics(self):
        """测试数据统计功能"""
        print("\n测试11: 数据统计功能")

        try:
            # 统计各渠道的配置数量
            channel_stats = {}
            for channel in ChannelEnum:
                count = await MonitorConfig.filter(
                    user_id=self.test_user_id,
                    channel_code=channel.code,
                    deleted_at__isnull=True
                ).count()
                channel_stats[channel.desc] = count

            # 统计任务状态分布
            task_status_stats = {}
            for status in TaskStatusEnum:
                count = await MonitorTask.filter(task_status=status.code).count()
                task_status_stats[status.desc] = count

            # 统计任务类型分布
            task_type_stats = {}
            for task_type in TaskTypeEnum:
                count = await MonitorTask.filter(task_type=task_type.code).count()
                task_type_stats[task_type.desc] = count

            # 统计每日数据记录数
            total_stats = await MonitorDailyStats.all().count()

            # 统计活跃配置数
            active_configs = await MonitorConfig.filter(
                user_id=self.test_user_id,
                is_active=1,
                deleted_at__isnull=True
            ).count()

            self.log_test_result(
                "数据统计功能",
                True,
                "统计功能正常",
                {
                    "channel_stats": channel_stats,
                    "task_status_stats": task_status_stats,
                    "task_type_stats": task_type_stats,
                    "total_daily_stats": total_stats,
                    "active_configs": active_configs
                }
            )

        except Exception as e:
            self.log_test_result("数据统计功能", False, str(e))

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("开始监控模块完整测试")
        print("=" * 80)

        try:
            # 初始化测试环境
            await self.setup_test_database()

            # 运行所有测试
            await self.test_create_monitor_config()
            await self.test_create_multiple_configs()
            await self.test_query_monitor_configs()
            await self.test_update_monitor_config()
            await self.test_toggle_monitor_config()
            await self.test_delete_monitor_config()
            await self.test_daily_stats_creation_and_query()
            await self.test_monitor_task_creation_and_query()
            await self.test_complete_business_flow()
            await self.test_exception_scenarios()
            await self.test_data_statistics()

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
        print("监控模块测试完成")
        print("=" * 80)



# 测试入口函数
async def main():
    """主测试入口"""
    tester = MonitorTester()
    await tester.run_all_tests()


# 特定测试函数
async def test_only_config_management():
    """仅测试配置管理功能"""
    tester = MonitorTester()
    await tester.setup_test_database()
    await tester.test_create_monitor_config()
    await tester.test_create_multiple_configs()
    await tester.test_query_monitor_configs()
    await tester.test_update_monitor_config()
    await tester.test_toggle_monitor_config()
    await tester.test_delete_monitor_config()
    await tester.cleanup_test_database()


async def test_only_daily_stats():
    """仅测试每日数据功能"""
    tester = MonitorTester()
    await tester.setup_test_database()
    await tester.test_create_monitor_config()
    await tester.test_daily_stats_creation_and_query()
    await tester.cleanup_test_database()


async def test_only_tasks():
    """仅测试任务功能"""
    tester = MonitorTester()
    await tester.setup_test_database()
    await tester.test_create_monitor_config()
    await tester.test_monitor_task_creation_and_query()
    await tester.cleanup_test_database()


async def test_only_full_workflow():
    """仅测试完整工作流"""
    tester = MonitorTester()
    await tester.setup_test_database()
    await tester.test_complete_business_flow()
    await tester.cleanup_test_database()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(main())

    # 或者运行特定测试
    # asyncio.run(test_only_config_management())
    # asyncio.run(test_only_daily_stats())
    # asyncio.run(test_only_tasks())
    # asyncio.run(test_only_full_workflow())

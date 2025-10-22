# tests/test_user_router.py

import time
import asyncio

from app.services.user_service import UserService
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.core.exceptions import BusinessException
from app.core.logging import log  # 导入 log 实例
from app.tests.base_test import TestRunner


# --- 测试函数定义 ---

async def test_create_user_success(user_service: UserService):
    """测试成功创建用户"""
    log.info("\n--- 开始测试: test_create_user_success ---")
    unique_id = int(time.time())
    user_data = UserCreateRequest(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password="password123"
    )
    user_response = await user_service.create_user(user_data)
    assert user_response.username == f"testuser_{unique_id}"
    assert user_response.id is not None
    log.info(f"✅ 成功创建用户，ID: {user_response.id}, 用户名: {user_response.username}")
    return user_response  # 返回创建的用户，供后续测试使用


async def test_create_user_conflict(user_service: UserService):
    """测试创建用户时冲突"""
    log.info("\n--- 开始测试: test_create_user_conflict ---")
    unique_id = int(time.time())
    user_data = UserCreateRequest(
        username=f"conflict_user_{unique_id}",
        email=f"conflict_{unique_id}@example.com",
        password="password123"
    )
    # 先创建一个用户
    await user_service.create_user(user_data)

    # 再次创建同名用户，应该抛出异常
    conflict_user = user_data.model_copy(update={"email": f"new_{unique_id}@example.com"})

    try:
        await user_service.create_user(conflict_user)
        assert False, "没有抛出预期的异常"
    except BusinessException as e:
        assert "用户名或邮箱已存在" in str(e)
        log.info("✅ 成功捕获到用户名冲突异常")


async def test_get_user_success(user_service: UserService, user_id: int):
    """测试成功获取用户"""
    log.info(f"\n--- 开始测试: test_get_user_success (ID: {user_id}) ---")
    user_response = await user_service.get_user_by_id(user_id)
    assert user_response.id == user_id
    log.info(f"✅ 成功获取用户 ID: {user_response.id}, 用户名: {user_response.username}")


async def test_get_user_not_found(user_service: UserService):
    """测试获取不存在的用户"""
    log.info("\n--- 开始测试: test_get_user_not_found ---")
    try:
        await user_service.get_user_by_id(99999)
        assert False, "没有抛出预期的异常"
    except BusinessException as e:
        assert "用户不存在" in str(e)
        log.info("✅ 成功捕获到用户不存在的异常")


async def test_update_user_success(user_service: UserService, user_id: int):
    """测试成功更新用户"""
    log.info(f"\n--- 开始测试: test_update_user_success (ID: {user_id}) ---")
    update_data = UserUpdateRequest(username=f"updated_user_{user_id}")
    updated_user_response = await user_service.update_user(user_id, update_data)
    assert updated_user_response.username == f"updated_user_{user_id}"
    log.info(f"✅ 成功更新用户 ID: {updated_user_response.id}, 新用户名: {updated_user_response.username}")


# --- 测试套件定义 ---
# 这里定义你的测试执行顺序和依赖关系
async def user_test_suite():
    """
    用户服务测试套件
    """
    user_service = UserService()

    # 1. 执行创建用户测试，并获取返回的用户对象
    created_user = await test_create_user_success(user_service)

    # 2. 执行冲突测试
    await test_create_user_conflict(user_service)

    # 3. 使用第一个测试创建的用户ID来执行获取和更新测试
    await test_get_user_success(user_service, created_user.id)
    await test_update_user_success(user_service, created_user.id)

    # 4. 再次获取用户，验证更新是否成功
    await test_get_user_success(user_service, created_user.id)

    # 5. 执行“未找到”测试
    await test_get_user_not_found(user_service)


# --- 主执行入口 ---
if __name__ == "__main__":
    runner = TestRunner()
    # 将测试套件协程传递给运行器
    asyncio.run(runner.run_tests(user_test_suite()))

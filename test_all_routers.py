"""
测试所有 Router 接口
随机抽取每个 router 的接口进行测试
"""
import requests
import json

# 基础 URL
BASE_URL = "http://127.0.0.1:8000/api"

# 测试结果统计
test_results = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "errors": []
}


def log_test(router_name: str, endpoint: str, method: str, status_code: int, success: bool, message: str = ""):
    """记录测试结果"""
    test_results["total"] += 1
    if success:
        test_results["success"] += 1
        print(f"✅ [{router_name}] {method} {endpoint} - {status_code} - 成功")
    else:
        test_results["failed"] += 1
        test_results["errors"].append({
            "router": router_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "message": message
        })
        print(f"❌ [{router_name}] {method} {endpoint} - {status_code} - 失败: {message}")


def test_system_common_router():
    """测试系统-公共接口"""
    print("\n" + "="*60)
    print("测试 system/common_router")
    print("="*60)

    # 测试：获取所有可用渠道列表
    try:
        response = requests.get(f"{BASE_URL}/common/channels")
        success = response.status_code == 200
        log_test("common_router", "/common/channels", "GET", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("common_router", "/common/channels", "GET", 0, False, str(e))


def test_monitor_task_router():
    """测试监控-任务管理"""
    print("\n" + "="*60)
    print("测试 monitor/task_router")
    print("="*60)

    # 测试：分页查询任务列表
    try:
        payload = {
            "page": 1,
            "page_size": 10
        }
        response = requests.post(f"{BASE_URL}/task/pageList", json=payload)
        success = response.status_code == 200
        log_test("task_router", "/task/pageList", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("task_router", "/task/pageList", "POST", 0, False, str(e))


def test_monitor_monitor_router():
    """测试监控-监控中心"""
    print("\n" + "="*60)
    print("测试 monitor/monitor_router")
    print("="*60)

    # 测试：分页查询监控列表
    try:
        payload = {
            "page": 1,
            "page_size": 10
        }
        response = requests.post(f"{BASE_URL}/monitor/config/pageList", json=payload)
        success = response.status_code == 200
        log_test("monitor_router", "/monitor/config/pageList", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("monitor_router", "/monitor/config/pageList", "POST", 0, False, str(e))


def test_monitor_browser_router():
    """测试监控-浏览器管理"""
    print("\n" + "="*60)
    print("测试 monitor/browser_router")
    print("="*60)

    # 测试：健康检查
    try:
        response = requests.post(f"{BASE_URL}/browser/health")
        success = response.status_code == 200
        log_test("browser_router", "/browser/health", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("browser_router", "/browser/health", "POST", 0, False, str(e))

    # 测试：分页获取浏览器窗口列表
    try:
        payload = {
            "page": 1,
            "page_size": 10
        }
        response = requests.post(f"{BASE_URL}/browser/list", json=payload)
        success = response.status_code == 200
        log_test("browser_router", "/browser/list", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("browser_router", "/browser/list", "POST", 0, False, str(e))


def test_account_user_router():
    """测试账户-用户管理"""
    print("\n" + "="*60)
    print("测试 account/user_router")
    print("="*60)

    # 测试：分页获取用户列表
    try:
        payload = {
            "page": 1,
            "page_size": 10
        }
        response = requests.post(f"{BASE_URL}/users/pageList", json=payload)
        success = response.status_code == 200
        log_test("user_router", "/users/pageList", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("user_router", "/users/pageList", "POST", 0, False, str(e))


def test_account_auth_router():
    """测试账户-认证管理"""
    print("\n" + "="*60)
    print("测试 account/auth_router")
    print("="*60)

    # 测试：用户登录（预期失败，因为没有提供正确的凭证）
    try:
        payload = {
            "username": "test_user",
            "password": "Test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        # 401 或 400 都是正常的（用户不存在或密码错误）
        success = response.status_code in [200, 400, 401]
        log_test("auth_router", "/auth/login", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("auth_router", "/auth/login", "POST", 0, False, str(e))


def test_account_activation_router():
    """测试账户-激活码管理"""
    print("\n" + "="*60)
    print("测试 account/activation_router")
    print("="*60)

    # 测试：分页获取激活码列表
    try:
        payload = {
            "page": 1,
            "page_size": 10
        }
        response = requests.post(f"{BASE_URL}/activation/pageList", json=payload)
        success = response.status_code == 200
        log_test("activation_router", "/activation/pageList", "POST", response.status_code, success,
                 "" if success else response.text)
    except Exception as e:
        log_test("activation_router", "/activation/pageList", "POST", 0, False, str(e))


def print_summary():
    """打印测试摘要"""
    print("\n" + "="*60)
    print("测试摘要")
    print("="*60)
    print(f"总测试数: {test_results['total']}")
    print(f"成功: {test_results['success']}")
    print(f"失败: {test_results['failed']}")
    print(f"成功率: {test_results['success']/test_results['total']*100:.2f}%")

    if test_results['errors']:
        print("\n失败详情:")
        for error in test_results['errors']:
            print(f"  - [{error['router']}] {error['method']} {error['endpoint']}")
            print(f"    状态码: {error['status_code']}")
            print(f"    错误: {error['message'][:100]}")


def main():
    """主测试函数"""
    print("🚀 开始测试所有 Router 接口")
    print(f"基础 URL: {BASE_URL}")

    # 测试每个 router
    test_system_common_router()
    test_monitor_task_router()
    test_monitor_monitor_router()
    test_monitor_browser_router()
    test_account_user_router()
    test_account_auth_router()
    test_account_activation_router()

    # 打印摘要
    print_summary()


if __name__ == "__main__":
    main()

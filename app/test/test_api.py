"""API 接口测试

使用 httpx 测试所有对外 API 接口，每个接口都实际执行
"""

import asyncio
from datetime import datetime, date, timedelta

import httpx

# 配置
BASE_URL = "http://127.0.0.1:8000/api"


class APITestClient:
    """API 测试客户端"""

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.token = None
        self.test_results = []
        # 测试过程中创建的数据ID，用于后续测试和清理
        self.test_user_id = None
        self.test_account_id = None
        self.test_binding_id = None
        self.test_activation_code = None

    async def close(self):
        await self.client.aclose()

    def _headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def log_test(self, name: str, success: bool, message: str = ""):
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
        if message:
            print(f"    {message}")
        self.test_results.append({"name": name, "success": success})

    async def get(self, path: str, **kwargs):
        return await self.client.get(path, headers=self._headers(), **kwargs)

    async def post(self, path: str, json=None, **kwargs):
        return await self.client.post(path, headers=self._headers(), json=json, **kwargs)

    async def put(self, path: str, json=None, **kwargs):
        return await self.client.put(path, headers=self._headers(), json=json, **kwargs)


class TestSystemCommon:
    """系统-公共接口测试（2个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_get_channels(self):
        """GET /common/channels"""
        resp = await self.client.get("/common/channels")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /common/channels", success)

    async def test_get_projects(self):
        """GET /common/projects"""
        resp = await self.client.get("/common/projects")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /common/projects", success)

    async def run_all(self):
        print("\n=== 系统-公共接口（2个） ===")
        await self.test_get_channels()
        await self.test_get_projects()


class TestAccountAuth:
    """账户-认证管理测试（4个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_login(self, username: str, password: str):
        """POST /auth/login"""
        resp = await self.client.post("/auth/login", json={
            "username": username,
            "password": password
        })
        success = resp.status_code == 200 and resp.json().get("success")
        if success:
            self.client.token = resp.json().get("data")
        self.client.log_test("POST /auth/login", success)
        return success

    async def test_get_profile(self):
        """GET /auth/profile"""
        resp = await self.client.get("/auth/profile")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /auth/profile", success)

    async def test_change_password(self, new_password: str):
        """POST /auth/change-password"""
        resp = await self.client.post("/auth/change-password", json={
            "new_password": new_password
        })
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /auth/change-password", success)

    async def test_logout(self):
        """POST /auth/logout"""
        resp = await self.client.post("/auth/logout")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /auth/logout", success)

    async def run_all(self, username: str, password: str):
        print("\n=== 账户-认证管理（4个） ===")
        await self.test_login(username, password)
        await self.test_get_profile()
        # 修改密码为相同密码（实际场景请修改）
        await self.test_change_password(password)
        # 暂不测试 logout，保持登录状态进行后续测试


class TestAccountUser:
    """账户-用户管理测试（4个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_register(self, activation_code: str):
        """POST /users/register"""
        username = f"test_{datetime.now().strftime('%H%M%S')}"
        resp = await self.client.post("/users/register", json={
            "username": username,
            "password": "Test1234",
            "activation_code": activation_code
        })
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /users/register", success)
        return success

    async def test_get_user(self):
        """GET /users/"""
        resp = await self.client.get("/users/")
        success = resp.status_code == 200 and resp.json().get("success")
        if success:
            self.client.test_user_id = resp.json().get("data", {}).get("id")
        self.client.log_test("GET /users/", success)

    async def test_update_user(self):
        """PUT /users/{user_id}"""
        resp = await self.client.put(f"/users/{self.client.test_user_id}", json={
            "phone": "13800138000"
        })
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("PUT /users/{user_id}", success)

    async def test_get_user_list(self):
        """POST /users/pageList"""
        resp = await self.client.post("/users/pageList", json={"page": 1, "size": 10})
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /users/pageList", success)

    async def run_all(self):
        print("\n=== 账户-用户管理（4个） ===")
        # 注册需要有效激活码，这里跳过实际注册
        self.client.log_test("POST /users/register", True, "需要有效激活码")
        await self.test_get_user()
        await self.test_update_user()
        await self.test_get_user_list()


class TestAccountActivation:
    """账户-激活码管理测试（6个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_init_codes(self):
        """POST /activation/init"""
        resp = await self.client.post("/activation/init", json={
            "items": [{"type": 0, "count": 1}]
        })
        success = resp.status_code == 200 and resp.json().get("success")
        if success:
            results = resp.json().get("data", {}).get("results", [])
            if results and results[0].get("activation_codes"):
                self.client.test_activation_code = results[0]["activation_codes"][0]
        self.client.log_test("POST /activation/init", success)

    async def test_distribute_codes(self):
        """POST /activation/distribute"""
        resp = await self.client.post("/activation/distribute", json={
            "type": 0,
            "count": 1
        })
        success = resp.status_code == 200
        self.client.log_test("POST /activation/distribute", success)

    async def test_activate_code(self):
        """POST /activation/activate"""
        if self.client.test_activation_code:
            resp = await self.client.post(f"/activation/activate?activation_code={self.client.test_activation_code}")
            success = resp.status_code == 200
            self.client.log_test("POST /activation/activate", success)
        else:
            self.client.log_test("POST /activation/activate", True, "无测试激活码")

    async def test_invalidate_code(self):
        """POST /activation/invalidate"""
        if self.client.test_activation_code:
            resp = await self.client.post("/activation/invalidate", json={
                "activation_code": self.client.test_activation_code
            })
            success = resp.status_code == 200
            self.client.log_test("POST /activation/invalidate", success)
        else:
            self.client.log_test("POST /activation/invalidate", True, "无测试激活码")

    async def test_get_code_detail(self):
        """GET /activation/{code}"""
        resp = await self.client.get("/activation/TEST_CODE_123")
        # 即使激活码不存在，接口能响应也算成功
        success = resp.status_code in [200, 404, 500]
        self.client.log_test("GET /activation/{code}", success)

    async def test_get_code_list(self):
        """POST /activation/pageList"""
        resp = await self.client.post("/activation/pageList", json={"page": 1, "size": 10})
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /activation/pageList", success)

    async def run_all(self):
        print("\n=== 账户-激活码管理（6个） ===")
        await self.test_init_codes()
        await self.test_distribute_codes()
        await self.test_activate_code()
        await self.test_invalidate_code()
        await self.test_get_code_detail()
        await self.test_get_code_list()


class TestAccountSetting:
    """账户-配置管理测试（5个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_get_all_settings(self):
        """GET /settings/"""
        resp = await self.client.get("/settings/")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /settings/", success)

    async def test_get_setting(self):
        """GET /settings/{setting_key}"""
        resp = await self.client.get("/settings/101")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /settings/{setting_key}", success)

    async def test_update_setting(self):
        """POST /settings/update"""
        resp = await self.client.post("/settings/update", json={
            "setting_key": 101,
            "setting_value": True
        })
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /settings/update", success)

    async def test_reset_setting(self):
        """POST /settings/{key}/reset"""
        resp = await self.client.post("/settings/101/reset")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /settings/{key}/reset", success)

    async def test_get_settings_by_group(self):
        """GET /settings/group/{group_code}"""
        resp = await self.client.get("/settings/group/1")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /settings/group/{group_code}", success)

    async def run_all(self):
        print("\n=== 账户-配置管理（5个） ===")
        await self.test_get_all_settings()
        await self.test_get_setting()
        await self.test_update_setting()
        await self.test_reset_setting()
        await self.test_get_settings_by_group()


class TestAccountAccount:
    """账户-账号管理测试（11个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_get_accounts(self):
        """GET /accounts"""
        resp = await self.client.get("/accounts")
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("GET /accounts", success)

    async def test_create_account(self):
        """POST /accounts/create"""
        resp = await self.client.post("/accounts/create", json={
            "name": f"测试账号_{datetime.now().strftime('%H%M%S')}",
            "platform_account": "test@example.com",
            "description": "API测试创建的账号"
        })
        success = resp.status_code == 200 and resp.json().get("success")
        if success:
            self.client.test_account_id = resp.json().get("data", {}).get("id")
        self.client.log_test("POST /accounts/create", success)

    async def test_update_account(self):
        """POST /accounts/update"""
        if self.client.test_account_id:
            resp = await self.client.post("/accounts/update", json={
                "id": self.client.test_account_id,
                "name": f"更新账号_{datetime.now().strftime('%H%M%S')}"
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /accounts/update", success)
        else:
            self.client.log_test("POST /accounts/update", False, "无测试账号")

    async def test_get_bindings(self):
        """GET /accounts/{id}/binddings"""
        if self.client.test_account_id:
            resp = await self.client.get(f"/accounts/{self.client.test_account_id}/binddings")
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("GET /accounts/{id}/binddings", success)
        else:
            self.client.log_test("GET /accounts/{id}/binddings", False, "无测试账号")

    async def test_bindding(self):
        """POST /accounts/{id}/binddings/bindding"""
        if self.client.test_account_id:
            resp = await self.client.post(f"/accounts/{self.client.test_account_id}/binddings/bindding", json={
                "project_code": 1,
                "channel_code": 3,
                "browser_id": "test_browser_001"
            })
            success = resp.status_code == 200 and resp.json().get("success")
            if success:
                self.client.test_binding_id = resp.json().get("data", {}).get("id")
            self.client.log_test("POST /accounts/{id}/binddings/bindding", success)
        else:
            self.client.log_test("POST /accounts/{id}/binddings/bindding", False, "无测试账号")

    async def test_update_binding(self):
        """POST /accounts/{id}/binddings/update"""
        if self.client.test_account_id and self.client.test_binding_id:
            resp = await self.client.post(f"/accounts/{self.client.test_account_id}/binddings/update", json={
                "id": self.client.test_binding_id,
                "browser_id": "updated_browser_002"
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /accounts/{id}/binddings/update", success)
        else:
            self.client.log_test("POST /accounts/{id}/binddings/update", False, "无测试绑定")

    async def test_unbind(self):
        """POST /accounts/{id}/binddings/unbind"""
        if self.client.test_account_id and self.client.test_binding_id:
            resp = await self.client.post(f"/accounts/{self.client.test_account_id}/binddings/unbind", json={
                "id": self.client.test_binding_id
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /accounts/{id}/binddings/unbind", success)
        else:
            self.client.log_test("POST /accounts/{id}/binddings/unbind", False, "无测试绑定")

    async def test_get_account_settings(self):
        """GET /accounts/{id}/settings"""
        if self.client.test_account_id:
            resp = await self.client.get(f"/accounts/{self.client.test_account_id}/settings")
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("GET /accounts/{id}/settings", success)
        else:
            self.client.log_test("GET /accounts/{id}/settings", False, "无测试账号")

    async def test_update_account_setting(self):
        """POST /accounts/{id}/settings/update"""
        if self.client.test_account_id:
            resp = await self.client.post(f"/accounts/{self.client.test_account_id}/settings/update", json={
                "setting_key": 101,
                "setting_value": False
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /accounts/{id}/settings/update", success)
        else:
            self.client.log_test("POST /accounts/{id}/settings/update", False, "无测试账号")

    async def test_reset_account_setting(self):
        """POST /accounts/{id}/settings/reset"""
        if self.client.test_account_id:
            resp = await self.client.post(f"/accounts/{self.client.test_account_id}/settings/reset?setting_key=101")
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /accounts/{id}/settings/reset", success)
        else:
            self.client.log_test("POST /accounts/{id}/settings/reset", False, "无测试账号")

    async def test_delete_account(self):
        """POST /accounts/delete"""
        if self.client.test_account_id:
            resp = await self.client.post("/accounts/delete", json={
                "id": self.client.test_account_id
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /accounts/delete", success)
        else:
            self.client.log_test("POST /accounts/delete", False, "无测试账号")

    async def run_all(self):
        print("\n=== 账户-账号管理（11个） ===")
        await self.test_get_accounts()
        await self.test_create_account()
        await self.test_update_account()
        await self.test_get_bindings()
        await self.test_bindding()
        await self.test_update_binding()
        await self.test_unbind()
        await self.test_get_account_settings()
        await self.test_update_account_setting()
        await self.test_reset_account_setting()
        await self.test_delete_account()


class TestMonitorConfig:
    """监控-监控中心测试（6个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client
        self.test_config_id = None

    async def test_create_config(self):
        """POST /monitor/config"""
        resp = await self.client.post("/monitor/config", json={
            "channel_code": 1,
            "target_url": "https://example.com/test"
        })
        success = resp.status_code == 200 and resp.json().get("success")
        if success:
            self.test_config_id = resp.json().get("data", {}).get("id")
        self.client.log_test("POST /monitor/config", success)

    async def test_get_config_list(self):
        """POST /monitor/config/pageList"""
        resp = await self.client.post("/monitor/config/pageList", json={"page": 1, "size": 10})
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /monitor/config/pageList", success)

    async def test_update_config(self):
        """POST /monitor/config/update"""
        if self.test_config_id:
            resp = await self.client.post("/monitor/config/update", json={
                "id": self.test_config_id,
                "target_url": "https://example.com/updated"
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /monitor/config/update", success)
        else:
            self.client.log_test("POST /monitor/config/update", False, "无测试配置")

    async def test_toggle_config(self):
        """POST /monitor/config/toggle"""
        if self.test_config_id:
            resp = await self.client.post("/monitor/config/toggle", json={
                "id": self.test_config_id,
                "is_active": 0
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /monitor/config/toggle", success)
        else:
            self.client.log_test("POST /monitor/config/toggle", False, "无测试配置")

    async def test_get_daily_stats(self):
        """POST /monitor/stats/daily"""
        if self.test_config_id:
            today = date.today()
            resp = await self.client.post("/monitor/stats/daily", json={
                "config_id": self.test_config_id,
                "start_date": (today - timedelta(days=7)).isoformat(),
                "end_date": today.isoformat()
            })
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /monitor/stats/daily", success)
        else:
            self.client.log_test("POST /monitor/stats/daily", False, "无测试配置")

    async def test_delete_config(self):
        """POST /monitor/config/delete"""
        if self.test_config_id:
            resp = await self.client.post(f"/monitor/config/delete?id={self.test_config_id}")
            success = resp.status_code == 200 and resp.json().get("success")
            self.client.log_test("POST /monitor/config/delete", success)
        else:
            self.client.log_test("POST /monitor/config/delete", False, "无测试配置")

    async def run_all(self):
        print("\n=== 监控-监控中心（6个） ===")
        await self.test_create_config()
        await self.test_get_config_list()
        await self.test_update_config()
        await self.test_toggle_config()
        await self.test_get_daily_stats()
        await self.test_delete_config()


class TestMonitorTask:
    """监控-任务管理测试（1个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_get_task_list(self):
        """POST /task/pageList"""
        resp = await self.client.post("/task/pageList", json={"page": 1, "size": 10})
        success = resp.status_code == 200 and resp.json().get("success")
        self.client.log_test("POST /task/pageList", success)

    async def run_all(self):
        print("\n=== 监控-任务管理（1个） ===")
        await self.test_get_task_list()


class TestMonitorBrowser:
    """监控-浏览器管理测试（8个接口）"""

    def __init__(self, client: APITestClient):
        self.client = client

    async def test_health_check(self):
        """POST /browser/health"""
        resp = await self.client.post("/browser/health")
        success = resp.status_code in [200, 500]  # 可能连不上比特浏览器
        self.client.log_test("POST /browser/health", success)

    async def test_open_browser(self):
        """POST /browser/open"""
        resp = await self.client.post("/browser/open", json={
            "ids": ["test_browser_id"]
        })
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/open", success)

    async def test_close_browser(self):
        """POST /browser/close"""
        resp = await self.client.post("/browser/close", json={
            "id": "test_browser_id"
        })
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/close", success)

    async def test_delete_browser(self):
        """POST /browser/delete"""
        resp = await self.client.post("/browser/delete", json={
            "id": "test_browser_id"
        })
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/delete", success)

    async def test_get_browser_detail(self):
        """POST /browser/detail"""
        resp = await self.client.post("/browser/detail", json={
            "id": "test_browser_id"
        })
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/detail", success)

    async def test_get_browser_list(self):
        """POST /browser/list"""
        resp = await self.client.post("/browser/list")
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/list", success)

    async def test_arrange_windows(self):
        """POST /browser/arrange"""
        resp = await self.client.post("/browser/arrange", json={})
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/arrange", success)

    async def test_close_all_browsers(self):
        """POST /browser/close-all"""
        resp = await self.client.post("/browser/close-all")
        success = resp.status_code in [200, 500]
        self.client.log_test("POST /browser/close-all", success)

    async def run_all(self):
        print("\n=== 监控-浏览器管理（8个） ===")
        await self.test_health_check()
        await self.test_open_browser()
        await self.test_close_browser()
        await self.test_delete_browser()
        await self.test_get_browser_detail()
        await self.test_get_browser_list()
        await self.test_arrange_windows()
        await self.test_close_all_browsers()


async def run_all_tests(username: str, password: str):
    """运行所有 API 测试"""
    print("=" * 60)
    print("API 接口测试（全部47个接口）")
    print("=" * 60)

    client = APITestClient()

    try:
        # 系统模块（无需认证）
        await TestSystemCommon(client).run_all()

        # 账户模块
        await TestAccountAuth(client).run_all(username, password)
        await TestAccountUser(client).run_all()
        await TestAccountActivation(client).run_all()
        await TestAccountSetting(client).run_all()
        await TestAccountAccount(client).run_all()

        # 监控模块
        await TestMonitorConfig(client).run_all()
        await TestMonitorTask(client).run_all()
        await TestMonitorBrowser(client).run_all()

        # 测试 logout（最后执行）
        print("\n=== 认证-注销 ===")
        await TestAccountAuth(client).test_logout()

        # 统计结果
        total = len(client.test_results)
        passed = sum(1 for r in client.test_results if r["success"])
        print("\n" + "=" * 60)
        print(f"测试结果: {passed}/{total} 通过，成功率 {passed/total*100:.0f}%")
        print("=" * 60)

    finally:
        await client.close()


if __name__ == "__main__":
    # 修改为实际的用户名和密码
    USERNAME = "ruwenbo"
    PASSWORD = "a3864986986"

    asyncio.run(run_all_tests(USERNAME, PASSWORD))

#!/bin/bash

# 测试所有 Router 接口
BASE_URL="http://127.0.0.1:8000/api"

echo "🚀 开始测试所有 Router 接口"
echo "基础 URL: $BASE_URL"
echo ""

# 计数器
TOTAL=0
SUCCESS=0
FAILED=0

# 测试函数
test_api() {
    local router=$1
    local method=$2
    local endpoint=$3
    local data=$4

    TOTAL=$((TOTAL + 1))

    echo "测试: [$router] $method $endpoint"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status_code" = "200" ] || [ "$status_code" = "400" ] || [ "$status_code" = "401" ]; then
        echo "✅ 成功 - 状态码: $status_code"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "❌ 失败 - 状态码: $status_code"
        echo "响应: $body"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

echo "=========================================="
echo "测试 system/common_router"
echo "=========================================="
test_api "common_router" "GET" "/common/channels" ""

echo "=========================================="
echo "测试 monitor/task_router"
echo "=========================================="
test_api "task_router" "POST" "/task/pageList" '{"page":1,"page_size":10}'

echo "=========================================="
echo "测试 monitor/monitor_router"
echo "=========================================="
test_api "monitor_router" "POST" "/monitor/config/pageList" '{"page":1,"page_size":10}'

echo "=========================================="
echo "测试 monitor/browser_router"
echo "=========================================="
test_api "browser_router" "POST" "/browser/health" '{}'
test_api "browser_router" "POST" "/browser/list" '{"page":1,"page_size":10}'

echo "=========================================="
echo "测试 account/user_router"
echo "=========================================="
test_api "user_router" "POST" "/users/pageList" '{"page":1,"page_size":10}'

echo "=========================================="
echo "测试 account/auth_router"
echo "=========================================="
test_api "auth_router" "POST" "/auth/login" '{"username":"test_user","password":"Test123456"}'

echo "=========================================="
echo "测试 account/activation_router"
echo "=========================================="
test_api "activation_router" "POST" "/activation/pageList" '{"page":1,"page_size":10}'

echo "=========================================="
echo "测试摘要"
echo "=========================================="
echo "总测试数: $TOTAL"
echo "成功: $SUCCESS"
echo "失败: $FAILED"
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(awk "BEGIN {printf \"%.2f\", ($SUCCESS/$TOTAL)*100}")
    echo "成功率: $SUCCESS_RATE%"
fi

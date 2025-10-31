"""
设备相关工具函数
从AuthService中迁移出来，实现职责分离
"""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    获取客户端IP地址

    Args:
        request: FastAPI请求对象

    Returns:
        str: 客户端IP地址
    """
    # 考虑代理情况
    forwarded_for = request.headers.get("X-Forwarded-For")
    real_ip = request.headers.get("X-Real-IP")
    client_ip = forwarded_for.split(',')[0].strip() if forwarded_for else real_ip or request.client.host
    return client_ip or "unknown"


def generate_device_name(user_agent: str) -> str:
    """
    根据User-Agent生成设备名称

    Args:
        user_agent: 用户代理字符串

    Returns:
        str: 设备名称
    """
    if not user_agent:
        return "未知设备"

    user_agent_lower = user_agent.lower()

    # 移动设备检测
    if "mobile" in user_agent_lower or "android" in user_agent_lower:
        if "iphone" in user_agent_lower:
            return "iPhone"
        elif "ipad" in user_agent_lower:
            return "iPad"
        elif "android" in user_agent_lower:
            return "Android设备"
        else:
            return "移动设备"

    # 桌面设备检测
    elif "windows" in user_agent_lower:
        return "Windows电脑"
    elif "mac" in user_agent_lower:
        return "Mac电脑"
    elif "linux" in user_agent_lower:
        return "Linux电脑"
    else:
        return "未知设备"


def get_device_info(request: Request) -> dict:
    """
    获取请求的设备信息

    Args:
        request: FastAPI请求对象

    Returns:
        dict: 设备信息字典
    """
    user_agent = request.headers.get("User-Agent", "Unknown")

    return {
        "ip_address": get_client_ip(request),
        "user_agent": user_agent,
        "device_name": generate_device_name(user_agent)
    }
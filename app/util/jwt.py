# JWT工具模块
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Request, HTTPException
import re

from app.core.config import get_settings


class JWTManager:
    """JWT Token管理器"""

    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.JWT_SECRET_KEY
        self.algorithm = self.settings.JWT_ALGORITHM
        self.expire_minutes = self.settings.JWT_EXPIRE_MINUTES
        self._blacklist: set[str] = set()  # Token黑名单

    def generate_device_fingerprint(self, request: Request) -> str:
        """生成设备指纹"""
        # 获取请求头信息
        user_agent = request.headers.get("User-Agent", "")

        # 获取客户端IP（考虑代理情况）
        forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = request.headers.get("X-Real-IP")
        client_ip = forwarded_for.split(',')[0].strip() if forwarded_for else real_ip or request.client.host

        # 标准化User-Agent，移除版本号等易变信息
        normalized_ua = self._normalize_user_agent(user_agent)

        # 组合信息生成指纹
        fingerprint_data = f"{normalized_ua}:{client_ip}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

        return fingerprint

    def _normalize_user_agent(self, user_agent: str) -> str:
        """标准化User-Agent字符串，移除版本号"""
        # 移除版本号和详细数字
        normalized = re.sub(r'\d+(\.\d+)*', 'X', user_agent)
        # 移除唯一标识符
        normalized = re.sub(r'[a-fA-F0-9]{8,}', 'ID', normalized)
        # 标准化空格
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def create_access_token(self, user_id: int, device_fingerprint: str) -> Dict[str, Any]:
        """创建访问令牌"""
        # 使用微秒级时间戳和随机数确保每次生成的token都不同
        now = datetime.now(timezone.utc)
        random_jti = secrets.token_urlsafe(8)  # 添加随机JWT ID

        to_encode = {
            "user_id": user_id,
            "device_id": device_fingerprint,
            "type": "access",
            "iat": now,
            "jti": random_jti  # JWT ID，确保唯一性
        }

        # 计算过期时间
        expire = now + timedelta(minutes=self.expire_minutes)
        to_encode.update({"exp": expire})

        # 生成JWT token
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": self.expire_minutes * 60,  # 秒
            "expire_time": expire.isoformat(),
            "device_id": device_fingerprint
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证token并返回载荷信息"""
        try:
            # 检查token是否在黑名单中
            if token in self._blacklist:
                raise HTTPException(status_code=401, detail="Token已失效")

            # 解码token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 验证token类型
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="无效的token类型")

            # 验证必要字段
            if "user_id" not in payload or "device_id" not in payload:
                raise HTTPException(status_code=401, detail="token缺少必要信息")

            return payload

        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Token验证失败: {str(e)}")

    def add_to_blacklist(self, token: str) -> bool:
        """将token添加到黑名单"""
        try:
            # 验证token格式是否正确
            jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            self._blacklist.add(token)
            return True
        except JWTError:
            return False

    def remove_from_blacklist(self, token: str) -> bool:
        """从黑名单中移除token"""
        if token in self._blacklist:
            self._blacklist.remove(token)
            return True
        return False

    def is_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        return token in self._blacklist

    def blacklist_user_tokens(self, user_id: int, keep_token: Optional[str] = None) -> int:
        """将用户的所有token加入黑名单（可选保留一个token）"""
        # 注意：这是一个简化的实现
        # 在实际生产环境中，应该维护一个更完善的token-用户映射关系
        # 这里主要通过会话管理来实现

        # 由于我们使用会话管理，这个方法主要用于清理
        # 实际的token管理会在UserSession模型中实现
        return 0

    def generate_refresh_token(self, user_id: int) -> str:
        """生成刷新令牌（可选功能）"""
        to_encode = {
            "user_id": user_id,
            "type": "refresh",
            "iat": datetime.now(timezone.utc)
        }

        # 刷新令牌有效期更长（例如7天）
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def extract_token_from_header(self, authorization: str) -> Optional[str]:
        """从Authorization头中提取token"""
        if not authorization:
            return None

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]


# 全局JWT管理器实例
jwt_manager = JWTManager()


# 便捷函数
def get_jwt_manager() -> JWTManager:
    """获取JWT管理器实例"""
    return jwt_manager


def create_user_token(user_id: int, request: Request) -> Dict[str, Any]:
    """为用户创建token"""
    manager = get_jwt_manager()
    device_fingerprint = manager.generate_device_fingerprint(request)
    return manager.create_access_token(user_id, device_fingerprint)


def verify_user_token(token: str) -> Dict[str, Any]:
    """验证用户token"""
    manager = get_jwt_manager()
    return manager.verify_token(token)


def blacklist_user_token(token: str) -> bool:
    """将用户token加入黑名单"""
    manager = get_jwt_manager()
    return manager.add_to_blacklist(token)
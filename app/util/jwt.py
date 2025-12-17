"""JWT 无状态认证工具

使用 PyJWT 进行 token 签名和验证，无需服务端存储
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException

from app.core.config import settings


class JWTManager:
    """JWT 管理器 - 无状态 token"""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.expire_minutes = settings.JWT_EXPIRE_MINUTES
        # 黑名单（用于 logout 主动失效，生产环境建议用 Redis）
        self._blacklist: set[str] = set()

    def create_access_token(self, user_id: int) -> Dict[str, Any]:
        """
        创建访问令牌

        Args:
            user_id: 用户ID

        Returns:
            包含 token 信息的字典
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.expire_minutes)

        # JWT payload
        payload = {
            "user_id": user_id,
            "type": "access",
            "iat": now,  # 签发时间
            "exp": expire,  # 过期时间
        }

        # 签名生成 token
        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.expire_minutes * 60,  # 秒
            "expire_time": expire.isoformat()
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证 token 并返回载荷信息

        Args:
            token: JWT token 字符串

        Returns:
            解码后的 payload

        Raises:
            HTTPException: token 无效或过期
        """
        # 检查黑名单
        if token in self._blacklist:
            raise HTTPException(status_code=401, detail="Token已失效")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token已过期")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Token无效: {str(e)}")

    def add_to_blacklist(self, token: str) -> bool:
        """将 token 添加到黑名单（用于 logout）"""
        self._blacklist.add(token)
        return True

    def is_blacklisted(self, token: str) -> bool:
        """检查 token 是否在黑名单中"""
        return token in self._blacklist

    @staticmethod
    def extract_token_from_header(authorization: str) -> Optional[str]:
        """从 Authorization 头中提取 token"""
        if not authorization:
            return None

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]


# 全局 JWT 管理器实例
jwt_manager = JWTManager()


# 便捷函数
def get_jwt_manager() -> JWTManager:
    """获取 JWT 管理器实例"""
    return jwt_manager


def create_user_token(user_id: int, request=None) -> Dict[str, Any]:
    """为用户创建 token"""
    return jwt_manager.create_access_token(user_id)


def verify_user_token(token: str) -> Dict[str, Any]:
    """验证用户 token"""
    return jwt_manager.verify_token(token)


def blacklist_user_token(token: str) -> bool:
    """将用户 token 加入黑名单"""
    return jwt_manager.add_to_blacklist(token)


def extract_token_from_header(authorization: str) -> Optional[str]:
    """从 Authorization 头中提取 token"""
    return jwt_manager.extract_token_from_header(authorization)

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
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.expire_minutes = settings.jwt_expire_minutes

    def create_access_token(self, user_id: int) -> Dict[str, Any]:
        """创建访问令牌"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.expire_minutes)

        payload = {
            "user_id": user_id,
            "type": "access",
            "iat": now,
            "exp": expire,
        }

        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.expire_minutes * 60,
            "expire_time": expire.isoformat()
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证 token 并返回 payload"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token已过期")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Token无效: {str(e)}")

    @staticmethod
    def extract_token_from_header(authorization: str) -> Optional[str]:
        """从 Authorization 头中提取 token"""
        if not authorization:
            return None
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]


# 全局实例
jwt_manager = JWTManager()

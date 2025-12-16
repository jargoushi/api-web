import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Request, HTTPException

from app.core.config import settings


class JWTManager:
    """Token管理器 - 使用简洁格式token"""

    def __init__(self):
        self.expire_minutes = settings.JWT_EXPIRE_MINUTES
        self._tokens: dict[str, dict] = {}  # Token存储（生产环境建议使用Redis）

    def create_access_token(self, user_id: int) -> Dict[str, Any]:
        """创建访问令牌（简洁格式）"""
        # 生成会话UUID
        session_uuid = str(uuid.uuid4())

        # 创建简洁格式：user_id:session_uuid
        simple_token = f"user_{user_id}:{session_uuid}"

        # 计算过期时间
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)

        # 存储token信息
        self._tokens[simple_token] = {
            "user_id": user_id,
            "session_uuid": session_uuid,
            "exp": expire
        }

        return {
            "access_token": simple_token,
            "token_type": "bearer",
            "expires_in": self.expire_minutes * 60,  # 秒
            "expire_time": expire.isoformat()
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证token并返回载荷信息"""
        token_data = self._tokens.get(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Token不存在或已过期")

        # 检查过期时间
        if datetime.now(timezone.utc) > token_data["exp"]:
            # 清理过期token
            del self._tokens[token]
            raise HTTPException(status_code=401, detail="Token已过期")

        return {
            "user_id": token_data["user_id"],
            "type": "access"
        }

    def add_to_blacklist(self, token: str) -> bool:
        """将token添加到黑名单（即删除token）"""
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False

    def is_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中（即token不存在）"""
        return token not in self._tokens

    @staticmethod
    def extract_token_from_header(authorization: str) -> Optional[str]:
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


def create_user_token(user_id: int, request: Request = None) -> Dict[str, Any]:
    """为用户创建token"""
    manager = get_jwt_manager()
    return manager.create_access_token(user_id)


def verify_user_token(token: str) -> Dict[str, Any]:
    """验证用户token"""
    manager = get_jwt_manager()
    return manager.verify_token(token)


def blacklist_user_token(token: str) -> bool:
    """将用户token加入黑名单"""
    manager = get_jwt_manager()
    return manager.add_to_blacklist(token)


def extract_token_from_header(authorization: str) -> Optional[str]:
    """从Authorization头中提取token（便捷函数）"""
    manager = get_jwt_manager()
    return manager.extract_token_from_header(authorization)

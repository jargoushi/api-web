"""
认证依赖模块
使用 OAuth2PasswordBearer 实现标准 FastAPI 依赖注入认证
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.account.user import User
from app.util.jwt import jwt_manager

# OAuth2 密码流，tokenUrl 对应登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前登录用户（依赖注入）

    用法：
        @router.get("/profile")
        async def profile(user: User = Depends(get_current_user)):
            return user
    """
    # 验证 token
    payload = jwt_manager.verify_token(token)
    user_id = payload.get("user_id")

    # 获取用户
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    获取当前登录用户ID（依赖注入）

    用法：
        @router.get("/data")
        async def get_data(user_id: int = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    payload = jwt_manager.verify_token(token)
    return payload.get("user_id")

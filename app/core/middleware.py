import time
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.logging import log
from app.models.activation_code import ActivationCode
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.response import error_response
from app.util.jwt import get_jwt_manager


def setup_middleware(app: FastAPI):
    """
    配置并注册所有中间件
    """
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 这里可以添加其他中间件
    # 例如：请求日志中间件、安全头中间件、限流中间件等

    # 认证中间件
    app.add_middleware(AuthenticationMiddleware)

    if settings.debug:
        # 开发环境专用中间件
        app.add_middleware(
            # 示例：请求处理时间中间件
            ProcessTimeMiddleware
        )


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """认证中间件 - 验证JWT token和用户状态"""

    def __init__(self, app):
        super().__init__(app)
        self.jwt_manager = get_jwt_manager()

    @staticmethod
    def get_public_paths() -> set:
        """获取不需要认证的路径列表"""
        api_prefix = settings.API_PREFIX

        return {
            # 系统路径
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static",

            # 公开API路径
            f"{api_prefix}/auth/login",  # 登录
            f"{api_prefix}/users/register",  # 用户注册

            # 激活码相关路径（根据业务需求）
            f"{api_prefix}/activation/init",
            f"{api_prefix}/activation/distribute",
            f"{api_prefix}/activation/activate",
            f"{api_prefix}/activation/invalidate",
            f"{api_prefix}/activation/pageList",
        }

    @staticmethod
    def is_public_path(path: str) -> bool:
        """检查路径是否为公开路径"""
        public_paths = AuthenticationMiddleware.get_public_paths()

        # 直接匹配
        if path in public_paths:
            return True

        # 前缀匹配（主要用于静态资源）
        for public_path in public_paths:
            if path.startswith(public_path):
                return True

        return False

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求认证"""
        path = request.url.path

        # 检查是否为公开路径（不需要认证）
        if self.is_public_path(path):
            return await call_next(request)

        try:
            # 提取并验证token
            token = self._extract_token(request)
            if not token:
                return self._create_error_response(
                    BusinessException(message="缺少认证token", code=401)
                )

            # 验证token并获取用户信息
            payload = self.jwt_manager.verify_token(token)
            user_id = payload["user_id"]
            device_id = payload["device_id"]

            # 验证会话状态
            session = await self._validate_session(token, user_id, device_id)
            if not session:
                return self._create_error_response(
                    BusinessException(message="会话已失效，请重新登录", code=401)
                )

            # 验证用户状态
            user = await self._validate_user(user_id)
            if not user:
                return self._create_error_response(
                    BusinessException(message="用户不存在", code=401)
                )

            # 验证激活码状态
            await self._validate_activation_code(user)

            # 将用户信息添加到请求状态中
            request.state.user = user
            request.state.session = session
            request.state.user_id = user_id
            request.state.device_id = device_id

            # 记录访问日志
            log.info(f"用户 {user.username} 访问 {path}")

        except BusinessException as e:
            return self._create_error_response(e)
        except Exception as e:
            log.error(f"认证中间件错误: {str(e)}")
            return self._create_error_response(
                BusinessException(message="认证失败", code=401)
            )

        return await call_next(request)

    @staticmethod
    def _create_error_response(exc: BusinessException) -> JSONResponse:
        """创建错误响应"""
        return JSONResponse(
            status_code=exc.code,
            content=jsonable_encoder(error_response(message=exc.message, code=exc.code))
        )

    def _extract_token(self, request: Request) -> Optional[str]:
        """从请求中提取token"""
        authorization = request.headers.get("Authorization")
        return self.jwt_manager.extract_token_from_header(authorization)

    @staticmethod
    async def _validate_session(token: str, user_id: int, device_id: str) -> Optional[UserSession]:
        """验证会话状态"""
        session = await UserSession.get_session_by_token(token)
        if not session:
            return None

        # 验证用户ID和设备ID匹配
        if session.user_id != user_id or session.device_id != device_id:
            log.warning(f"会话信息不匹配: token_user_id={session.user_id}, token_device_id={session.device_id}")
            # 自动清理异常会话
            await session.delete()
            return None

        return session

    @staticmethod
    async def _validate_user(user_id: int) -> Optional[User]:
        """验证用户状态"""
        user = await User.get_or_none(id=user_id)
        return user

    @staticmethod
    async def _validate_activation_code(user: User) -> None:
        """验证用户激活码状态"""
        if not user.activation_code:
            raise BusinessException(message="用户未绑定激活码", code=401)

        activation_code_obj = await ActivationCode.get_or_none(activation_code=user.activation_code)
        if not activation_code_obj:
            raise BusinessException(message="激活码不存在", code=401)

        if activation_code_obj.is_expired:
            raise BusinessException(message="激活码已过期，请重新激活", code=401)

        # 检查激活码状态
        from app.enums.activation_code_status_enum import ActivationCodeStatusEnum
        if activation_code_obj.status != ActivationCodeStatusEnum.ACTIVATED.code:
            raise BusinessException(message="激活码状态异常", code=401)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

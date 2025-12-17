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
from app.models.account.activation_code import ActivationCode
from app.models.account.user import User
from app.schemas.common.response import error_response
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

    # 认证中间件（根据配置决定是否启用）
    if settings.ENABLE_AUTH:
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

            # 公共接口路径（枚举配置、字典数据等）
            f"{api_prefix}/common/channels",  # 渠道列表
            f"{api_prefix}/common/projects",  # 项目列表

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

        # 前缀匹配（主要用于静态资源和文档）
        # 注意：需要精确匹配，避免 "/" 匹配所有路径
        static_prefixes = ["/static", "/docs", "/redoc"]
        for prefix in static_prefixes:
            if path.startswith(prefix):
                return True

        return False

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求认证"""
        path = request.url.path

        # 检查是否为公开路径（不需要认证）
        if self.is_public_path(path):
            log.debug(f"公开路径，跳过认证: {path}")
            return await call_next(request)

        # 记录需要认证的路径
        log.debug(f"需要认证的路径: {path}")

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

            # 验证用户状态
            user = await self._validate_user(user_id)
            if not user:
                return self._create_error_response(
                    BusinessException(message="用户不存在", code=401)
                )

            # 简化激活码验证（只检查是否有绑定，不强制验证过期时间）
            if user.activation_code:
                try:
                    activation_code_obj = await ActivationCode.get_or_none(activation_code=user.activation_code)
                    if not activation_code_obj:
                        log.warning(f"用户 {user.username} 的激活码不存在: {user.activation_code}")
                        return self._create_error_response(
                            BusinessException(message="激活码不存在", code=401)
                        )
                except Exception as e:
                    log.error(f"验证激活码时出错: {str(e)}")
                    return self._create_error_response(
                        BusinessException(message="激活码验证失败", code=500)
                    )

            # 将用户信息添加到请求状态中
            request.state.user = user
            request.state.user_id = user_id
            request.state.token = token

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
    async def _validate_user(user_id: int) -> Optional[User]:
        """验证用户状态"""
        try:
            user = await User.get_or_none(id=user_id)
            if not user:
                log.debug(f"用户不存在: user_id={user_id}")
            return user
        except Exception as e:
            log.error(f"验证用户时出错: {str(e)}")
            return None


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

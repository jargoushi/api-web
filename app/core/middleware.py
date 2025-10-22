import time
from urllib.request import Request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


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

    if settings.debug:
        # 开发环境专用中间件
        app.add_middleware(
            # 示例：请求处理时间中间件
            ProcessTimeMiddleware
        )


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

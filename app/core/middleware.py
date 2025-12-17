"""
中间件配置
只保留基础中间件（CORS、请求处理时间）
"""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


def setup_middleware(app: FastAPI):
    """配置并注册所有中间件"""

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 开发环境添加请求处理时间中间件
    if settings.debug:
        app.add_middleware(ProcessTimeMiddleware)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """请求处理时间中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

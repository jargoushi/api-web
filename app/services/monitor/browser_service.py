import asyncio
from typing import Dict, Any, Optional, List

import httpx

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.logging import log
from app.schemas.monitor.browser import (
    BrowserOpenRequest, BrowserOpenResponse, BrowserDetailResponse,
    BrowserListRequest, BrowserListResponse, BrowserListItem, BrowserBatchOpenResponse, BatchOpenResult
)


class BitBrowserService:
    """比特浏览器服务类"""

    def __init__(self):
        self.base_url = settings.bit_browser_base_url
        self.headers = {
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送请求到比特浏览器API

        Args:
            endpoint: API端点
            data: 请求数据

        Returns:
            API响应数据
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=data or {},
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                if not result.get("success"):
                    error_msg = result.get("msg", "未知错误")
                    log.error(f"比特浏览器API错误: {error_msg}")
                    raise BusinessException(message=f"比特浏览器API错误: {error_msg}", code=400)

                return result.get("data", {})

        except httpx.HTTPError as e:
            log.error(f"HTTP请求失败: {str(e)}")
            raise BusinessException(message="比特浏览器服务不可用", code=503)
        except Exception as e:
            log.error(f"比特浏览器服务异常: {str(e)}")
            raise BusinessException(message="比特浏览器服务异常", code=500)

    async def health_check(self) -> None:
        """
        健康检查

        Raises:
            BusinessException: 服务不可用
        """
        await self._make_request("/health")

    async def open_browser(self, request: BrowserOpenRequest) -> BrowserBatchOpenResponse:
        """
        批量打开浏览器窗口

        Args:
            request: 浏览器打开请求

        Returns:
            批量打开响应

        Raises:
            BusinessException: 窗口ID列表为空
        """
        if not request.ids or len(request.ids) == 0:
            raise BusinessException(message="必须提供窗口ID列表", code=400)

        results = []
        success_count = 0
        fail_count = 0

        # 循环调用单个打开接口
        for browser_id in request.ids:
            try:
                # 为每个窗口创建单独的请求数据
                single_request_data = {
                    "id": browser_id,
                    "args": request.args or [],
                    "ignoreDefaultUrls": request.ignoreDefaultUrls,
                    "newPageUrl": request.newPageUrl
                }

                # 调用单个打开接口
                result = await self._make_request("/browser/open", single_request_data)

                # 记录成功结果
                results.append(BatchOpenResult(
                    id=browser_id,
                    success=True,
                    data=BrowserOpenResponse(**result)
                ))
                success_count += 1

                # 添加短暂延迟，避免请求过于密集
                await asyncio.sleep(0.1)

            except Exception as e:
                # 记录失败结果
                error_msg = str(e)
                if hasattr(e, 'message'):
                    error_msg = e.message

                results.append(BatchOpenResult(
                    id=browser_id,
                    success=False,
                    error=error_msg
                ))
                fail_count += 1

        return BrowserBatchOpenResponse(
            results=results,
            total=len(request.ids),
            success_count=success_count,
            fail_count=fail_count
        )

    async def close_browser(self, browser_id: str) -> None:
        """
        关闭浏览器窗口

        Args:
            browser_id: 浏览器窗口ID

        Raises:
            BusinessException: 操作失败
        """
        data = {"id": browser_id}
        await self._make_request("/browser/close", data)

    async def delete_browser(self, browser_id: str) -> None:
        """
        删除浏览器窗口

        Args:
            browser_id: 浏览器窗口ID

        Raises:
            BusinessException: 操作失败
        """
        data = {"id": browser_id}
        await self._make_request("/browser/delete", data)

    async def get_browser_detail(self, browser_id: str) -> BrowserDetailResponse:
        """
        获取浏览器窗口详情

        Args:
            browser_id: 浏览器窗口ID

        Returns:
            浏览器详情响应

        Raises:
            BusinessException: 操作失败
        """
        data = {"id": browser_id}
        result = await self._make_request("/browser/detail", data)
        return BrowserDetailResponse(**result)

    async def get_browser_list(self, params: BrowserListRequest) -> BrowserListResponse:
        """
        分页获取浏览器窗口列表

        Args:
            params: 浏览器列表查询请求

        Returns:
            浏览器列表响应

        Raises:
            BusinessException: 操作失败
        """
        # 转换页码（从1开始转换为从0开始）
        page_data = params.model_dump(exclude_unset=True)
        page_data["page"] = params.page - 1  # 比特浏览器API页码从0开始
        page_data["pageSize"] = params.size

        result = await self._make_request("/browser/list", page_data)

        # 转换响应格式
        return BrowserListResponse(
            total=result.get("total", 0),
            page=params.page,
            pageSize=params.size,
            list=[BrowserListItem(**item) for item in result.get("list", [])]
        )

    async def arrange_windows(self, seqlist: Optional[List[int]] = None) -> None:
        """
        一键自适应排列窗口

        Args:
            seqlist: 窗口序列列表（可选）

        Raises:
            BusinessException: 操作失败
        """
        data = {"seqlist": seqlist or []}
        await self._make_request("/windowbounds/flexable", data)

    async def close_all_browsers(self) -> None:
        """
        关闭所有浏览器窗口

        Raises:
            BusinessException: 操作失败
        """
        await self._make_request("/browser/close/all")


# 创建服务实例
bit_browser_service = BitBrowserService()

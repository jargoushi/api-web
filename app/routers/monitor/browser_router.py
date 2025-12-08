from fastapi import APIRouter, Depends

from app.schemas.monitor.browser import (
    BrowserOpenRequest, BrowserCloseRequest, BrowserDeleteRequest, BrowserDetailRequest,
    BrowserDetailResponse, BrowserListRequest, WindowArrangeRequest, BrowserListItem, BrowserBatchOpenResponse
)
from app.schemas.common.pagination import PageResponse
from app.schemas.common.response import ApiResponse, success_response
from app.services.monitor.browser_service import bit_browser_service

router = APIRouter()


@router.post("/health", response_model=ApiResponse, summary="健康检查")
async def health_check():
    """
    检查比特浏览器Local Server连接状态
    """
    await bit_browser_service.health_check()
    return success_response(data=True)


@router.post("/open",
             response_model=ApiResponse[BrowserBatchOpenResponse],
             summary="批量打开浏览器窗口")
async def open_browser(request: BrowserOpenRequest):
    """
    批量打开浏览器窗口

    - **ids**: 浏览器窗口ID列表（必填）
    - **args**: 浏览器启动参数（可选）
    - **ignoreDefaultUrls**: 忽略已同步URL（可选）
    - **newPageUrl**: 指定打开URL（可选）
    """
    result = await bit_browser_service.open_browser(request)
    return success_response(data=result)


@router.post("/close", response_model=ApiResponse, summary="关闭浏览器窗口")
async def close_browser(request: BrowserCloseRequest):
    """
    关闭指定浏览器窗口

    - **id**: 浏览器窗口ID（必填）
    """
    await bit_browser_service.close_browser(request.id)
    return success_response(data=True)


@router.post("/delete", response_model=ApiResponse, summary="删除浏览器窗口")
async def delete_browser(request: BrowserDeleteRequest):
    """
    彻底删除浏览器窗口

    - **id**: 浏览器窗口ID（必填）
    """
    await bit_browser_service.delete_browser(request.id)
    return success_response(data=True)


@router.post("/detail", response_model=ApiResponse[BrowserDetailResponse], summary="获取浏览器窗口详情")
async def get_browser_detail(request: BrowserDetailRequest):
    """
    获取浏览器窗口详细信息

    - **id**: 浏览器窗口ID（必填）
    """
    result = await bit_browser_service.get_browser_detail(request.id)
    return success_response(data=result)


@router.post("/list", response_model=ApiResponse[PageResponse[BrowserListItem]],
             summary="分页获取浏览器窗口列表")
async def get_browser_list(params: BrowserListRequest = Depends()):
    """
    获取浏览器窗口列表（分页+条件查询）
    """
    result = await bit_browser_service.get_browser_list(params)

    page_response = PageResponse[BrowserListItem](
        total=result.total,
        page=result.page,
        size=result.pageSize,
        pages=(result.total + result.pageSize - 1) // result.pageSize,
        items=result.list
    )

    return success_response(data=page_response)


@router.post("/arrange", response_model=ApiResponse, summary="一键自适应排列窗口")
async def arrange_windows(request: WindowArrangeRequest):
    """
    自适应排列所有或指定窗口

    - **seqlist**: 窗口序号列表，不传则排列全部窗口（可选）
    """
    await bit_browser_service.arrange_windows(request.seqlist)
    return success_response(data=True)


@router.post("/close-all", response_model=ApiResponse, summary="关闭所有浏览器窗口")
async def close_all_browsers():
    """
    关闭所有已打开的浏览器窗口

    注意：此操作会关闭所有当前运行的浏览器窗口，无需参数
    """
    await bit_browser_service.close_all_browsers()
    return success_response(data=True)

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.common.pagination import PageRequest
from app.schemas.common.response import BaseResponseModel


class BrowserFingerPrint(BaseModel):
    """浏览器指纹对象"""
    coreProduct: Optional[str] = Field("chrome", description="内核，chrome | firefox")
    coreVersion: Optional[str] = Field("130", description="内核版本")
    ostype: Optional[str] = Field("PC", description="操作系统平台 PC | Android | IOS")
    os: Optional[str] = Field("Win32", description="操作系统")
    osVersion: Optional[str] = Field("", description="操作系统版本")
    userAgent: Optional[str] = Field("", description="用户代理")
    openWidth: Optional[int] = Field(1280, description="窗口宽度")
    openHeight: Optional[int] = Field(720, description="窗口高度")

    model_config = ConfigDict(extra="allow")  # 允许其他指纹字段


class BrowserOpenRequest(BaseModel):
    """打开浏览器窗口请求参数"""
    ids: Optional[List[str]] = Field(None, description="浏览器窗口ID列表")
    args: Optional[List[str]] = Field([], description="浏览器启动参数")
    ignoreDefaultUrls: Optional[bool] = Field(False, description="忽略已同步URL")
    newPageUrl: Optional[str] = Field("", description="指定打开URL")


class BrowserCloseRequest(BaseModel):
    """关闭浏览器窗口请求参数"""
    id: str = Field(..., description="浏览器窗口ID")


class BrowserDeleteRequest(BaseModel):
    """删除浏览器窗口请求参数"""
    id: str = Field(..., description="浏览器窗口ID")


class BrowserDetailRequest(BaseModel):
    """获取浏览器详情请求参数"""
    id: str = Field(..., description="浏览器窗口ID")


class BrowserListRequest(PageRequest):
    """浏览器列表查询参数"""
    groupId: Optional[str] = Field(None, description="分组ID")
    name: Optional[str] = Field(None, description="窗口名称模糊查询")


class WindowArrangeRequest(BaseModel):
    """窗口排列请求参数"""
    seqlist: Optional[List[int]] = Field([], description="窗口序号列表")


# 响应模型
class BrowserOpenResponse(BaseResponseModel):
    """打开浏览器窗口响应"""
    ws: str = Field(..., description="WebSocket连接地址")
    http: str = Field(..., description="HTTP连接地址")
    name: str = Field(..., description="窗口名称")
    remark: str = Field(..., description="备注")
    groupId: str = Field(None, description="分组ID")


class BatchOpenResult(BaseResponseModel):
    """批量打开结果项"""
    id: str = Field(..., description="窗口ID")
    success: bool = Field(..., description="是否成功")
    data: Optional[BrowserOpenResponse] = Field(None, description="成功时的响应数据")
    error: Optional[str] = Field(None, description="失败时的错误信息")


class BrowserBatchOpenResponse(BaseResponseModel):
    """批量打开浏览器窗口响应"""
    results: List[BatchOpenResult] = Field(..., description="批量打开结果列表")
    total: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    fail_count: int = Field(..., description="失败数量")


class BrowserDetailResponse(BaseResponseModel):
    """浏览器详情响应"""
    id: str = Field(..., description="窗口ID")
    name: str = Field(..., description="窗口名称")
    status: int = Field(..., description="状态")
    proxyType: Optional[str] = Field(None, description="代理类型")
    host: Optional[str] = Field(None, description="代理主机")
    port: Optional[int] = Field(None, description="代理端口")
    browserFingerPrint: Optional[Dict[str, Any]] = Field(None, description="指纹信息")
    createdTime: Optional[str] = Field(None, description="创建时间")

    model_config = ConfigDict(extra="allow")  # 允许其他字段


class BrowserListItem(BaseResponseModel):
    """浏览器列表项"""
    id: str = Field(..., description="窗口ID")
    name: str = Field(..., description="窗口名称")
    status: int = Field(..., description="状态")
    seq: int = Field(..., description="序号")
    proxyType: Optional[str] = Field(None, description="代理类型")
    host: Optional[str] = Field(None, description="代理主机")
    port: Optional[int] = Field(None, description="代理端口")
    createdTime: Optional[str] = Field(None, description="创建时间")

    model_config = ConfigDict(extra="allow")  # 允许其他字段


class BrowserListResponse(BaseResponseModel):
    """浏览器列表响应"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    pageSize: int = Field(..., description="每页数量")
    list: List[BrowserListItem] = Field(..., description="数据列表")

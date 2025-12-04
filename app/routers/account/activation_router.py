from fastapi import APIRouter

from app.schemas.account.activation import (
    ActivationCodeGetRequest,
    ActivationCodeInvalidateRequest,
    ActivationCodeBatchResponse, ActivationCodeBatchCreateRequest, ActivationCodeQueryRequest, ActivationCodeResponse,
)
from app.schemas.common.pagination import PageResponse
from app.schemas.common.response import ApiResponse, success_response, paginated_response
from app.services.account.activation_service import ActivationCodeService

router = APIRouter()


@router.post("/init", response_model=ApiResponse[ActivationCodeBatchResponse], summary="初始化激活码数据")
async def init_activation_codes(request: ActivationCodeBatchCreateRequest):
    """
    初始化激活码数据（根据类型维护过期时间）

    - **type**: 激活码类型（0：日卡 1：月卡 2：年卡 3：永久卡）
    - **count**: 生成数量
    """
    result = await ActivationCodeService.init_activation_codes(request)
    return success_response(data=result)


@router.post("/distribute", response_model=ApiResponse[list], summary="派发激活码")
async def distribute_activation_codes(request: ActivationCodeGetRequest):
    """
    派发激活码（根据类型查询指定数量未使用的激活码，并更新状态为已分发）

    - **type**: 激活码类型（0：日卡 1：月卡 2：年卡 3：永久卡）
    - **count**: 派发数量，默认1条
    """
    activation_codes = await ActivationCodeService.distribute_activation_codes(request)
    return success_response(data=activation_codes)


@router.post("/activate", response_model=ApiResponse[ActivationCodeResponse], summary="激活激活码")
async def activate_activation_code(activation_code: str):
    """
    激活激活码（将已分发状态的激活码激活，设置激活时间和过期时间）

    - **activation_code**: 激活码
    """
    result = await ActivationCodeService.activate_activation_code(activation_code)
    return success_response(data=result)


@router.post("/invalidate", response_model=ApiResponse[bool], summary="激活码作废")
async def invalidate_activation_code(request: ActivationCodeInvalidateRequest):
    """
    激活码作废（将已分发或已激活状态的激活码作废）

    - **activation_code**: 激活码
    """
    result = await ActivationCodeService.invalidate_activation_code(request)
    return success_response(data=result)


@router.get("/{activation_code}", response_model=ApiResponse[ActivationCodeResponse], summary="获取激活码详情")
async def get_activation_code_detail(activation_code: str):
    """
    根据激活码获取详情信息
    """
    result = await ActivationCodeService.get_activation_code_by_code(activation_code)
    return success_response(data=result)


@router.post("/pageList", response_model=ApiResponse[PageResponse[ActivationCodeResponse]], summary="分页获取激活码列表")
async def get_paginated_activation_codes(params: ActivationCodeQueryRequest):
    """
    获取激活码列表（分页+条件查询）
    - **page**: 页码，从1开始，默认为1
    - **size**: 每页数量，默认为10，最大100
    - **type**: 激活码类型（0：日卡 1：月卡 2：年卡 3：永久卡）
    - **activation_code**: 激活码（精准匹配）
    - **status**: 激活码状态（0：未使用 1：已分发 2：已激活 3：作废）
    - **distributed_at_start**: 分发时间开始（包含）
    - **distributed_at_end**: 分发时间结束（包含）
    - **activated_at_start**: 激活时间开始（包含）
    - **activated_at_end**: 激活时间结束（包含）
    - **expire_time_start**: 过期时间开始（包含）
    - **expire_time_end**: 过期时间结束（包含）
    """
    query = ActivationCodeService.get_activation_code_queryset(params)
    return await paginated_response(query, params)

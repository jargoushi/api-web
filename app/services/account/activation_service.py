import hashlib
import secrets
import string
from datetime import datetime
from typing import List

from app.core.config import Settings
from app.core.exceptions import BusinessException
from app.core.logging import log
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum
from app.models.account.activation_code import ActivationCode
from app.schemas.account.activation import (
    ActivationCodeBatchCreateRequest,
    ActivationCodeBatchResponse,
    ActivationCodeTypeResult,
    ActivationCodeGetRequest,
    ActivationCodeInvalidateRequest,
    ActivationCodeResponse, ActivationCodeQueryRequest
)


class ActivationCodeService:
    @staticmethod
    def generate_activation_code() -> str:
        """生成随机激活码"""
        # 生成随机种子
        seed = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

        # 第一次哈希：SHA256
        hash1 = hashlib.sha256(seed.encode()).hexdigest()

        # 第二次哈希：MD5（取前32位）
        hash2 = hashlib.md5(hash1.encode()).hexdigest()

        # 生成后缀
        suffix_chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        suffix = ''.join(secrets.choice(suffix_chars) for _ in range(16))

        return f"{hash2}{suffix}"

    @staticmethod
    async def init_activation_codes(request: ActivationCodeBatchCreateRequest) -> ActivationCodeBatchResponse:
        """批量初始化激活码数据"""
        log.info(f"开始批量生成激活码，共{len(request.items)}种类型")

        results = []
        total_count = 0
        summary = {}

        for item in request.items:
            # 使用枚举获取类型信息
            type_enum = ActivationTypeEnum.from_code(item.type)
            type_name = type_enum.desc

            log.info(f"生成{type_name}激活码，数量：{item.count}")

            activation_codes = []

            for i in range(item.count):
                # 生成唯一的激活码
                while True:
                    code = ActivationCodeService.generate_activation_code()
                    if not await ActivationCode.filter(activation_code=code).exists():
                        break

                # 创建激活码记录，使用枚举值
                await ActivationCode.create(
                    activation_code=code,
                    expire_time=None,
                    type=item.type,
                    status=ActivationCodeStatusEnum.UNUSED.code,
                    activated_at=None
                )
                activation_codes.append(code)

            # 创建该类型的结果
            type_result = ActivationCodeTypeResult(
                type=item.type,
                type_name=type_name,
                activation_codes=activation_codes,
                count=len(activation_codes)
            )
            results.append(type_result)
            total_count += len(activation_codes)
            summary[type_name] = len(activation_codes)

            log.info(f"成功生成{len(activation_codes)}个{type_name}激活码")

        log.info(f"批量生成完成，总计{total_count}个激活码")

        return ActivationCodeBatchResponse(
            results=results,
            total_count=total_count,
            summary=summary
        )

    @staticmethod
    async def distribute_activation_codes(request: ActivationCodeGetRequest) -> List[str]:
        """派发激活码（获取激活码并设置为已分发状态）"""
        log.info(f"派发激活码，类型：{request.type}，数量：{request.count}")

        # 查询指定类型未使用的激活码，按创建时间倒序
        codes = await ActivationCode.filter(
            type=request.type,
            status=ActivationCodeStatusEnum.UNUSED.code
        ).order_by("-created_at").limit(request.count)

        if len(codes) < request.count:
            type_enum = ActivationTypeEnum.from_code(request.type)
            raise BusinessException(
                message=f"{type_enum.desc}可用激活码不足，需要{request.count}个，实际只有{len(codes)}个")

        activation_codes = []

        # 批量更新状态为已分发
        for code in codes:
            # 激活码被分发
            code.distribute()
            await code.save()

            activation_codes.append(code.activation_code)

        log.info(f"成功派发{len(activation_codes)}个激活码")
        return activation_codes

    @staticmethod
    async def get_distributed_activation_code(activation_code: str) -> ActivationCode:
        """查询已分发的激活码"""
        log.info(f"查询已分发激活码：{activation_code}")

        code = await ActivationCode.get_or_none(activation_code=activation_code)
        if not code:
            raise BusinessException(message="激活码不存在")

        if code.status != ActivationCodeStatusEnum.DISTRIBUTED.code:
            raise BusinessException(message="激活码状态不正确，必须是已分发状态")

        log.info(f"成功查询已分发激活码：{activation_code}")
        return code

    @staticmethod
    async def activate_activation_code(activation_code: str) -> ActivationCodeResponse:
        """激活激活码（将已分发状态的激活码激活）"""
        log.info(f"激活激活码：{activation_code}")

        code = await ActivationCode.get_or_none(activation_code=activation_code)
        if not code:
            raise BusinessException(message="激活码不存在")

        if code.status == ActivationCodeStatusEnum.INVALID.code:
            raise BusinessException(message="激活码已作废，无法激活")

        if code.status == ActivationCodeStatusEnum.UNUSED.code:
            raise BusinessException(message="激活码未分发，请先分发激活码")

        if code.status == ActivationCodeStatusEnum.ACTIVATED.code:
            raise BusinessException(message="激活码已激活，无需重复激活")

        # 激活激活码
        code.activate()
        await code.save()

        log.info(f"激活码{activation_code}激活成功")
        return ActivationCodeResponse.model_validate(code, from_attributes=True)

    @staticmethod
    async def invalidate_activation_code(request: ActivationCodeInvalidateRequest) -> bool:
        """激活码作废（支持已分发和已激活状态的激活码作废）"""
        log.info(f"作废激活码：{request.activation_code}")

        code = await ActivationCode.get_or_none(activation_code=request.activation_code)
        if not code:
            raise BusinessException(message="激活码不存在")

        if code.status == ActivationCodeStatusEnum.INVALID.code:
            raise BusinessException(message="激活码已作废")

        if code.status == ActivationCodeStatusEnum.UNUSED.code:
            raise BusinessException(message="激活码未分发，无法作废")

        # 作废激活码
        code.invalidate()
        await code.save()

        log.info(f"激活码{request.activation_code}已作废")
        return True

    @staticmethod
    async def get_activation_code_by_code(activation_code: str) -> ActivationCodeResponse:
        """根据激活码获取详情"""
        code = await ActivationCode.get_or_none(activation_code=activation_code)
        if not code:
            raise BusinessException(message="激活码不存在")

        return ActivationCodeResponse.model_validate(code, from_attributes=True)

    @staticmethod
    def get_activation_code_queryset(params: ActivationCodeQueryRequest):
        """获取激活码查询集（支持条件过滤+分页）"""
        query = ActivationCode.all()  # 基础查询，不过滤状态

        # 动态添加过滤条件
        if params.type is not None:
            query = query.filter(type=params.type)

        if params.activation_code:
            query = query.filter(activation_code=params.activation_code)

        if params.status is not None:
            query = query.filter(status=params.status)

        # 分发时间区间查询
        if params.distributed_at_start:
            query = query.filter(distributed_at__gte=params.distributed_at_start)
        if params.distributed_at_end:
            query = query.filter(distributed_at__lte=params.distributed_at_end)

        # 激活时间区间查询
        if params.activated_at_start:
            query = query.filter(activated_at__gte=params.activated_at_start)
        if params.activated_at_end:
            query = query.filter(activated_at__lte=params.activated_at_end)

        # 过期时间区间查询
        if params.expire_time_start:
            query = query.filter(expire_time__gte=params.expire_time_start)
        if params.expire_time_end:
            query = query.filter(expire_time__lte=params.expire_time_end)

        # 保持原排序：按创建时间倒序
        return query.order_by("-created_at")

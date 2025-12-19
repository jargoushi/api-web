from datetime import datetime
from typing import List

from app.core.config import settings
from app.core.exceptions import BusinessException
from app.core.logging import log
from app.enums.account.activation_type import ActivationTypeEnum
from app.enums.account.activation_status import ActivationCodeStatusEnum
from app.repositories.account.activation_repository import activation_repository
from app.schemas.account.activation import (
    ActivationCodeBatchCreateRequest,
    ActivationCodeBatchResponse,
    ActivationCodeTypeResult,
    ActivationCodeGetRequest,
    ActivationCodeInvalidateRequest,
    ActivationCodeResponse, ActivationCodeQueryRequest
)
from app.util.activation_code_generator import code_generator


class ActivationCodeService:
    """激活码服务类"""

    async def _generate_unique_code(self) -> str:
        """
        生成唯一的激活码

        Returns:
            唯一的激活码字符串
        """
        while True:
            code = code_generator.generate()
            if not await activation_repository.code_exists(code):
                return code

    async def init_activation_codes(self, request: ActivationCodeBatchCreateRequest) -> ActivationCodeBatchResponse:
        """
        批量初始化激活码数据

        Args:
            request: 批量创建请求

        Returns:
            批量创建响应
        """
        log.info(f"开始批量生成激活码，共{len(request.items)}种类型")

        results = []
        total_count = 0
        summary = {}

        for item in request.items:
            type_enum = ActivationTypeEnum.from_code(item.type)
            type_name = type_enum.desc

            log.info(f"生成{type_name}激活码，数量：{item.count}")

            activation_codes = []

            for i in range(item.count):
                code = await self._generate_unique_code()
                await activation_repository.create_activation_code(
                    activation_code=code,
                    type_code=item.type,
                    status=ActivationCodeStatusEnum.UNUSED.code,
                    expire_time=None,
                    activated_at=None
                )
                activation_codes.append(code)

            # 构建响应
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

    async def distribute_activation_codes(self, request: ActivationCodeGetRequest) -> List[str]:
        """
        派发激活码

        Args:
            request: 派发请求

        Returns:
            激活码字符串列表

        Raises:
            BusinessException: 激活码数量不足
        """
        log.info(f"派发激活码，类型：{request.type}，数量：{request.count}")

        codes = await activation_repository.find_unused_codes(
            type_code=request.type,
            limit=request.count
        )

        if len(codes) < request.count:
            type_enum = ActivationTypeEnum.from_code(request.type)
            raise BusinessException(
                message=f"{type_enum.desc}可用激活码不足，需要{request.count}个，实际只有{len(codes)}个")

        activation_codes = []
        for code in codes:
            await activation_repository.distribute_activation_code(code)
            activation_codes.append(code.activation_code)

        log.info(f"成功派发{len(activation_codes)}个激活码")
        return activation_codes

    async def get_distributed_activation_code(self, activation_code: str):
        """
        查询已分发的激活码

        Args:
            activation_code: 激活码字符串

        Returns:
            激活码实例

        Raises:
            BusinessException: 激活码不存在或状态不正确
        """
        log.info(f"查询已分发激活码：{activation_code}")

        code = await activation_repository.find_by_code(activation_code)

        if not code:
            raise BusinessException(message="激活码不存在")

        if code.status != ActivationCodeStatusEnum.DISTRIBUTED.code:
            raise BusinessException(message="激活码状态不正确，必须是已分发状态")

        log.info(f"成功查询已分发激活码：{activation_code}")
        return code

    async def activate_activation_code(self, activation_code: str) -> ActivationCodeResponse:
        """
        激活激活码

        Args:
            activation_code: 激活码字符串

        Returns:
            激活码响应

        Raises:
            BusinessException: 激活码不存在或状态不允许激活
        """
        log.info(f"激活激活码：{activation_code}")

        code = await activation_repository.find_by_code(activation_code)

        if not code:
            raise BusinessException(message="激活码不存在")

        if code.status == ActivationCodeStatusEnum.INVALID.code:
            raise BusinessException(message="激活码已作废，无法激活")

        if code.status == ActivationCodeStatusEnum.UNUSED.code:
            raise BusinessException(message="激活码未分发，请先分发激活码")

        if code.status == ActivationCodeStatusEnum.ACTIVATED.code:
            raise BusinessException(message="激活码已激活，无需重复激活")

        await activation_repository.activate_activation_code(code, settings.activation_grace_hours)

        log.info(f"激活码{activation_code}激活成功")
        return ActivationCodeResponse.model_validate(code, from_attributes=True)

    async def invalidate_activation_code(self, request: ActivationCodeInvalidateRequest) -> bool:
        """
        激活码作废

        Args:
            request: 作废请求

        Returns:
            是否成功

        Raises:
            BusinessException: 激活码不存在或状态不允许作废
        """
        log.info(f"作废激活码：{request.activation_code}")

        code = await activation_repository.find_by_code(request.activation_code)

        if not code:
            raise BusinessException(message="激活码不存在")

        if code.status == ActivationCodeStatusEnum.INVALID.code:
            raise BusinessException(message="激活码已作废")

        if code.status == ActivationCodeStatusEnum.UNUSED.code:
            raise BusinessException(message="激活码未分发，无法作废")

        await activation_repository.invalidate_activation_code(code)

        log.info(f"激活码{request.activation_code}已作废")
        return True

    async def get_activation_code_by_code(self, activation_code: str) -> ActivationCodeResponse:
        """
        根据激活码获取详情

        Args:
            activation_code: 激活码字符串

        Returns:
            激活码响应

        Raises:
            BusinessException: 激活码不存在
        """
        code = await activation_repository.find_by_code(activation_code)

        if not code:
            raise BusinessException(message="激活码不存在")

        return ActivationCodeResponse.model_validate(code, from_attributes=True)

    def get_activation_code_list(self, params: ActivationCodeQueryRequest):
        """
        获取激活码查询集（用于分页）

        Args:
            params: 查询参数

        Returns:
            激活码查询集（QuerySet）
        """
        return activation_repository.find_with_filters(params)


# 创建服务实例
activation_service = ActivationCodeService()

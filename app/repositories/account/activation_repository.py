"""
激活码仓储类
封装激活码相关的所有数据访问操作
"""
from typing import Optional, List
from datetime import datetime

from app.repositories.base import BaseRepository
from app.models.account.activation_code import ActivationCode
from app.enums.account.activation_status import ActivationCodeStatusEnum
from app.util.time_util import get_utc_now


class ActivationCodeRepository(BaseRepository[ActivationCode]):
    """
    激活码仓储类

    提供激活码相关的数据访问方法，封装所有与数据库交互的操作
    """

    def __init__(self):
        """初始化激活码仓储"""
        super().__init__(ActivationCode)

    async def find_by_code(self, code: str) -> Optional[ActivationCode]:
        """
        根据激活码查询

        Args:
            code: 激活码字符串

        Returns:
            激活码实例，如果不存在则返回 None
        """
        return await self.get_or_none(activation_code=code)

    async def find_unused_codes(
        self,
        type_code: int,
        limit: int
    ) -> List[ActivationCode]:
        """
        查询未使用的激活码

        Args:
            type_code: 激活码类型
            limit: 查询数量限制

        Returns:
            激活码列表，按创建时间倒序
        """
        return await self.model.filter(
            type=type_code,
            status=ActivationCodeStatusEnum.UNUSED.code
        ).order_by("-created_at").limit(limit).all()

    async def find_distributed_codes(
        self,
        type_code: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[ActivationCode]:
        """
        查询已分发的激活码

        Args:
            type_code: 激活码类型（可选）
            limit: 查询数量限制（可选）

        Returns:
            激活码列表
        """
        query = self.model.filter(status=ActivationCodeStatusEnum.DISTRIBUTED.code)

        if type_code is not None:
            query = query.filter(type=type_code)

        query = query.order_by("-distributed_at")

        if limit is not None:
            query = query.limit(limit)

        return await query.all()

    async def code_exists(self, code: str) -> bool:
        """
        检查激活码是否存在

        Args:
            code: 激活码字符串

        Returns:
            是否存在
        """
        return await self.exists(activation_code=code)

    async def count_by_status(
        self,
        status: int,
        type_code: Optional[int] = None
    ) -> int:
        """
        按状态统计激活码数量

        Args:
            status: 激活码状态
            type_code: 激活码类型（可选）

        Returns:
            激活码数量
        """
        filters = {"status": status}
        if type_code is not None:
            filters["type"] = type_code

        return await self.count(**filters)

    def find_with_filters(self, params):
        """
        复杂条件查询激活码（返回 QuerySet，用于分页）

        Args:
            params: 查询参数对象

        Returns:
            激活码查询集（QuerySet）
        """
        query = self.model.all()

        if params.type is not None:
            query = query.filter(type=params.type)

        if params.activation_code:
            query = query.filter(activation_code=params.activation_code)

        if params.status is not None:
            query = query.filter(status=params.status)

        if params.distributed_at_start:
            query = query.filter(distributed_at__gte=params.distributed_at_start)
        if params.distributed_at_end:
            query = query.filter(distributed_at__lte=params.distributed_at_end)

        if params.activated_at_start:
            query = query.filter(activated_at__gte=params.activated_at_start)
        if params.activated_at_end:
            query = query.filter(activated_at__lte=params.activated_at_end)

        if params.expire_time_start:
            query = query.filter(expire_time__gte=params.expire_time_start)
        if params.expire_time_end:
            query = query.filter(expire_time__lte=params.expire_time_end)

        query = query.order_by("-created_at")

        return query

    async def count_unused_by_type(self, type_code: int) -> int:
        """
        统计指定类型的未使用激活码数量

        Args:
            type_code: 激活码类型

        Returns:
            未使用激活码数量
        """
        return await self.count(
            type=type_code,
            status=ActivationCodeStatusEnum.UNUSED.code
        )

    async def create_activation_code(
        self,
        activation_code: str,
        type_code: int,
        status: int,
        expire_time: Optional[datetime] = None,
        activated_at: Optional[datetime] = None
    ) -> ActivationCode:
        """
        创建激活码

        Args:
            activation_code: 激活码字符串
            type_code: 激活码类型
            status: 激活码状态
            expire_time: 过期时间（可选）
            activated_at: 激活时间（可选）

        Returns:
            创建的激活码实例
        """
        return await self.create(
            activation_code=activation_code,
            type=type_code,
            status=status,
            expire_time=expire_time,
            activated_at=activated_at
        )

    async def distribute_activation_code(self, code: ActivationCode) -> ActivationCode:
        """
        分发激活码

        Args:
            code: 激活码实例

        Returns:
            更新后的激活码实例
        """
        code.distributed_at = get_utc_now()
        code.status = ActivationCodeStatusEnum.DISTRIBUTED.code
        await code.save()
        return code

    async def activate_activation_code(
        self,
        code: ActivationCode,
        grace_hours: int
    ) -> ActivationCode:
        """
        激活激活码

        Args:
            code: 激活码实例
            grace_hours: 宽限小时数

        Returns:
            更新后的激活码实例
        """
        activated_at = get_utc_now()
        expire_time = code.type_enum.get_expire_time_from(activated_at, grace_hours)

        code.activated_at = activated_at
        code.expire_time = expire_time
        code.status = ActivationCodeStatusEnum.ACTIVATED.code
        await code.save()
        return code

    async def invalidate_activation_code(self, code: ActivationCode) -> ActivationCode:
        """
        作废激活码

        Args:
            code: 激活码实例

        Returns:
            更新后的激活码实例
        """
        code.status = ActivationCodeStatusEnum.INVALID.code
        await code.save()
        return code


# 创建单例实例
activation_repository = ActivationCodeRepository()

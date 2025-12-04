"""
基础仓储类
提供通用的 CRUD 操作，所有具体的 Repository 都应继承此类
"""
from typing import TypeVar, Generic, Optional, List, Type, Dict, Any
from tortoise.models import Model
from tortoise.queryset import QuerySet

T = TypeVar('T', bound=Model)


class BaseRepository(Generic[T]):
    """
    基础仓储类

    提供通用的 CRUD 操作，封装 Tortoise ORM 的底层调用
    所有具体的 Repository 都应继承此类

    泛型参数:
        T: Model 类型，必须是 Tortoise Model 的子类
    """

    def __init__(self, model: Type[T]):
        """
        初始化仓储

        Args:
            model: Model 类型
        """
        self.model = model

    async def create(self, **kwargs) -> T:
        """
        创建记录

        Args:
            **kwargs: 字段值

        Returns:
            创建的 Model 实例
        """
        return await self.model.create(**kwargs)

    async def get_by_id(self, id: int) -> Optional[T]:
        """
        根据 ID 获取记录

        Args:
            id: 记录 ID

        Returns:
            Model 实例，如果不存在则返回 None
        """
        return await self.model.get_or_none(id=id)

    async def get_or_none(self, **filters) -> Optional[T]:
        """
        根据条件获取单条记录

        Args:
            **filters: 过滤条件

        Returns:
            Model 实例，如果不存在则返回 None
        """
        return await self.model.get_or_none(**filters)

    async def find_all(self, **filters) -> List[T]:
        """
        根据条件获取所有记录

        Args:
            **filters: 过滤条件

        Returns:
            Model 实例列表
        """
        return await self.model.filter(**filters).all()

    async def update(self, instance: T, **kwargs) -> T:
        """
        更新记录

        Args:
            instance: Model 实例
            **kwargs: 要更新的字段值

        Returns:
            更新后的 Model 实例
        """
        instance.update_from_dict(kwargs)
        await instance.save()
        return instance

    async def delete(self, instance: T) -> bool:
        """
        删除记录

        Args:
            instance: Model 实例

        Returns:
            是否删除成功
        """
        await instance.delete()
        return True

    async def exists(self, **filters) -> bool:
        """
        检查记录是否存在

        Args:
            **filters: 过滤条件

        Returns:
            是否存在
        """
        return await self.model.filter(**filters).exists()

    async def count(self, **filters) -> int:
        """
        统计记录数量

        Args:
            **filters: 过滤条件

        Returns:
            记录数量
        """
        return await self.model.filter(**filters).count()

    def get_queryset(self, **filters) -> QuerySet:
        """
        获取查询集

        Args:
            **filters: 过滤条件

        Returns:
            QuerySet 对象，可以继续链式调用
        """
        return self.model.filter(**filters)

    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[T]:
        """
        批量创建记录

        Args:
            objects: 对象列表，每个对象是一个字典

        Returns:
            创建的 Model 实例列表
        """
        instances = [self.model(**obj) for obj in objects]
        return await self.model.bulk_create(instances)

    async def bulk_update(
        self,
        instances: List[T],
        fields: List[str]
    ) -> int:
        """
        批量更新记录

        Args:
            instances: Model 实例列表
            fields: 要更新的字段列表

        Returns:
            更新的记录数量
        """
        return await self.model.bulk_update(instances, fields)

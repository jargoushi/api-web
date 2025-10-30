"""
简单的事务装饰器
提供基于注解的声明式事务支持
"""

import functools
from typing import Callable, Any
from tortoise import transactions


def transactional(func: Callable) -> Callable:
    """
    事务装饰器，确保方法中的所有数据库操作在事务中执行

    如果方法执行过程中出现任何异常，整个事务会自动回滚

    Args:
        func: 需要事务支持的异步函数

    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        async with transactions.in_transaction():
            return await func(*args, **kwargs)

    return wrapper
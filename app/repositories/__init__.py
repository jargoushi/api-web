"""
仓储层模块
封装所有数据访问逻辑，提供语义化的数据访问接口
"""

from .base import BaseRepository
from .account import ActivationCodeRepository, UserRepository

__all__ = [
    "BaseRepository",
    "ActivationCodeRepository",
    "UserRepository",
]

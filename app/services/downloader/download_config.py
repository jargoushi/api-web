"""下载配置"""

from dataclasses import dataclass
from typing import Optional

from app.enums.settings import DownloadSettingEnum


@dataclass
class DownloadConfig:
    """
    下载配置对象

    封装用户下载相关配置，提供便捷访问。
    """
    download_path: str
    proxy: Optional[str]

    @classmethod
    def default(cls) -> "DownloadConfig":
        """获取默认配置"""
        return cls(
            download_path=DownloadSettingEnum.DOWNLOAD_PATH.default,
            proxy=DownloadSettingEnum.PROXY_URL.default or None
        )

    @classmethod
    async def from_user(cls, user_id: int) -> "DownloadConfig":
        """
        从用户配置加载

        如果用户不存在或未配置，自动使用默认值。
        单次批量查询所有下载相关配置。

        Args:
            user_id: 用户 ID

        Returns:
            DownloadConfig 配置对象
        """
        from app.repositories.account.user_setting_repository import user_setting_repository

        # 单次批量查询所有下载相关配置
        setting_keys = [e.code for e in DownloadSettingEnum]
        user_settings = await user_setting_repository.find_by_user_and_keys(user_id, setting_keys)

        # 构建 code -> value 映射
        settings_map = {s.setting_key: s.setting_value for s in user_settings}

        # 获取值，不存在则使用默认值
        download_path = settings_map.get(
            DownloadSettingEnum.DOWNLOAD_PATH.code,
            DownloadSettingEnum.DOWNLOAD_PATH.default
        )
        proxy_value = settings_map.get(
            DownloadSettingEnum.PROXY_URL.code,
            DownloadSettingEnum.PROXY_URL.default
        )

        return cls(
            download_path=download_path,
            proxy=proxy_value
        )

"""
剪映工具类 - 草稿管理
"""
import os
import shutil
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class JianyingUtil:
    """剪映草稿管理工具类"""

    def __init__(self, draft_folder: Optional[str] = None):
        """
        初始化剪映工具

        Args:
            draft_folder: 剪映草稿文件夹路径，如果不提供则从环境变量读取
        """
        if draft_folder:
            self.draft_folder = Path(draft_folder)
        else:
            # 从环境变量读取
            draft_path = os.getenv("JIANYING_DRAFT_FOLDER")
            if not draft_path:
                raise ValueError("未配置剪映草稿文件夹路径，请设置 JIANYING_DRAFT_FOLDER 环境变量")
            self.draft_folder = Path(draft_path)

        if not self.draft_folder.exists():
            raise FileNotFoundError(f"剪映草稿文件夹不存在: {self.draft_folder}")

        # 剪映用户数据目录（用于清理缓存）
        self.user_data_folder = self.draft_folder.parent.parent

    def get_draft_list(self) -> List[Dict[str, any]]:
        """
        获取所有草稿列表

        Returns:
            草稿列表，每个草稿包含：
            - name: 草稿名称
            - path: 草稿完整路径
            - draft_file: draft_content.json 文件路径
            - size: 草稿文件夹大小（字节）
            - exists: draft_content.json 是否存在
        """
        drafts = []

        try:
            for item in self.draft_folder.iterdir():
                if item.is_dir():
                    draft_file = item / "draft_content.json"
                    draft_info = {
                        "name": item.name,
                        "path": str(item),
                        "draft_file": str(draft_file),
                        "exists": draft_file.exists(),
                        "size": self._get_folder_size(item)
                    }
                    drafts.append(draft_info)

            logger.info(f"找到 {len(drafts)} 个草稿")
            return drafts

        except Exception as e:
            logger.error(f"获取草稿列表失败: {str(e)}")
            raise

    def delete_draft_by_name(self, draft_name: str) -> bool:
        """
        根据名称删除草稿

        Args:
            draft_name: 草稿名称

        Returns:
            是否删除成功
        """
        draft_path = self.draft_folder / draft_name

        if not draft_path.exists():
            logger.warning(f"草稿不存在: {draft_name}")
            return False

        try:
            shutil.rmtree(draft_path)
            logger.info(f"✓ 已删除草稿: {draft_name}")
            return True

        except Exception as e:
            logger.error(f"删除草稿失败 {draft_name}: {str(e)}")
            raise

    def clear_all_drafts(self, confirm: bool = False) -> int:
        """
        清空所有草稿（危险操作）

        Args:
            confirm: 是否确认删除，必须显式传入 True

        Returns:
            删除的草稿数量
        """
        if not confirm:
            raise ValueError("清空草稿是危险操作，必须显式传入 confirm=True")

        drafts = self.get_draft_list()
        deleted_count = 0

        for draft in drafts:
            try:
                shutil.rmtree(draft["path"])
                deleted_count += 1
                logger.info(f"✓ 已删除: {draft['name']}")
            except Exception as e:
                logger.error(f"删除失败 {draft['name']}: {str(e)}")

        logger.info(f"清空完成，共删除 {deleted_count} 个草稿")
        return deleted_count

    def draft_exists(self, draft_name: str) -> bool:
        """
        检查草稿是否存在

        Args:
            draft_name: 草稿名称

        Returns:
            是否存在
        """
        draft_path = self.draft_folder / draft_name
        draft_file = draft_path / "draft_content.json"
        return draft_file.exists()

    def get_draft_path(self, draft_name: str) -> Optional[str]:
        """
        获取草稿的 draft_content.json 文件路径

        Args:
            draft_name: 草稿名称

        Returns:
            draft_content.json 文件路径，如果不存在返回 None
        """
        draft_path = self.draft_folder / draft_name / "draft_content.json"
        return str(draft_path) if draft_path.exists() else None

    def _get_folder_size(self, folder_path: Path) -> int:
        """
        计算文件夹大小

        Args:
            folder_path: 文件夹路径

        Returns:
            文件夹大小（字节）
        """
        total_size = 0
        try:
            for item in folder_path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 字节数

        Returns:
            格式化后的大小字符串
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

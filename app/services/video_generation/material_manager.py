import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.core.config import settings
from app.core.logging import log
from app.core.exceptions import BusinessException


class MaterialManager:
    """
    素材管理服务

    负责管理视频、音频、图片等素材文件
    """

    def __init__(self):
        """初始化服务"""
        self.material_base_path = getattr(settings, 'MATERIAL_BASE_PATH', './materials')
        self._ensure_directories()

    def _ensure_directories(self):
        """确保素材目录存在"""
        directories = [
            os.path.join(self.material_base_path, 'videos'),
            os.path.join(self.material_base_path, 'audios'),
            os.path.join(self.material_base_path, 'images'),
            os.path.join(self.material_base_path, 'subtitles'),
            os.path.join(self.material_base_path, 'temp'),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    async def get_material_path(
        self,
        material_type: str,
        filename: str
    ) -> str:
        """
        获取素材完整路径

        Args:
            material_type: 素材类型（video/audio/image/subtitle）
            filename: 文件名

        Returns:
            完整路径

        Raises:
            BusinessException: 文件不存在
        """
        type_map = {
            'video': 'videos',
            'audio': 'audios',
            'image': 'images',
            'subtitle': 'subtitles'
        }

        if material_type not in type_map:
            raise BusinessException(message=f"不支持的素材类型：{material_type}")

        path = os.path.join(
            self.material_base_path,
            type_map[material_type],
            filename
        )

        if not os.path.exists(path):
            raise BusinessException(message=f"素材文件不存在：{path}")

        return path

    async def list_materials(
        self,
        material_type: str,
        pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出素材文件

        Args:
            material_type: 素材类型
            pattern: 文件名模式（可选）

        Returns:
            素材文件列表

        Raises:
            BusinessException: 列出失败
        """
        try:
            type_map = {
                'video': 'videos',
                'audio': 'audios',
                'image': 'images',
                'subtitle': 'subtitles'
            }

            if material_type not in type_map:
                raise BusinessException(message=f"不支持的素材类型：{material_type}")

            directory = os.path.join(self.material_base_path, type_map[material_type])

            materials = []
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)

                if not os.path.isfile(filepath):
                    continue

                if pattern and pattern not in filename:
                    continue

                stat = os.stat(filepath)
                materials.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'modified_at': stat.st_mtime
                })

            return materials
        except Exception as e:
            log.error(f"列出素材失败：{str(e)}")
            raise BusinessException(message=f"列出素材失败：{str(e)}")

    async def save_material(
        self,
        material_type: str,
        filename: str,
        content: bytes
    ) -> str:
        """
        保存素材文件

        Args:
            material_type: 素材类型
            filename: 文件名
            content: 文件内容

        Returns:
            保存的文件路径

        Raises:
            BusinessException: 保存失败
        """
        try:
            type_map = {
                'video': 'videos',
                'audio': 'audios',
                'image': 'images',
                'subtitle': 'subtitles'
            }

            if material_type not in type_map:
                raise BusinessException(message=f"不支持的素材类型：{material_type}")

            filepath = os.path.join(
                self.material_base_path,
                type_map[material_type],
                filename
            )

            with open(filepath, 'wb') as f:
                f.write(content)

            log.info(f"素材保存成功：{filepath}")
            return filepath
        except Exception as e:
            log.error(f"保存素材失败：{str(e)}")
            raise BusinessException(message=f"保存素材失败：{str(e)}")

    async def delete_material(
        self,
        material_type: str,
        filename: str
    ) -> bool:
        """
        删除素材文件

        Args:
            material_type: 素材类型
            filename: 文件名

        Returns:
            是否删除成功

        Raises:
            BusinessException: 删除失败
        """
        try:
            filepath = await self.get_material_path(material_type, filename)

            if os.path.exists(filepath):
                os.remove(filepath)
                log.info(f"素材删除成功：{filepath}")
                return True

            return False
        except Exception as e:
            log.error(f"删除素材失败：{str(e)}")
            raise BusinessException(message=f"删除素材失败：{str(e)}")

    async def get_temp_path(self, filename: str) -> str:
        """
        获取临时文件路径

        Args:
            filename: 文件名

        Returns:
            临时文件路径
        """
        return os.path.join(self.material_base_path, 'temp', filename)

    async def cleanup_temp(self) -> int:
        """
        清理临时文件

        Returns:
            清理的文件数量
        """
        try:
            temp_dir = os.path.join(self.material_base_path, 'temp')
            count = 0

            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    count += 1

            log.info(f"清理了 {count} 个临时文件")
            return count
        except Exception as e:
            log.error(f"清理临时文件失败：{str(e)}")
            return 0


# 创建服务实例
material_manager = MaterialManager()

import sys
import os
from typing import Optional

# 将 pyJianYingDraft 源码路径添加到 sys.path
PYJIANYING_PATH = os.path.join(os.path.dirname(__file__), "../../../pyJianYingDraft_source")
if PYJIANYING_PATH not in sys.path:
    sys.path.insert(0, PYJIANYING_PATH)

import pyJianYingDraft as draft
from pyJianYingDraft import ExportResolution, ExportFramerate

from app.core.config import settings
from app.core.logging import log
from app.core.exceptions import BusinessException


class ExportService:
    """
    视频导出服务

    负责控制剪映导出视频
    """

    def __init__(self):
        """初始化服务"""
        self.controller = None

    def _ensure_controller(self):
        """确保控制器已初始化"""
        if not self.controller:
            try:
                self.controller = draft.JianyingController()
                log.info("剪映控制器初始化成功")
            except Exception as e:
                log.error(f"初始化剪映控制器失败：{str(e)}")
                raise BusinessException(message=f"初始化剪映控制器失败，请确保剪映已打开并位于目录页：{str(e)}")

        return self.controller

    async def export_draft(
        self,
        draft_name: str,
        export_path: str,
        resolution: str = "1080p",
        framerate: int = 30
    ) -> str:
        """
        导出草稿为视频

        Args:
            draft_name: 草稿名称
            export_path: 导出路径（可以是文件夹或完整文件路径）
            resolution: 分辨率（720p/1080p/2k/4k）
            framerate: 帧率（24/30/60）

        Returns:
            导出的视频文件路径

        Raises:
            BusinessException: 导出失败
        """
        try:
            log.info(f"开始导出草稿：{draft_name}")

            ctrl = self._ensure_controller()

            # 转换分辨率
            resolution_map = {
                "720p": ExportResolution.RES_720P,
                "1080p": ExportResolution.RES_1080P,
                "2k": ExportResolution.RES_2K,
                "4k": ExportResolution.RES_4K
            }

            if resolution not in resolution_map:
                raise BusinessException(message=f"不支持的分辨率：{resolution}")

            # 转换帧率
            framerate_map = {
                24: ExportFramerate.FR_24,
                30: ExportFramerate.FR_30,
                60: ExportFramerate.FR_60
            }

            if framerate not in framerate_map:
                raise BusinessException(message=f"不支持的帧率：{framerate}")

            # 导出视频
            ctrl.export_draft(
                draft_name,
                export_path,
                resolution=resolution_map[resolution],
                framerate=framerate_map[framerate]
            )

            log.info(f"草稿 {draft_name} 导出成功：{export_path}")
            return export_path
        except Exception as e:
            log.error(f"导出草稿失败：{str(e)}")
            raise BusinessException(message=f"导出草稿失败：{str(e)}")

    async def batch_export(
        self,
        draft_names: list[str],
        export_folder: str,
        resolution: str = "1080p",
        framerate: int = 30
    ) -> list[str]:
        """
        批量导出草稿

        Args:
            draft_names: 草稿名称列表
            export_folder: 导出文件夹
            resolution: 分辨率
            framerate: 帧率

        Returns:
            导出的视频文件路径列表

        Raises:
            BusinessException: 导出失败
        """
        try:
            log.info(f"开始批量导出 {len(draft_names)} 个草稿")

            # 确保导出文件夹存在
            os.makedirs(export_folder, exist_ok=True)

            exported_paths = []
            for draft_name in draft_names:
                export_path = os.path.join(export_folder, f"{draft_name}.mp4")
                result = await self.export_draft(
                    draft_name,
                    export_path,
                    resolution,
                    framerate
                )
                exported_paths.append(result)

            log.info(f"批量导出完成，共 {len(exported_paths)} 个视频")
            return exported_paths
        except Exception as e:
            log.error(f"批量导出失败：{str(e)}")
            raise BusinessException(message=f"批量导出失败：{str(e)}")


# 创建服务实例
export_service = ExportService()

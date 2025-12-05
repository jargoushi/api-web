"""
改进的导出服务 - 支持最小化窗口
"""
import sys
import os

PYJIANYING_PATH = os.path.join(os.path.dirname(__file__), "../../../pyJianYingDraft_source")
if PYJIANYING_PATH not in sys.path:
    sys.path.insert(0, PYJIANYING_PATH)

import pyJianYingDraft as draft
from pyJianYingDraft import ExportResolution, ExportFramerate
import win32gui
import win32con

from app.core.config import settings
from app.core.logging import log
from app.core.exceptions import BusinessException


class MinimizedExportService:
    """
    改进的视频导出服务 - 支持最小化窗口

    注意：需要安装 pywin32
    pip install pywin32
    """

    def __init__(self):
        """初始化服务"""
        self.controller = None
        self.hwnd = None

    def _minimize_window(self):
        """最小化剪映窗口"""
        try:
            # 查找剪映窗口句柄
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "剪映专业版" in title:
                        hwnds.append(hwnd)
                return True

            hwnds = []
            win32gui.EnumWindows(callback, hwnds)

            if hwnds:
                self.hwnd = hwnds[0]
                # 最小化窗口
                win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
                log.info("剪映窗口已最小化")
        except Exception as e:
            log.warning(f"最小化窗口失败：{e}")

    def _restore_window(self):
        """恢复剪映窗口"""
        try:
            if self.hwnd:
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                log.info("剪映窗口已恢复")
        except Exception as e:
            log.warning(f"恢复窗口失败：{e}")

    async def export_draft_minimized(
        self,
        draft_name: str,
        export_path: str,
        resolution: str = "1080p",
        framerate: int = 30
    ) -> str:
        """
        最小化导出草稿

        导出过程中窗口会最小化，减少对用户的干扰
        """
        try:
            log.info(f"开始导出草稿（最小化模式）：{draft_name}")

            # 初始化控制器
            if not self.controller:
                self.controller = draft.JianyingController()

            # 最小化窗口
            self._minimize_window()

            # 转换参数
            resolution_map = {
                "720p": ExportResolution.RES_720P,
                "1080p": ExportResolution.RES_1080P,
                "2k": ExportResolution.RES_2K,
                "4k": ExportResolution.RES_4K
            }

            framerate_map = {
                24: ExportFramerate.FR_24,
                30: ExportFramerate.FR_30,
                60: ExportFramerate.FR_60
            }

            # 调用原始导出方法
            self.controller.export_draft(
                draft_name,
                export_path,
                resolution=resolution_map.get(resolution),
                framerate=framerate_map.get(framerate)
            )

            log.info(f"草稿 {draft_name} 导出成功：{export_path}")
            return export_path

        except Exception as e:
            log.error(f"导出草稿失败：{str(e)}")
            raise BusinessException(message=f"导出草稿失败：{str(e)}")
        finally:
            # 恢复窗口
            self._restore_window()


# 创建服务实例
minimized_export_service = MinimizedExportService()

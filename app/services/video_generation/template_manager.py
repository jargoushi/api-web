import sys
import os
from typing import List, Dict, Any, Optional

# 将 pyJianYingDraft 源码路径添加到 sys.path
PYJIANYING_PATH = os.path.join(os.path.dirname(__file__), "../../../pyJianYingDraft_source")
if PYJIANYING_PATH not in sys.path:
    sys.path.insert(0, PYJIANYING_PATH)

import pyJianYingDraft as draft

from app.core.config import settings
from app.core.logging import log
from app.core.exceptions import BusinessException


class TemplateManager:
    """
    模板管理服务

    负责管理剪映草稿模板，包括加载、替换素材等
    """

    def __init__(self):
        """初始化服务"""
        self.draft_folder_path = getattr(settings, 'JIANYING_DRAFT_FOLDER', None)
        if not self.draft_folder_path:
            log.warning("未配置剪映草稿文件夹路径，模板功能将不可用")
        self.draft_folder = None

    def _ensure_draft_folder(self):
        """确保草稿文件夹已初始化"""
        if not self.draft_folder_path:
            raise BusinessException(message="未配置剪映草稿文件夹路径")

        if not self.draft_folder:
            self.draft_folder = draft.DraftFolder(self.draft_folder_path)

        return self.draft_folder

    async def load_template(self, template_name: str) -> Any:
        """
        加载模板草稿

        Args:
            template_name: 模板名称

        Returns:
            模板草稿对象

        Raises:
            BusinessException: 加载失败
        """
        try:
            log.info(f"加载模板：{template_name}")
            folder = self._ensure_draft_folder()
            script = folder.load_template(template_name)
            log.info(f"模板 {template_name} 加载成功")
            return script
        except Exception as e:
            log.error(f"加载模板失败：{str(e)}")
            raise BusinessException(message=f"加载模板失败：{str(e)}")

    async def duplicate_template(
        self,
        template_name: str,
        new_name: str
    ) -> Any:
        """
        复制模板创建新草稿

        Args:
            template_name: 模板名称
            new_name: 新草稿名称

        Returns:
            新草稿对象

        Raises:
            BusinessException: 复制失败
        """
        try:
            log.info(f"复制模板 {template_name} 为 {new_name}")
            folder = self._ensure_draft_folder()
            script = folder.duplicate_as_template(template_name, new_name)
            log.info(f"模板复制成功")
            return script
        except Exception as e:
            log.error(f"复制模板失败：{str(e)}")
            raise BusinessException(message=f"复制模板失败：{str(e)}")

    async def replace_material_by_name(
        self,
        script: Any,
        old_material_name: str,
        new_material_path: str,
        material_type: str = "video"
    ) -> None:
        """
        根据名称替换素材

        Args:
            script: 草稿对象
            old_material_name: 原素材名称
            new_material_path: 新素材路径
            material_type: 素材类型（video/audio/image）

        Raises:
            BusinessException: 替换失败
        """
        try:
            log.info(f"替换素材：{old_material_name} -> {new_material_path}")

            # 创建新素材
            if material_type == "video":
                new_material = draft.VideoMaterial(new_material_path)
            elif material_type == "audio":
                new_material = draft.AudioMaterial(new_material_path)
            elif material_type == "image":
                new_material = draft.VideoMaterial(new_material_path)  # 图片也用VideoMaterial
            else:
                raise BusinessException(message=f"不支持的素材类型：{material_type}")

            # 替换素材
            script.replace_material_by_name(old_material_name, new_material)

            log.info(f"素材替换成功")
        except Exception as e:
            log.error(f"替换素材失败：{str(e)}")
            raise BusinessException(message=f"替换素材失败：{str(e)}")

    async def replace_text(
        self,
        script: Any,
        track_name: str,
        segment_index: int,
        new_text: str
    ) -> None:
        """
        替换文本片段内容

        Args:
            script: 草稿对象
            track_name: 轨道名称
            segment_index: 片段索引
            new_text: 新文本内容

        Raises:
            BusinessException: 替换失败
        """
        try:
            log.info(f"替换文本：轨道 {track_name}，索引 {segment_index}")

            # 获取文本轨道
            text_track = script.get_imported_track(
                draft.TrackType.text,
                name=track_name
            )

            # 替换文本
            script.replace_text(text_track, segment_index, new_text)

            log.info(f"文本替换成功")
        except Exception as e:
            log.error(f"替换文本失败：{str(e)}")
            raise BusinessException(message=f"替换文本失败：{str(e)}")

    async def inspect_material(
        self,
        template_name: str
    ) -> Dict[str, Any]:
        """
        提取模板素材元数据

        Args:
            template_name: 模板名称

        Returns:
            素材元数据字典

        Raises:
            BusinessException: 提取失败
        """
        try:
            log.info(f"提取模板素材元数据：{template_name}")
            folder = self._ensure_draft_folder()

            # 这里需要捕获 inspect_material 的输出
            # 由于它直接打印，我们需要重定向输出
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                folder.inspect_material(template_name)

            output = f.getvalue()
            log.info(f"素材元数据提取成功")

            return {"output": output}
        except Exception as e:
            log.error(f"提取素材元数据失败：{str(e)}")
            raise BusinessException(message=f"提取素材元数据失败：{str(e)}")

    async def import_track(
        self,
        source_script: Any,
        target_script: Any,
        track_type: str,
        track_index: int = 0,
        offset: Optional[int] = None,
        new_name: Optional[str] = None
    ) -> None:
        """
        从源草稿导入轨道到目标草稿

        Args:
            source_script: 源草稿对象
            target_script: 目标草稿对象
            track_type: 轨道类型
            track_index: 轨道索引
            offset: 时间偏移（微秒）
            new_name: 新轨道名称

        Raises:
            BusinessException: 导入失败
        """
        try:
            log.info(f"导入轨道：类型 {track_type}，索引 {track_index}")

            # 转换轨道类型
            track_type_enum = getattr(draft.TrackType, track_type)

            # 获取源轨道
            source_track = source_script.get_imported_track(
                track_type_enum,
                index=track_index
            )

            # 导入轨道
            if offset is None:
                offset = target_script.duration

            target_script.import_track(
                source_script,
                source_track,
                offset=offset,
                new_name=new_name
            )

            log.info(f"轨道导入成功")
        except Exception as e:
            log.error(f"导入轨道失败：{str(e)}")
            raise BusinessException(message=f"导入轨道失败：{str(e)}")


# 创建服务实例
template_manager = TemplateManager()

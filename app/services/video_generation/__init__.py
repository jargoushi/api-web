"""
视频生成服务模块

基于剪映实现自动化视频生成
"""
from app.services.video_generation.draft_service import draft_service
from app.services.video_generation.template_manager import template_manager
from app.services.video_generation.material_manager import material_manager
from app.services.video_generation.export_service import export_service

__all__ = [
    "draft_service",
    "template_manager",
    "material_manager",
    "export_service",
]

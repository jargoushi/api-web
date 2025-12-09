"""
运镜计算服务 - 计算关键帧参数
"""
import sys
from pathlib import Path

# 添加 pyJianYingDraft 到路径
project_root = Path(__file__).parent.parent.parent.parent
pyjy_path = project_root / "pyJianYingDraft_source"
if str(pyjy_path) not in sys.path:
    sys.path.insert(0, str(pyjy_path))

from pyJianYingDraft.keyframe import KeyframeList, KeyframeProperty
from .models import Bounds, Point, CameraParams


class CameraCalculator:
    """运镜计算器"""

    def __init__(self, canvas_width: int, canvas_height: int):
        """
        初始化计算器

        Args:
            canvas_width: 画布宽度（像素）
            canvas_height: 画布高度（像素）
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.canvas_center = Point(canvas_width / 2, canvas_height / 2)

    def calculate_camera_params(
        self,
        target_bounds: Bounds,
        padding: float = 0.15
    ) -> CameraParams:
        """
        计算运镜参数，使目标区域适配画布

        Args:
            target_bounds: 目标区域边界（地理坐标）
            padding: 边距比例（0-1），默认 0.15 表示留 15% 的边距

        Returns:
            运镜参数（缩放和位置）
        """
        # 计算目标区域的宽高
        target_width = target_bounds.width
        target_height = target_bounds.height

        # 计算缩放比例（考虑边距）
        scale_x = (self.canvas_width * (1 - padding * 2)) / target_width
        scale_y = (self.canvas_height * (1 - padding * 2)) / target_height

        # 使用较小的缩放比例，保持比例不变形
        scale = min(scale_x, scale_y)

        # 计算目标中心点
        target_center = target_bounds.center

        # 计算位置偏移
        # 剪映坐标系：以画布中心为原点，单位为半个画布宽/高
        # 正值表示向右/向上移动

        # 这里需要将地理坐标转换为像素坐标
        # 简化处理：假设地理坐标已经是像素坐标（由 matplotlib 处理）
        # 实际使用时，需要根据底图的坐标系进行转换

        # 由于我们使用的是相对缩放，位置偏移设为 0
        # 运镜效果主要通过缩放实现
        position_x = 0.0
        position_y = 0.0

        return CameraParams(
            scale=scale,
            position_x=position_x,
            position_y=position_y
        )

    def create_transition_keyframes(
        self,
        start_time: int,
        end_time: int,
        from_params: CameraParams,
        to_params: CameraParams
    ) -> list:
        """
        创建过渡关键帧（从一个状态平滑过渡到另一个状态）

        Args:
            start_time: 开始时间（微秒）
            end_time: 结束时间（微秒）
            from_params: 起始运镜参数
            to_params: 目标运镜参数

        Returns:
            关键帧列表
        """
        keyframe_lists = []

        # 缩放关键帧
        kf_scale = KeyframeList(KeyframeProperty.uniform_scale)
        kf_scale.add_keyframe(start_time, from_params.scale)
        kf_scale.add_keyframe(end_time, to_params.scale)
        keyframe_lists.append(kf_scale)

        # X 轴位置关键帧
        if from_params.position_x != to_params.position_x:
            kf_pos_x = KeyframeList(KeyframeProperty.position_x)
            kf_pos_x.add_keyframe(start_time, from_params.position_x)
            kf_pos_x.add_keyframe(end_time, to_params.position_x)
            keyframe_lists.append(kf_pos_x)

        # Y 轴位置关键帧
        if from_params.position_y != to_params.position_y:
            kf_pos_y = KeyframeList(KeyframeProperty.position_y)
            kf_pos_y.add_keyframe(start_time, from_params.position_y)
            kf_pos_y.add_keyframe(end_time, to_params.position_y)
            keyframe_lists.append(kf_pos_y)

        return keyframe_lists

    def calculate_province_view(self, province_bounds: Bounds) -> CameraParams:
        """
        计算省份全景视图参数

        Args:
            province_bounds: 省份边界

        Returns:
            运镜参数
        """
        return self.calculate_camera_params(province_bounds, padding=0.1)

    def calculate_city_view(self, city_bounds: Bounds) -> CameraParams:
        """
        计算城市特写视图参数

        Args:
            city_bounds: 城市边界

        Returns:
            运镜参数
        """
        return self.calculate_camera_params(city_bounds, padding=0.2)

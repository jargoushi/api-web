from tortoise import fields

from app.models.base import BaseModel


class MonitorDailyStats(BaseModel):
    """监控每日数据明细模型"""
    config_id = fields.IntField(description="关联配置ID")
    stat_date = fields.DateField(description="统计日期")
    follower_count = fields.IntField(default=0, description="粉丝数")
    liked_count = fields.IntField(default=0, description="获赞/收藏数")
    view_count = fields.BigIntField(default=0, description="总播放/阅读量")
    content_count = fields.IntField(default=0, description="发布内容数量")
    extra_data = fields.JSONField(null=True, description="渠道特有数据")

    class Meta:
        table = "monitor_daily_stats"
        ordering = ["-stat_date"]

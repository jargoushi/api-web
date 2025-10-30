# 统一时间处理工具模块
from datetime import datetime, timezone
from typing import Optional


def get_utc_now() -> datetime:
    """
    获取当前UTC时间（naive格式，兼容TortoiseORM）

    Returns:
        datetime: 当前UTC时间（naive格式，无时区信息）
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def utc_to_iso(dt: datetime) -> str:
    """
    将datetime转换为ISO格式字符串

    Args:
        dt (datetime): datetime对象

    Returns:
        str: ISO格式时间字符串
    """
    if dt.tzinfo is None:
        # 如果是naive datetime，假设为UTC时间
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat()


def iso_to_utc(iso_str: str) -> datetime:
    """
    将ISO格式字符串转换为UTC datetime（naive格式）

    Args:
        iso_str (str): ISO格式时间字符串

    Returns:
        datetime: UTC时间（naive格式）
    """
    dt = datetime.fromisoformat(iso_str)

    if dt.tzinfo is not None:
        # 转换为UTC并移除时区信息
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt


def parse_datetime(dt_str: str) -> datetime:
    """
    解析时间字符串为datetime对象

    Args:
        dt_str (str): 时间字符串

    Returns:
        datetime: 解析后的datetime对象
    """
    try:
        # 尝试解析ISO格式
        return iso_to_utc(dt_str)
    except ValueError:
        # 如果不是ISO格式，尝试其他格式
        from dateutil.parser import parse
        dt = parse(dt_str)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化datetime为字符串

    Args:
        dt (datetime): datetime对象
        fmt (str): 格式化字符串

    Returns:
        str: 格式化后的时间字符串
    """
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt.strftime(fmt)


def add_utc_timedelta(dt: datetime, **kwargs) -> datetime:
    """
    为UTC时间添加时间间隔

    Args:
        dt (datetime): 基础时间
        **kwargs: timedelta参数（days, hours, minutes, seconds等）

    Returns:
        datetime: 新的时间
    """
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    from datetime import timedelta
    return dt + timedelta(**kwargs)


def is_expired(expire_time: Optional[datetime], reference_time: Optional[datetime] = None) -> bool:
    """
    检查时间是否已过期

    Args:
        expire_time (Optional[datetime]): 过期时间
        reference_time (Optional[datetime]): 参考时间，默认为当前时间

    Returns:
        bool: 是否已过期
    """
    if expire_time is None:
        return False

    if reference_time is None:
        reference_time = get_utc_now()

    # 确保两个时间都是naive UTC时间
    if expire_time.tzinfo is not None:
        expire_time = expire_time.astimezone(timezone.utc).replace(tzinfo=None)

    if reference_time.tzinfo is not None:
        reference_time = reference_time.astimezone(timezone.utc).replace(tzinfo=None)

    return reference_time > expire_time


def normalize_datetime(dt: datetime) -> datetime:
    """
    标准化datetime对象为naive UTC时间

    Args:
        dt (datetime): 输入时间

    Returns:
        datetime: 标准化后的naive UTC时间
    """
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

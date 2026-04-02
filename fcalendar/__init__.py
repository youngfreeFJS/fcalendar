"""fcalendar package - Chinese date/time expression recognition and holiday query tool.

fcalendar 包 - 中文日期时间表达式识别与节假日查询工具。
"""

__version__ = "0.12.0"

from fcalendar.core import annotate_time_expressions, get_holidays

def query(text: str, today=None, lang=None):
    """Query and annotate time expressions in text.
    
    查询并标注文本中的时间表达式。
    
    Supports automatic detection and recognition of both Chinese and English.
    支持中英文自动检测和识别。
    
    Args:
        text: 要标注的文本 / Text to be annotated
        today: 参考日期，默认为当前日期 / Reference date, defaults to current date
        lang: 语言代码，'zh' 表示中文，'en' 表示英文。如果为 None，则自动检测
              Language code, 'zh' for Chinese, 'en' for English. If None, auto-detect
        
    Returns:
        标注后的文本 / Annotated text
        
    Examples:
        >>> query("明天开会")
        '明天开会（今天是2026 年 3 月 25 日，明天是2026 年 3 月 26 日）'
        
        >>> query("meeting tomorrow")
        'meeting tomorrow (Today is March 25, 2026, tomorrow is March 26, 2026)'
    """
    return annotate_time_expressions(text, today, lang)

def holiday(scope: str = "half_year", today=None):
    """查询指定时间范围内的中国法定节假日信息
    
    Args:
        scope: 查询范围，支持以下格式：
            - "half_year"（默认）：未来 180 天
            - "this_week"：本周（周一至周日）
            - "next_week"：下周（周一至周日）
            - "next_month"：下个月（第一天至最后一天）
            - "weeks=N"：从今天起未来 N 周（N 为正整数）
            - "months=N"：从今天起未来 N 个月（N 为正整数）
        today: 参考日期，默认为当前日期
        
    Returns:
        节假日列表，按起始日期升序排列，每条记录包含：
            - name (str)  ：假期中文名称，如 "春节"、"国庆节"
            - start (str) ：起始日期，ISO 格式（YYYY-MM-DD）
            - end (str)   ：结束日期，ISO 格式（YYYY-MM-DD）
            - days (int)  ：假期天数
        
    Examples:
        >>> holiday()
        [{'name': '劳动节', 'start': '2026-05-01', 'end': '2026-05-05', 'days': 5}, ...]
        
        >>> holiday("this_week")
        []
        
        >>> holiday("next_month")
        [{'name': '劳动节', 'start': '2026-05-01', 'end': '2026-05-05', 'days': 5}]
        
        >>> holiday("weeks=3")
        []
        
        >>> holiday("months=2")
        [{'name': '劳动节', 'start': '2026-05-01', 'end': '2026-05-05', 'days': 5}]
    """
    return get_holidays(scope, today)

def hello() -> str:
    """Return a greeting message.
    
    返回问候语。
    
    Returns:
        str: Greeting message / 问候语
    """
    return "Hello from fcalendar!"

__all__ = ['query', 'holiday', 'get_holidays', 'hello', '__version__']

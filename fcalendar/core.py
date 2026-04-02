# -*- coding: utf-8 -*-

"""
fcalendar Core Module
v0.11.0

Provides Chinese time expression recognition and annotation, supporting:
- Relative time (tomorrow, next week, next month, etc.)
- Chinese public holidays
- Lunar dates and traditional festivals
- Western holidays
- 24 Solar Terms
- Seasons and annual cycles
- Specific dates

fcalendar 核心功能模块
v0.11.0

提供中文时间表达式的识别和标注功能，支持：
- 相对时间（明天、下周、下个月等）
- 中国法定节假日
- 农历日期和传统节日
- 西方节日
- 二十四节气
- 季节和年度周期
- 具体日期
"""

import calendar as cal_mod
import datetime
import math
import re
from dataclasses import dataclass
from typing import Optional
from zoneinfo import ZoneInfo

from chinese_calendar import get_holiday_detail
from lunardate import LunarDate

# Mapping from chinese_calendar holiday English names to Chinese keywords
# chinese_calendar 假期英文名 -> 中文关键词的映射
HOLIDAY_EN_TO_CN = {
    "New Year's Day": "元旦",
    "Spring Festival": "春节",
    "Tomb-sweeping Day": "清明节",
    "Labour Day": "劳动节",
    "Dragon Boat Festival": "端午节",
    "Mid-autumn Festival": "中秋节",
    "National Day": "国庆节",
}

# Reverse mapping from Chinese keywords to English names (used for matching festivals in text)
# 中文关键词 -> 英文名的反向映射（用于从文本中匹配节日）
HOLIDAY_CN_TO_EN = {cn: en for en, cn in HOLIDAY_EN_TO_CN.items()}

# Chinese weekday characters -> weekday index (0=Monday)
# 中文星期数字 -> weekday index (0=周一)
WEEKDAY_CN_MAP = {
    "一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6,
}

# Chinese lunar month names -> numeric month
# 农历月份中文 -> 数字
LUNAR_MONTH_CN_MAP = {
    "正": 1, "整": 1, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
    "七": 7, "八": 8, "九": 9, "十": 10, "冬": 11, "十一": 11, "腊": 12, "十二": 12,
}

# Chinese lunar day names -> numeric day
# 农历日期中文 -> 数字
LUNAR_DAY_CN_MAP = {
    "初一": 1, "初二": 2, "初三": 3, "初四": 4, "初五": 5,
    "初六": 6, "初七": 7, "初八": 8, "初九": 9, "初十": 10,
    "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
    "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20,
    "二十一": 21, "二十二": 22, "二十三": 23, "二十四": 24, "二十五": 25,
    "二十六": 26, "二十七": 27, "二十八": 28, "二十九": 29, "三十": 30,
}

# Lunar traditional festival names -> (lunar month, lunar day) mapping
# 农历传统节日名称 -> (农历月, 农历日) 的映射
LUNAR_FESTIVAL_MAP: dict[str, tuple[int, int]] = {
    "元宵节": (1, 15),
    "元宵": (1, 15),
    "龙抬头": (2, 2),
    "上巳节": (3, 3),
    "七夕": (7, 7),
    "七夕节": (7, 7),
    "中元节": (7, 15),
    "重阳节": (9, 9),
    "重阳": (9, 9),
    "寒衣节": (10, 1),
    "下元节": (10, 15),
    "小年": (12, 23),
    "除夕": (12, 30),
}

# Western/international festival names -> (Gregorian month, day) mapping
# 西方/国际节日名称 -> (公历月, 公历日) 的映射
WESTERN_FESTIVAL_MAP: dict[str, tuple[int, int]] = {
    "万圣节": (10, 31),
    "平安夜": (12, 24),
    "圣诞节": (12, 25),
    "圣诞": (12, 25),
    "情人节": (2, 14),
    "愚人节": (4, 1),
    "母亲节": (5, 12),
    "父亲节": (6, 15),
    "儿童节": (6, 1),
    "妇女节": (3, 8),
    "三八节": (3, 8),
    "植树节": (3, 12),
    "教师节": (9, 10),
    "护士节": (5, 12),
    "独立日": (7, 4),
    "美国独立日": (7, 4),
}

# List of religious festival names (dates require dynamic calculation)
# 宗教节日名称列表（日期需要动态计算）
RELIGIOUS_FESTIVAL_NAMES = ["复活节", "斋月"]

# Annual cycle names -> (start month, end month) mapping
# 年度周期 -> (起始月, 结束月) 的映射
ANNUAL_CYCLE_MAP: dict[str, tuple[int, int]] = {
    "Q1": (1, 3), "Q2": (4, 6), "Q3": (7, 9), "Q4": (10, 12),
    "q1": (1, 3), "q2": (4, 6), "q3": (7, 9), "q4": (10, 12),
    "S1": (1, 6), "S2": (7, 12),
    "s1": (1, 6), "s2": (7, 12),
    "上半年": (1, 6), "下半年": (7, 12),
}

# Chinese numeric month names -> integer (for Gregorian month matching)
# 中文数字月份 -> 数字（用于公历月份匹配）
CN_MONTH_NUM_MAP: dict[str, int] = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
    "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12,
}

# Season names -> (start month, start day, end month, end day) mapping (meteorological division)
# 季节名称 -> (起始月, 起始日, 结束月, 结束日) 的映射（气象学划分）
SEASON_MAP: dict[str, tuple[int, int, int, int]] = {
    "春季": (3, 1, 5, 31),
    "春天": (3, 1, 5, 31),
    "夏季": (6, 1, 8, 31),
    "夏天": (6, 1, 8, 31),
    "秋季": (9, 1, 11, 30),
    "秋天": (9, 1, 11, 30),
    "冬季": (12, 1, 2, 28),
    "冬天": (12, 1, 2, 28),
}

# 24 Solar Terms -> (term index, Gregorian month) mapping
# 二十四节气名称 -> (节气序号, 所在公历月) 的映射
# Term index: 0=Minor Cold, 1=Major Cold, 2=Start of Spring, ... (counted from the first term in January)
# 节气序号：0=小寒,1=大寒,2=立春,...（从1月第一个节气开始计数）
# Note: Qingming (4,5) is excluded here because "Tomb-sweeping Day" is handled as a public holiday
# 注意：清明(4,5)不在此表中，因为"清明节"已在法定假期中处理
SOLAR_TERM_MAP: dict[str, tuple[int, int]] = {
    "小寒": (0, 1), "大寒": (1, 1),
    "立春": (2, 2), "雨水": (3, 2),
    "惊蛰": (4, 3), "春分": (5, 3),
    "谷雨": (7, 4),
    "立夏": (8, 5), "小满": (9, 5),
    "芒种": (10, 6), "夏至": (11, 6),
    "小暑": (12, 7), "大暑": (13, 7),
    "立秋": (14, 8), "处暑": (15, 8),
    "白露": (16, 9), "秋分": (17, 9),
    "寒露": (18, 10), "霜降": (19, 10),
    "立冬": (20, 11), "小雪": (21, 11),
    "大雪": (22, 12), "冬至": (23, 12),
}

# Fallback date table for 24 Solar Terms (used when the astronomical algorithm fails)
# 二十四节气兜底日期表（当天文算法失败时使用）
SOLAR_TERM_FALLBACK: dict[str, tuple[int, int]] = {
    "小寒": (1, 6), "大寒": (1, 20),
    "立春": (2, 4), "雨水": (2, 19),
    "惊蛰": (3, 6), "春分": (3, 20),
    "谷雨": (4, 20),
    "立夏": (5, 6), "小满": (5, 21),
    "芒种": (6, 6), "夏至": (6, 21),
    "小暑": (7, 7), "大暑": (7, 23),
    "立秋": (8, 7), "处暑": (8, 23),
    "白露": (9, 8), "秋分": (9, 23),
    "寒露": (10, 8), "霜降": (10, 23),
    "立冬": (11, 7), "小雪": (11, 22),
    "大雪": (12, 7), "冬至": (12, 22),
}

def _compute_solar_term_date(term_name: str, year: int) -> datetime.date:
    """
    Calculate the exact Gregorian date of a 24 Solar Term for a given year
    using the astronomical algorithm from the Shouxing Perpetual Calendar.

    The algorithm is based on solar longitude; each term corresponds to a
    multiple of 15 degrees of solar longitude:
      Minor Cold=285°, Major Cold=300°, Start of Spring=315°, ..., Winter Solstice=270°

    Precision: error within ±1 day, far better than the fixed average method (±2 days).

    Args:
        term_name: Chinese name of the solar term, e.g., "春分", "冬至"
        year: Gregorian year

    Returns:
        Exact Gregorian date of the solar term in the given year

    Raises:
        ValueError: When term_name is not in the known solar term list

    使用寿星万年历天文算法精确计算指定年份的二十四节气日期。

    算法基于太阳黄经，每个节气对应太阳黄经的整数倍（15度间隔）：
      小寒=285°, 大寒=300°, 立春=315°, ..., 冬至=270°

    精度：误差在 ±1 天以内，远优于固定平均值方法（±2 天）。

    Args:
        term_name: 节气中文名称，如 "春分"、"冬至"
        year: 公历年份

    Returns:
        该节气在指定年份的精确公历日期

    Raises:
        ValueError: 当 term_name 不在已知节气列表中时
    """
    if term_name not in SOLAR_TERM_MAP:
        raise ValueError(f"未知节气: {term_name}")

    # Solar longitude (degrees) for each term, starting from Minor Cold, every 15 degrees
    # 各节气对应的太阳黄经（度）：从小寒开始，每15度一个节气
    # Minor Cold 285, Major Cold 300, Start of Spring 315, Rain Water 330, Awakening of Insects 345, Spring Equinox 0,
    # 小寒285, 大寒300, 立春315, 雨水330, 惊蛰345, 春分0,
    # Clear and Bright 15, Grain Rain 30, Start of Summer 45, Grain Buds 60, Grain in Ear 75, Summer Solstice 90,
    # 清明15, 谷雨30, 立夏45, 小满60, 芒种75, 夏至90,
    # Minor Heat 105, Major Heat 120, Start of Autumn 135, End of Heat 150, White Dew 165, Autumnal Equinox 180,
    # 小暑105, 大暑120, 立秋135, 处暑150, 白露165, 秋分180,
    # Cold Dew 195, Frost's Descent 210, Start of Winter 225, Minor Snow 240, Major Snow 255, Winter Solstice 270
    # 寒露195, 霜降210, 立冬225, 小雪240, 大雪255, 冬至270
    term_longitude_map: dict[str, float] = {
        "小寒": 285.0, "大寒": 300.0,
        "立春": 315.0, "雨水": 330.0,
        "惊蛰": 345.0, "春分": 0.0,
        "谷雨": 30.0,
        "立夏": 45.0, "小满": 60.0,
        "芒种": 75.0, "夏至": 90.0,
        "小暑": 105.0, "大暑": 120.0,
        "立秋": 135.0, "处暑": 150.0,
        "白露": 165.0, "秋分": 180.0,
        "寒露": 195.0, "霜降": 210.0,
        "立冬": 225.0, "小雪": 240.0,
        "大雪": 255.0, "冬至": 270.0,
    }

    target_longitude = term_longitude_map[term_name]
    _, approx_month = SOLAR_TERM_MAP[term_name]

    # Use fallback date as initial estimate to prevent iteration divergence
    # 以兜底日期为初始估计值，避免迭代发散
    fallback_day = SOLAR_TERM_FALLBACK[term_name][1]
    try:
        t0 = datetime.date(year, approx_month, fallback_day)
    except ValueError:
        t0 = datetime.date(year, approx_month, 15)

    # Convert date to Julian Day Number (JDN)
    # 将日期转换为儒略日数（Julian Day Number）
    def to_jdn(d: datetime.date) -> float:
        y, m, day = d.year, d.month, d.day
        a = (14 - m) // 12
        y2 = y + 4800 - a
        m2 = m + 12 * a - 3
        return day + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045

    # Calculate solar longitude (low precision, ±0.5°, sufficient for ±1 day accuracy on solar terms)
    # 计算太阳黄经（低精度，±0.5度，满足节气日期±1天的需求）
    def sun_longitude(jdn: float) -> float:
        # Simplified astronomical algorithm (VSOP87 low-precision version)
        # 简化天文算法（VSOP87 低精度版）
        T = (jdn - 2451545.0) / 36525.0  # Julian centuries from J2000.0 / J2000.0 起算的儒略世纪数
        # Mean solar longitude (degrees)
        # 太阳平黄经（度）
        L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
        # Mean anomaly of the Sun (degrees)
        # 太阳平近点角（度）
        M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
        M_rad = math.radians(M % 360)
        # Equation of center (degrees)
        # 中心差（度）
        C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
        C += (0.019993 - 0.000101 * T) * math.sin(2 * M_rad)
        C += 0.000289 * math.sin(3 * M_rad)
        # True solar longitude
        # 太阳真黄经
        sun_lon = (L0 + C) % 360
        return sun_lon

    # Binary search to find the exact date of the solar term (precision: fractional Julian day, i.e., minute-level)
    # 二分法迭代求节气精确日期（精度：儒略日小数，即分钟级）
    # Search range: ±3 days around the fallback date
    # 搜索范围：兜底日期前后 3 天
    # JDN noon = integer, so JDN epoch starts at UTC 12:00
    # JDN 中正午=整数，所以 JDN 的起始时刻是 UTC 中午 12:00
    jdn0 = to_jdn(t0)
    # Center the search on the UTC noon of t0, ±3 days
    # 以 t0 所在 UTC 正午为中心，搜索前后 ±3 天
    low, high = jdn0 - 3.0, jdn0 + 3.0

    target = target_longitude

    def angle_diff(a: float, b: float) -> float:
        """Calculate the angular difference, result in the range (-180, 180].

        For the Spring Equinox (target longitude 0°): solar longitude increases from 359.x to 0.x,
        requiring special handling for the wrap-around at 0°.

        计算角度差，结果在 (-180, 180] 范围内。

        对于春分（目标黄经 0°）：太阳黄经从 359.x 增加到 0.x，
        需要特殊处理跨 0° 的情况。
        """
        d = (a - b) % 360
        if d > 180:
            d -= 360
        return d

    # Binary search: find jdn where sun_longitude(jdn) == target (second-level precision)
    # 二分搜索：找到 sun_longitude(jdn) == target 的 jdn（精度到秒级）
    for _ in range(60):
        mid = (low + high) / 2
        lon_mid = sun_longitude(mid)
        diff = angle_diff(lon_mid, target)
        if abs(diff) < 1e-6:
            break
        if diff < 0:
            low = mid
        else:
            high = mid

    result_jdn_utc = (low + high) / 2  # UTC Julian day (with fraction) / UTC 儒略日（含小数）

    # Convert to Beijing time (UTC+8): add 8/24 days
    # 转换到北京时间（UTC+8）：加 8/24 天
    # The Beijing time date when the solar term occurs is what we display to the user
    # 节气发生时刻的北京时间日期才是我们要展示给用户的日期
    result_jdn_cst = result_jdn_utc + 8.0 / 24.0

    # Round Julian day: JDN starts at UTC 12:00, so the calendar date
    # 儒略日取整：JDN 从 UTC 中午 12:00 开始，因此对应的日历日期
    # corresponds to floor(jdn + 0.5) in the Gregorian calendar
    # 是 floor(jdn + 0.5) 对应的格里历日期
    jdn_int = int(math.floor(result_jdn_cst + 0.5))
    # JDN -> Gregorian calendar date conversion
    # JDN -> 公历日期转换（格里历）
    a = jdn_int + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    y = 100 * b + d - 4800 + m // 10

    try:
        result = datetime.date(y, month, day)
        # Verify the year is correct (prevent year shift at boundary cases)
        # 验证年份是否正确（防止边界情况下年份偏移）
        if result.year != year:
            # Fall back to the default value when year shifts
            # 年份偏移时回退到兜底值
            fallback_m, fallback_d = SOLAR_TERM_FALLBACK[term_name]
            result = datetime.date(year, fallback_m, fallback_d)
        return result
    except ValueError:
        # Fallback: use fixed average date
        # 兜底：使用固定平均值
        fallback_m, fallback_d = SOLAR_TERM_FALLBACK[term_name]
        return datetime.date(year, fallback_m, fallback_d)

# ============ English Time Expression Mappings (Internationalization Support) ============
# ============ 英文时间表达式映射（国际化支持）============

# English weekday names -> weekday index (0=Monday)
# 英文星期映射 -> weekday index (0=Monday)
EN_WEEKDAY_MAP = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

# English relative time keywords -> day offset (positive=future, negative=past)
# 英文相对时间关键词 -> 天数偏移（正数=未来，负数=过去）
EN_RELATIVE_TIME_MAP = {
    "day before yesterday": -2,
    "yesterday": -1,
    "today": 0,
    "tomorrow": 1,
    "day after tomorrow": 2,
    "next week": 7,
    "last week": "last_week",   # Special marker: last week (Mon-Sun) / 特殊标记：上周（周一到周日）
    "last month": "last_month", # Special marker: last month (first to last day) / 特殊标记：上个月（第一天到最后一天）
    "next month": "month",      # Special marker: next month (first to last day) / 特殊标记：下个月（第一天到最后一天）
}

# English festival names -> (Gregorian month, day)
# 英文节日映射 -> (公历月, 公历日)
EN_FESTIVAL_MAP: dict[str, tuple[int, int]] = {
    "new year's day": (1, 1),
    "new year": (1, 1),
    "valentine's day": (2, 14),
    "valentine": (2, 14),
    "april fools' day": (4, 1),
    "april fools": (4, 1),
    "independence day": (7, 4),
    "halloween": (10, 31),
    "christmas eve": (12, 24),
    "christmas day": (12, 25),
    "christmas": (12, 25),
}

# English month names -> numeric month
# 英文月份名称 -> 数字
EN_MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

@dataclass
class TimeAnnotation:
    """A time annotation result: matched text from the original + corresponding specific date description.
    一个时间标注结果：原文中的匹配文本 + 对应的具体日期描述。
    """
    original_text: str
    start_pos: int
    end_pos: int
    date_label: str


# ============ Language Detection Function ============
# ============ 语言检测函数 ============

def _detect_language(text: str) -> str:
    """
    Detect the language of the text, returning 'zh' or 'en'.

    Determines language by checking for Chinese characters:
    - Contains Chinese characters → 'zh' (Chinese)
    - No Chinese characters → 'en' (English)

    Args:
        text: The text to detect

    Returns:
        'zh' or 'en'

    检测文本语言，返回 'zh' 或 'en'。

    通过检测文本中是否包含中文字符来判断语言：
    - 如果包含中文字符 → 'zh'（中文）
    - 如果不包含中文字符 → 'en'（英文）

    Args:
        text: 要检测的文本

    Returns:
        'zh' 或 'en'
    """
    # Chinese character range: U+4E00 to U+9FFF (CJK Unified Ideographs)
    # 中文字符范围：U+4E00 到 U+9FFF（CJK统一汉字）
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    return 'en'

def _get_beijing_time(reference_date: Optional[datetime.date] = None) -> datetime.datetime:
    """Get the current Beijing time.

    Args:
        reference_date: Optional reference date. If provided, returns 00:00:00 of that date (for testing);
                        otherwise returns the real-time Beijing time.

    获取当前北京时间。

    Args:
        reference_date: 可选的参考日期。如果提供，返回该日期的 00:00:00（用于测试）；
                       否则返回实时的北京时间。
    """
    if reference_date is not None:
        # Test mode: return 00:00:00 of the reference date
        # 测试模式：返回参考日期的 00:00:00
        return datetime.datetime.combine(
            reference_date,
            datetime.time(0, 0, 0),
            tzinfo=ZoneInfo('Asia/Shanghai')
        )
    # Production mode: return real-time Beijing time
    # 生产模式：返回实时北京时间
    return datetime.datetime.now(ZoneInfo('Asia/Shanghai'))

def _format_datetime(dt: datetime.datetime, lang: str = 'zh') -> str:
    """
    Format a datetime object into a localized string.

    Args:
        dt: The datetime object
        lang: Language code, 'zh' for Chinese, 'en' for English

    Returns:
        Formatted datetime string

    格式化日期时间。

    Args:
        dt: 日期时间对象
        lang: 语言代码，'zh' 表示中文，'en' 表示英文

    Returns:
        格式化后的日期时间字符串
    """
    if lang == 'zh':
        return f"北京时间 {dt.year} 年 {dt.month} 月 {dt.day} 日 {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    else:  # en
        month_name = dt.strftime("%B")
        return f"Beijing time {month_name} {dt.day}, {dt.year} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"

def format_date(date: datetime.date, lang: str = 'zh') -> str:
    """
    Format a date object into a localized string.

    Args:
        date: The date object
        lang: Language code, 'zh' for Chinese, 'en' for English

    Returns:
        Formatted date string

    格式化日期。

    Args:
        date: 日期对象
        lang: 语言代码，'zh' 表示中文，'en' 表示英文

    Returns:
        格式化后的日期字符串
    """
    if lang == 'zh':
        return f"{date.year} 年 {date.month} 月 {date.day} 日"
    else:  # en
        # Use %-d to remove leading zero from day (Unix/Mac); Windows uses %#d
        # 使用 %-d 移除日期的前导零（Unix/Mac），Windows 使用 %#d
        month_name = date.strftime("%B")
        return f"{month_name} {date.day}, {date.year}"

def format_date_range(start: datetime.date, end: datetime.date, lang: str = 'zh') -> str:
    """
    Format a date range into a localized string.

    Args:
        start: Start date
        end: End date
        lang: Language code, 'zh' for Chinese, 'en' for English

    Returns:
        Formatted date range string

    格式化日期范围。

    Args:
        start: 起始日期
        end: 结束日期
        lang: 语言代码，'zh' 表示中文，'en' 表示英文

    Returns:
        格式化后的日期范围字符串
    """
    if lang == 'zh':
        return f"{format_date(start, lang)}-{format_date(end, lang)}"
    else:  # en
        return f"{format_date(start, lang)} - {format_date(end, lang)}"

def _find_holiday_date_range(
    holiday_en_name: str, reference_date: datetime.date
) -> Optional[tuple[datetime.date, datetime.date]]:
    """
    Find the consecutive date range of a holiday by its English name,
    searching in the year of reference_date (and the next year).
    Returns (start_date, end_date) or None.

    根据假期英文名，在 reference_date 所在年份（及下一年）中查找该假期的连续日期范围。
    返回 (start_date, end_date) 或 None。
    """
    search_years = [reference_date.year]
    # If current date is in the second half of the year, also search next year
    # (e.g., asking about "Spring Festival" in December should find next year's)
    # 如果当前日期在下半年，也搜索下一年（比如12月问"春节"应该找下一年的）
    if reference_date.month >= 6:
        search_years.append(reference_date.year + 1)
    # If current date is in the first half of the year, also search current year
    # (e.g., asking about "National Day" in March should find the current year's)
    # 如果当前日期在上半年，也搜索当年（比如3月问"国庆"应该找当年的）
    # Current year is already included by default
    # 默认已包含当年

    for year in search_years:
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)

        holiday_dates = []
        current = start_date
        while current <= end_date:
            try:
                on_holiday, name = get_holiday_detail(current)
                if on_holiday and name is not None:
                    name_str = name if isinstance(name, str) else str(name)
                    if name_str == holiday_en_name:
                        holiday_dates.append(current)
            except Exception:
                pass
            current += datetime.timedelta(days=1)

        if holiday_dates:
            # Found consecutive holiday segments; take the nearest one (>= reference_date, or the last one)
            # 找到连续的假期段（取最近的一段，即 >= reference_date 的，或最后一段）
            segments = _group_consecutive_dates(holiday_dates)
            # Prefer returning the segment that is >= reference_date
            # 优先返回 >= reference_date 的段
            for segment in segments:
                if segment[-1] >= reference_date:
                    return segment[0], segment[-1]
            # If all segments are in the past, return the last one
            # 如果都在过去，返回最后一段
            if segments:
                last_segment = segments[-1]
                return last_segment[0], last_segment[-1]

    return None

def _group_consecutive_dates(
    dates: list[datetime.date],
) -> list[list[datetime.date]]:
    """Group a list of dates into consecutive segments.
    将日期列表按连续性分组。
    """
    if not dates:
        return []
    sorted_dates = sorted(dates)
    segments: list[list[datetime.date]] = [[sorted_dates[0]]]
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            segments[-1].append(sorted_dates[i])
        else:
            segments.append([sorted_dates[i]])
    return segments

def _resolve_relative_weekday(
    week_offset: int, weekday_index: int, today: datetime.date
) -> datetime.date:
    """
    Resolve a relative weekday to a concrete date.
    week_offset: 0 = this week, 1 = next week, 2 = the week after, and so on
    weekday_index: 0-6 (Monday to Sunday)

    When week_offset == 0 and the target weekday has already passed,
    return the date from next week (forward-looking logic, consistent with festival queries).

    解析相对星期为具体日期。
    week_offset: 0 表示本周，1 表示下周，2 表示下下周，以此类推
    weekday_index: 0-6 (周一到周日)

    当 week_offset == 0 且目标星期已过时，返回下周的日期（向前看逻辑，与节日查询保持一致）
    """
    today_weekday = today.weekday()
    if week_offset == 0:
        # This week / current week
        # 这周/本周
        days_diff = weekday_index - today_weekday
        # Forward-looking logic: if the target weekday has passed, return next week's date
        # 向前看逻辑：如果目标星期已过，返回下周
        if days_diff < 0:
            days_diff += 7
        return today + datetime.timedelta(days=days_diff)
    else:
        # Next N weeks: jump to next Monday, then add (week_offset - 1) * 7 days, then add weekday_index
        # 下N周：先跳到下周一，再加 (week_offset - 1) * 7 天，再加 weekday_index
        next_monday = today + datetime.timedelta(days=(7 - today_weekday))
        return next_monday + datetime.timedelta(days=(week_offset - 1) * 7 + weekday_index)

def _resolve_relative_weekend(
    week_offset: int, today: datetime.date
) -> tuple[datetime.date, datetime.date]:
    """Resolve a relative weekend to Saturday-Sunday.
    week_offset: 0=this weekend, 1=next weekend, 2=weekend after next...
    解析相对周末为周六-周日。week_offset: 0=本周末, 1=下周末, 2=下下周末...
    """
    saturday = _resolve_relative_weekday(week_offset, 5, today)
    sunday = saturday + datetime.timedelta(days=1)
    return saturday, sunday

def _resolve_lunar_date(
    lunar_month: int,
    lunar_day: int,
    reference_date: datetime.date,
    target_year: Optional[int] = None,
) -> datetime.date:
    """
    Convert a lunar month and day to a Gregorian date.
    target_year: when specified, use that year directly without the "if passed, use next year" logic.

    将农历月日转换为公历日期。
    target_year: 指定年份时直接使用该年份，不做"已过则取下一年"的推算。
    """
    if target_year is not None:
        return LunarDate(target_year, lunar_month, lunar_day).toSolarDate()
    solar_date = LunarDate(reference_date.year, lunar_month, lunar_day).toSolarDate()
    if solar_date < reference_date:
        solar_date = LunarDate(reference_date.year + 1, lunar_month, lunar_day).toSolarDate()
    return solar_date

def _build_lunar_date_pattern() -> str:
    """Build a regex pattern to match lunar dates, e.g., '正月十五', '腊月二十三', '八月初一'.

    Maintains the original two capture group structure (group N = month, group N+1 = day),
    but filters false matches after matching via _is_valid_lunar_date_match(),
    to avoid misidentifying ordinary Gregorian Chinese dates (e.g., "三月十八号") as lunar dates.

    构建匹配农历日期的正则表达式，如 '正月十五'、'腊月二十三'、'八月初一'。

    保持原有的两个捕获组结构（group N = 月份，group N+1 = 日期），
    但通过 _is_valid_lunar_date_match() 在匹配后过滤误匹配，
    避免将普通公历中文日期（如"三月十八号"）误识别为农历。
    """
    month_alternatives = "|".join(
        re.escape(m) for m in sorted(LUNAR_MONTH_CN_MAP.keys(), key=len, reverse=True)
    )
    day_alternatives = "|".join(
        re.escape(d) for d in sorted(LUNAR_DAY_CN_MAP.keys(), key=len, reverse=True)
    )
    return rf"({month_alternatives})月({day_alternatives})"


# Exclusive lunar month names: these words are only used for the lunar calendar
# and won't be confused with Gregorian months
# 农历专有月份名：这些词本身就只用于农历，不会与公历月份混淆
EXCLUSIVE_LUNAR_MONTH_NAMES = {"正", "整", "冬", "腊"}


def _is_valid_lunar_date_match(month_cn: str, day_cn: str) -> bool:
    """
    Determine whether a Chinese month-day combination should be recognized as a lunar date,
    used to filter false matches.

    Rules:
    - If the month is an exclusive lunar name (正, 整, 冬, 腊), any lunar day is valid.
    - If the month is an ordinary Chinese numeral (一~十二), the day must be in "初X" format
      (lunar-specific notation) to be recognized as lunar; otherwise treated as an ordinary
      Gregorian Chinese date (e.g., "三月十八") and not annotated.

    判断一个中文月日组合是否应当被识别为农历日期，用于过滤误匹配。

    规则：
    - 若月份是农历专有名称（正、整、冬、腊），则任意农历日期均有效。
    - 若月份是普通中文数字（一~十二），则日期必须是"初X"格式（农历特有写法），
      才认定为农历；否则视为普通公历中文日期（如"三月十八"），不予标注。
    """
    if month_cn in EXCLUSIVE_LUNAR_MONTH_NAMES:
        return True
    return day_cn.startswith("初")

LUNAR_DATE_PATTERN = _build_lunar_date_pattern()

def _compute_easter(year: int) -> datetime.date:
    """
    Calculate the Easter date using the Anonymous Gregorian algorithm.
    Easter = the first Sunday after the first full moon after the Spring Equinox.

    使用匿名公历算法（Anonymous Gregorian algorithm）计算复活节日期。
    复活节 = 春分后第一个满月之后的第一个周日。
    """
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_val = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_val) // 451
    month = (h + l_val - 7 * m + 114) // 31
    day = ((h + l_val - 7 * m + 114) % 31) + 1
    return datetime.date(year, month, day)

def _compute_ramadan_start(year: int) -> datetime.date:
    """
    Calculate the Gregorian start date of the Islamic month of Ramadan.
    Uses a lookup table for 2020-2030; uses an approximate algorithm for years outside this range.

    计算伊斯兰历斋月（Ramadan）在公历中的起始日期。
    使用查表法覆盖 2020-2030 年，超出范围则用近似算法推算。
    """
    # Known Ramadan start dates (based on astronomical observation data)
    # 已知斋月起始日期（基于天文观测数据）
    ramadan_table: dict[int, tuple[int, int]] = {
        2020: (4, 24),
        2021: (4, 13),
        2022: (4, 2),
        2023: (3, 23),
        2024: (3, 12),
        2025: (3, 1),
        2026: (2, 18),
        2027: (2, 8),
        2028: (1, 28),
        2029: (1, 16),
        2030: (1, 6),
    }
    if year in ramadan_table:
        month, day = ramadan_table[year]
        return datetime.date(year, month, day)
    # Use approximate algorithm when out of table range: advances ~10.876 days per year
    # 超出查表范围时用近似算法：每年提前约 10.876 天
    anchor_date = datetime.date(2024, 3, 12)
    year_diff = year - 2024
    drift_per_year = 10.876
    total_drift_days = year_diff * drift_per_year
    result = anchor_date - datetime.timedelta(days=round(total_drift_days))
    if result.year != year:
        if result.year < year:
            result = result.replace(year=year)
        else:
            result = result.replace(year=year)
    return result

def _compute_thanksgiving(year: int) -> datetime.date:
    """Calculate the US Thanksgiving date: the 4th Thursday of November.
    计算美国感恩节日期：11 月第 4 个周四。
    """
    november_first = datetime.date(year, 11, 1)
    first_weekday = november_first.weekday()
    # 第一个周四
    first_thursday = november_first + datetime.timedelta(
        days=(3 - first_weekday) % 7
    )
    # 第四个周四
    return first_thursday + datetime.timedelta(weeks=3)

# Year prefix regex: matches "last year", "year before last", "this year", "next year", "2015年", etc.
# 年份前缀正则：匹配 "去年"、"前年"、"大前年"、"今年"、"明年"、"后年"、"2015年" 等
YEAR_PREFIX_PATTERN = r"(?:去年|前年|大前年|今年|明年|后年|\d{4}年)"

def _resolve_year_prefix(prefix: Optional[str], today: datetime.date) -> Optional[int]:
    """
    Parse a year prefix string into a concrete year number.
    Returns None to indicate no year prefix (use the default auto-inference logic).

    将年份前缀解析为具体年份数字。
    返回 None 表示无年份前缀（使用默认的自动推算逻辑）。
    """
    if not prefix:
        return None
    year_map: dict[str, int] = {
        "今年": today.year,
        "去年": today.year - 1,
        "前年": today.year - 2,
        "大前年": today.year - 3,
        "明年": today.year + 1,
        "后年": today.year + 2,
    }
    if prefix in year_map:
        return year_map[prefix]
    # Match numeric year strings like "2015年"
    # 匹配 "2015年" 这类数字年份
    digit_match = re.match(r"(\d{4})年", prefix)
    if digit_match:
        return int(digit_match.group(1))
    return None

def _find_holiday_date_range_for_year(
    holiday_en_name: str, year: int
) -> Optional[tuple[datetime.date, datetime.date]]:
    """Find the consecutive date range of a holiday in the specified year.
    在指定年份中查找某个假期的连续日期范围。
    """
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)

    holiday_dates: list[datetime.date] = []
    current = start_date
    while current <= end_date:
        try:
            on_holiday, name = get_holiday_detail(current)
            if on_holiday and name is not None:
                name_str = name if isinstance(name, str) else str(name)
                if name_str == holiday_en_name:
                    holiday_dates.append(current)
        except Exception:
            pass
        current += datetime.timedelta(days=1)

    if holiday_dates:
        segments = _group_consecutive_dates(holiday_dates)
        if segments:
            return segments[0][0], segments[0][-1]
    return None

def _count_prefix_weeks(prefix: str) -> int:
    """
    Count the number of "下" characters in the prefix as the week offset.
    "这"/"本" -> 0, "下" -> 1, "下下" -> 2, "下下下" -> 3, ...

    计算前缀中"下"的个数作为周偏移量。
    "这"/"本" -> 0, "下" -> 1, "下下" -> 2, "下下下" -> 3, ...
    """
    if prefix in ("这", "本"):
        return 0
    count: int = prefix.count("下")
    return count

def _count_da_prefix(prefix: str) -> int:
    """
    Count the number of "大" characters in the prefix,
    used to calculate the day offset for "后天" (day after tomorrow).
    "" -> 0 (day after tomorrow = 2 days)
    "大" -> 1 (3 days later)
    "大大" -> 2 (4 days later)
    ...

    计算前缀中"大"的个数，用于计算"后天"的天数偏移。
    "" -> 0 (后天 = 2天)
    "大" -> 1 (大后天 = 3天)
    "大大" -> 2 (大大后天 = 4天)
    ...
    """
    return prefix.count("大")


# ============ English Time Expression Recognition Functions ============
# ============ 英文时间表达式识别函数 ============

def _annotate_english(
    text: str, today: datetime.date
) -> list[TimeAnnotation]:
    """
    Recognize time expressions in English text and return a list of annotations.

    Supported expressions:
    - Relative time: today, tomorrow, day after tomorrow, next week, next month
    - Weekdays: Monday, Tuesday, next Monday, this weekend
    - Festivals: Christmas, Halloween, Valentine's Day, etc.
    - Specific dates: January 15, 2026, July 15th

    识别英文文本中的时间表达式，返回标注列表。

    支持的表达式：
    - 相对时间：today, tomorrow, day after tomorrow, next week, next month
    - 星期：Monday, Tuesday, next Monday, this weekend
    - 节日：Christmas, Halloween, Valentine's Day 等
    - 具体日期：January 15, 2026, July 15th
    """
    annotations: list[TimeAnnotation] = []
    text_lower = text.lower()

    # 1. Match relative time keywords (today, tomorrow, day after tomorrow, next week)
    # 1. 匹配相对时间关键词（today, tomorrow, day after tomorrow, next week）
    for keyword, offset in EN_RELATIVE_TIME_MAP.items():
        pattern = r'\b' + re.escape(keyword) + r'\b'
        for match in re.finditer(pattern, text_lower):
            if offset == "month":
                # Special handling for "next month"
                # next month 特殊处理
                target_month = today.month + 1
                target_year = today.year
                if target_month > 12:
                    target_month = 1
                    target_year += 1
                month_start = datetime.date(target_year, target_month, 1)
                last_day = cal_mod.monthrange(target_year, target_month)[1]
                month_end = datetime.date(target_year, target_month, last_day)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date_range(month_start, month_end, 'en'),
                ))
            elif offset == "last_week":
                # last week: from last Monday to last Sunday
                # last week：上周一到上周日
                this_monday = today - datetime.timedelta(days=today.weekday())
                last_monday = this_monday - datetime.timedelta(days=7)
                last_sunday = last_monday + datetime.timedelta(days=6)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date_range(last_monday, last_sunday, 'en'),
                ))
            elif offset == "last_month":
                # last month: from the first to the last day of last month
                # last month：上个月第一天到最后一天
                if today.month == 1:
                    lm_year, lm_month = today.year - 1, 12
                else:
                    lm_year, lm_month = today.year, today.month - 1
                lm_start = datetime.date(lm_year, lm_month, 1)
                lm_last = cal_mod.monthrange(lm_year, lm_month)[1]
                lm_end = datetime.date(lm_year, lm_month, lm_last)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date_range(lm_start, lm_end, 'en'),
                ))
            else:
                target = today + datetime.timedelta(days=offset)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(target, 'en'),
                ))

    # 2. Match weekdays (Monday, Tuesday, next Monday, last Monday, this weekend)
    # 2. 匹配星期（Monday, Tuesday, next Monday, last Monday, this weekend）
    for weekday_name, weekday_index in EN_WEEKDAY_MAP.items():
        # Match "last weekday" (a specific day of last week)
        # 匹配 "last weekday"（上周某天）
        pattern = r'\blast\s+' + re.escape(weekday_name) + r'\b'
        for match in re.finditer(pattern, text_lower):
            if not any(a.start_pos <= match.start() < a.end_pos for a in annotations):
                # Target day of last week: go back to last Monday then add offset
                # 上周对应的星期：退到上周一再加偏移
                this_monday = today - datetime.timedelta(days=today.weekday())
                last_monday = this_monday - datetime.timedelta(days=7)
                target = last_monday + datetime.timedelta(days=weekday_index)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(target, 'en'),
                ))

        # Match "next weekday"
        # 匹配 "next weekday"
        pattern = r'\bnext\s+' + re.escape(weekday_name) + r'\b'
        for match in re.finditer(pattern, text_lower):
            if not any(a.start_pos <= match.start() < a.end_pos for a in annotations):
                target = _resolve_relative_weekday(1, weekday_index, today)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(target, 'en'),
                ))

        # Match standalone "weekday" (defaults to current week)
        # 匹配单独的 "weekday"（默认本周）
        pattern = r'\b' + re.escape(weekday_name) + r'\b(?!\s*\d)'
        for match in re.finditer(pattern, text_lower):
            # Avoid duplicate matching (if already matched by "last/next Monday")
            # 避免重复匹配（如果已经被 "last/next Monday" 匹配过）
            if not any(a.start_pos <= match.start() < a.end_pos for a in annotations):
                target = _resolve_relative_weekday(0, weekday_index, today)
                annotations.append(TimeAnnotation(
                    original_text=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(target, 'en'),
                ))

    # 3. Match "this weekend" and "next weekend"
    # 3. 匹配 "this weekend" 和 "next weekend"
    # "this weekend" -> current weekend (week_offset=0)
    # "this weekend" -> 本周末 (week_offset=0)
    # "next weekend" -> next weekend (week_offset=1)
    # "next weekend" -> 下周末 (week_offset=1)
    for match in re.finditer(r'\b(this|next)\s+weekend\b', text_lower):
        prefix = match.group(1)
        week_offset = 0 if prefix == "this" else 1
        saturday, sunday = _resolve_relative_weekend(week_offset, today)
        annotations.append(TimeAnnotation(
            original_text=text[match.start():match.end()],
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(saturday, sunday, 'en'),
        ))

    # 4. Match festivals (Christmas, Halloween, Valentine's Day, etc.)
    # 4. 匹配节日（Christmas, Halloween, Valentine's Day 等）
    for festival_name, (month, day) in EN_FESTIVAL_MAP.items():
        pattern = r'\b' + re.escape(festival_name) + r'\b'
        for match in re.finditer(pattern, text_lower):
            target_date = datetime.date(today.year, month, day)
            if target_date < today:
                target_date = datetime.date(today.year + 1, month, day)
            annotations.append(TimeAnnotation(
                original_text=text[match.start():match.end()],
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date(target_date, 'en'),
            ))

    # 5. Match specific dates (January 15, 2026 or July 15th or Jan 15)
    # 5. 匹配具体日期（January 15, 2026 或 July 15th 或 Jan 15）
    # Format 1: "January 15, 2026" or "Jan 15, 2026"
    # 格式1: "January 15, 2026" 或 "Jan 15, 2026"
    for month_name, month_num in EN_MONTH_MAP.items():
        # With year: January 15, 2026
        # 带年份：January 15, 2026
        pattern = r'\b' + re.escape(month_name) + r'\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b'
        for match in re.finditer(pattern, text_lower, re.IGNORECASE):
            day_num = int(match.group(1))
            year_num = int(match.group(2))
            if 1 <= day_num <= 31:
                try:
                    target_date = datetime.date(year_num, month_num, day_num)
                    annotations.append(TimeAnnotation(
                        original_text=text[match.start():match.end()],
                        start_pos=match.start(),
                        end_pos=match.end(),
                        date_label=format_date(target_date, 'en'),
                    ))
                except ValueError:
                    pass

        # Without year: January 15 or Jan 15th
        # 不带年份：January 15 或 Jan 15th
        pattern = r'\b' + re.escape(month_name) + r'\s+(\d{1,2})(?:st|nd|rd|th)?\b(?!,?\s*\d{4})'
        for match in re.finditer(pattern, text_lower, re.IGNORECASE):
            day_num = int(match.group(1))
            if 1 <= day_num <= 31:
                try:
                    target_date = datetime.date(today.year, month_num, day_num)
                    if target_date < today:
                        target_date = datetime.date(today.year + 1, month_num, day_num)
                    annotations.append(TimeAnnotation(
                        original_text=text[match.start():match.end()],
                        start_pos=match.start(),
                        end_pos=match.end(),
                        date_label=format_date(target_date, 'en'),
                    ))
                except ValueError:
                    pass

    return annotations


def annotate_time_expressions(
    text: str, today: Optional[datetime.date] = None, lang: Optional[str] = None
) -> str:
    """
    Recognize vague time/holiday/festival semantics in text and annotate with specific dates in brackets.
    Supports automatic detection and recognition of both Chinese and English.

    Args:
        text: The text to recognize
        today: Reference date (defaults to today)
        lang: Language code, 'zh' for Chinese, 'en' for English. If None, auto-detected.

    Returns:
        Annotated text in the format: original text (context information)

    识别文本中的模糊时间/假期/节日语义，在原文中用括号标注具体日期。
    支持中英文自动检测和识别。

    Args:
        text: 要识别的文本
        today: 参考日期（默认为今天）
        lang: 语言代码，'zh' 表示中文，'en' 表示英文。如果为 None，则自动检测

    Returns:
        标注后的文本，格式为：原文（上下文信息）
    """
    # Save the original today parameter to determine if we are in test mode
    # 保存原始的 today 参数，用于判断是否为测试模式
    is_mock_mode = today is not None

    if today is None:
        today = datetime.date.today()

    # Auto-detect language
    # 自动检测语言
    if lang is None:
        lang = _detect_language(text)

    # Choose recognition logic based on detected language
    # 根据语言选择不同的识别逻辑
    if lang == 'en':
        # English recognition
        # 英文识别
        annotations = _annotate_english(text, today)
    else:
        # Chinese recognition (keep original logic)
        # 中文识别（保持原有逻辑）
        annotations: list[TimeAnnotation] = []

        # 0. Match current time keywords
        # 0. 匹配当前时间关键词
        current_time_keywords = r"当前时间|现在|当前|目前|此时|此刻|眼下|当下|这会儿|这时候|今天"
        for match in re.finditer(current_time_keywords, text):
            keyword = match.group()
            # Only pass the today parameter in test mode (when the user explicitly provides it)
            # 只有在测试模式（用户明确传入 today）时才传入 today 参数
            beijing_time = _get_beijing_time(today if is_mock_mode else None)
            annotations.append(TimeAnnotation(
                original_text=keyword,
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=_format_datetime(beijing_time, lang),
            ))

    # 0.5. Match Chinese past time expressions
    # (yesterday, day before yesterday, last week X, last weekend, last month, etc.)
    # 0.5. 匹配中文过去时间（昨天、前天、大前天、上周X、上周末、上个月、上上个月等）
    # yesterday = -1 day, day before yesterday = -2 days, two days before yesterday = -3 days
    # 昨天 = -1天，前天 = -2天，大前天 = -3天
    for match in re.finditer(r"(大+)?前天|昨天", text):
        keyword = match.group()
        if keyword == "昨天":
            target = today - datetime.timedelta(days=1)
        else:
            # Day before yesterday or multiple days before
            # 前天或大...前天
            da_prefix = match.group(1) if match.group(1) else ""
            da_count = da_prefix.count("大")
            days_offset = 2 + da_count  # 前天=2, 大前天=3, 大大前天=4, ...
            target = today - datetime.timedelta(days=days_offset)
        annotations.append(TimeAnnotation(
            original_text=keyword,
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date(target),
        ))

    # Last week weekday (last Monday ~ last Sunday)
    # 上周X（上周一~上周日）
    for match in re.finditer(r"上+周([一二三四五六日天])", text):
        weekday_cn = match.group(1)
        weekday_index = WEEKDAY_CN_MAP[weekday_cn]
        # Count the number of "上" characters as the backward week offset
        # 计算"上"的个数作为向过去的周偏移
        prefix_text = match.group(0)
        shang_count = prefix_text.count("上")
        # Go back to this Monday, then go back shang_count weeks, then add weekday_index
        # 退到本周一，再退 shang_count 周，再加 weekday_index
        this_monday = today - datetime.timedelta(days=today.weekday())
        target_monday = this_monday - datetime.timedelta(weeks=shang_count)
        target = target_monday + datetime.timedelta(days=weekday_index)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date(target),
        ))

    # Last weekend (last Saturday to last Sunday)
    # 上周末（上周六-上周日）
    for match in re.finditer(r"上+周末", text):
        prefix_text = match.group(0)
        shang_count = prefix_text.count("上")
        this_monday = today - datetime.timedelta(days=today.weekday())
        target_monday = this_monday - datetime.timedelta(weeks=shang_count)
        saturday = target_monday + datetime.timedelta(days=5)
        sunday = target_monday + datetime.timedelta(days=6)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(saturday, sunday),
        ))

    # Last N months (last month, month before last, etc., supports multiple "上" stacking)
    # 上...个月（上个月、上上个月等，支持多个"上"叠加）
    for match in re.finditer(r"(上+)个月", text):
        shang_count = match.group(1).count("上")
        # Go back shang_count months
        # 退 shang_count 个月
        target_month = today.month - shang_count
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        lm_start = datetime.date(target_year, target_month, 1)
        lm_last = cal_mod.monthrange(target_year, target_month)[1]
        lm_end = datetime.date(target_year, target_month, lm_last)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(lm_start, lm_end),
        ))

    # 1. Match "tomorrow", "day after tomorrow", "大...后天" (supports multiple "大" stacking)
    # 1. 匹配 "明天"、"后天"、"大...后天"（支持多个"大"叠加）
    for match in re.finditer(r"明天|(大+)?后天", text):
        keyword = match.group()
        if keyword == "明天":
            target = today + datetime.timedelta(days=1)
        else:
            # Day after tomorrow or multiple days after
            # 后天或大...后天
            da_prefix = match.group(1) if match.group(1) else ""
            da_count = _count_da_prefix(da_prefix)
            days_offset = 2 + da_count  # 后天=2, 大后天=3, 大大后天=4, ...
            target = today + datetime.timedelta(days=days_offset)
        annotations.append(TimeAnnotation(
            original_text=keyword,
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date(target),
        ))

    # 2. Match "下下...周X", "这周X", "本周X" (supports multiple "下" stacking)
    # 2. 匹配 "下下...周X"、"这周X"、"本周X"（支持多个"下"叠加）
    for match in re.finditer(r"(下+|这|本)周([一二三四五六日天])", text):
        prefix = match.group(1)
        weekday_cn = match.group(2)
        weekday_index = WEEKDAY_CN_MAP[weekday_cn]
        week_offset = _count_prefix_weeks(prefix)
        target = _resolve_relative_weekday(week_offset, weekday_index, today)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=f"{target.month} 月 {target.day} 日",
        ))

    # 3. Match "下下...周末", "这周末", "本周末" (supports multiple "下" stacking)
    # 3. 匹配 "下下...周末"、"这周末"、"本周末"（支持多个"下"叠加）
    for match in re.finditer(r"(下+|这|本)周末", text):
        prefix = match.group(1)
        week_offset = _count_prefix_weeks(prefix)
        saturday, sunday = _resolve_relative_weekend(week_offset, today)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(saturday, sunday),
        ))

    # 4. Match Chinese holiday/festival names (supports year prefix: last year's National Day, Spring Festival 2015)
    # 4. 匹配中国节日/假期名称（支持年份前缀：去年国庆节、2015年春节）
    holiday_names = "|".join(re.escape(cn) for cn in HOLIDAY_CN_TO_EN.keys())
    holiday_with_year_pattern = rf"({YEAR_PREFIX_PATTERN})?({holiday_names})"
    for match in re.finditer(holiday_with_year_pattern, text):
        year_prefix = match.group(1)
        holiday_cn = match.group(2)
        holiday_en = HOLIDAY_CN_TO_EN[holiday_cn]
        target_year = _resolve_year_prefix(year_prefix, today)
        if target_year is not None:
            date_range = _find_holiday_date_range_for_year(holiday_en, target_year)
        else:
            date_range = _find_holiday_date_range(holiday_en, today)
        if date_range is not None:
            start, end = date_range
            annotations.append(TimeAnnotation(
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date_range(start, end),
            ))

    # 5. Match lunar traditional festival names (supports year prefix: last year's Lantern Festival, Qixi 2015)
    # 5. 匹配农历传统节日名称（支持年份前缀：去年元宵节、2015年七夕）
    lunar_festival_names = "|".join(
        re.escape(name) for name in sorted(LUNAR_FESTIVAL_MAP.keys(), key=len, reverse=True)
    )
    lunar_festival_with_year_pattern = rf"({YEAR_PREFIX_PATTERN})?({lunar_festival_names})"
    for match in re.finditer(lunar_festival_with_year_pattern, text):
        year_prefix = match.group(1)
        festival_name = match.group(2)
        lunar_month, lunar_day = LUNAR_FESTIVAL_MAP[festival_name]
        target_year = _resolve_year_prefix(year_prefix, today)
        try:
            solar_date = _resolve_lunar_date(lunar_month, lunar_day, today, target_year)
            annotations.append(TimeAnnotation(
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date(solar_date),
            ))
        except ValueError:
            pass

    # 6. Match lunar dates (supports year prefix:
    # last year's 15th of the 1st lunar month, 23rd of the 12th lunar month 2015)
    # 6. 匹配农历日期（支持年份前缀：去年正月十五、2015年腊月二十三）
    lunar_date_with_year_pattern = rf"({YEAR_PREFIX_PATTERN})?{LUNAR_DATE_PATTERN}"
    for match in re.finditer(lunar_date_with_year_pattern, text):
        year_prefix = match.group(1)
        month_cn = match.group(2)
        day_cn = match.group(3)
        lunar_month = LUNAR_MONTH_CN_MAP.get(month_cn)
        lunar_day = LUNAR_DAY_CN_MAP.get(day_cn)
        # Filter false matches: ordinary Chinese numeric month (e.g., "三月") + non-"初X" day (e.g., "十八")
        # 过滤误匹配：普通中文数字月份（如"三月"）+ 非"初X"日期（如"十八"）
        # These are Gregorian date expressions in Chinese and should not be recognized as lunar dates
        # 属于公历中文日期写法，不应识别为农历
        if lunar_month is not None and lunar_day is not None and _is_valid_lunar_date_match(month_cn, day_cn):
            target_year = _resolve_year_prefix(year_prefix, today)
            try:
                solar_date = _resolve_lunar_date(lunar_month, lunar_day, today, target_year)
                annotations.append(TimeAnnotation(
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(solar_date),
                ))
            except ValueError:
                pass

    # 7. Match Western/international festivals (supports year prefix: last year's Halloween, Christmas 2024)
    # 7. 匹配西方/国际节日（支持年份前缀：去年万圣节、2024年圣诞节）
    western_festival_names = "|".join(
        re.escape(name) for name in sorted(WESTERN_FESTIVAL_MAP.keys(), key=len, reverse=True)
    )
    western_festival_with_year_pattern = rf"({YEAR_PREFIX_PATTERN})?({western_festival_names})"
    for match in re.finditer(western_festival_with_year_pattern, text):
        year_prefix = match.group(1)
        festival_name = match.group(2)
        festival_month, festival_day = WESTERN_FESTIVAL_MAP[festival_name]
        target_year = _resolve_year_prefix(year_prefix, today)
        if target_year is not None:
            target_date = datetime.date(target_year, festival_month, festival_day)
        else:
            target_date = datetime.date(today.year, festival_month, festival_day)
            if target_date < today:
                target_date = datetime.date(today.year + 1, festival_month, festival_day)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date(target_date),
        ))

    # 8. Match seasons (supports year prefix: last year's winter, summer 2024)
    # 8. 匹配季节（支持年份前缀：去年冬季、2024年夏天）
    season_names = "|".join(re.escape(name) for name in SEASON_MAP.keys())
    season_with_year_pattern = rf"({YEAR_PREFIX_PATTERN})?({season_names})"
    for match in re.finditer(season_with_year_pattern, text):
        year_prefix = match.group(1)
        season_name = match.group(2)
        start_month, start_day, end_month, end_day = SEASON_MAP[season_name]
        target_year = _resolve_year_prefix(year_prefix, today)
        year = target_year if target_year is not None else today.year
        if end_month < start_month:
            # Winter spans two years: December 1 to February 28/29 of the next year
            # 冬季跨年：12月1日 - 次年2月28/29日
            season_start = datetime.date(year, start_month, start_day)
            feb_last = cal_mod.monthrange(year + 1, 2)[1]
            season_end = datetime.date(year + 1, end_month, feb_last)
        else:
            season_start = datetime.date(year, start_month, start_day)
            season_end = datetime.date(year, end_month, end_day)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(season_start, season_end),
        ))

    # 9. Match 24 Solar Terms (supports year prefix: last year's Spring Equinox, Winter Solstice 2024)
    # 9. 匹配二十四节气（支持年份前缀：去年春分、2024年冬至）
    solar_term_names = "|".join(
        re.escape(name) for name in sorted(SOLAR_TERM_MAP.keys(), key=len, reverse=True)
    )
    solar_term_with_year_pattern = rf"({YEAR_PREFIX_PATTERN})?({solar_term_names})"
    for match in re.finditer(solar_term_with_year_pattern, text):
        year_prefix = match.group(1)
        term_name = match.group(2)
        target_year = _resolve_year_prefix(year_prefix, today)
        if target_year is not None:
            target_date = _compute_solar_term_date(term_name, target_year)
        else:
            target_date = _compute_solar_term_date(term_name, today.year)
            if target_date < today:
                target_date = _compute_solar_term_date(term_name, today.year + 1)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date(target_date),
        ))

    # 10. Match "下...个月" (supports multiple "下" stacking)
    # 10. 匹配 "下...个月"（支持多个"下"叠加）
    for match in re.finditer(r"(下+)个月", text):
        prefix = match.group(1)
        month_offset = _count_prefix_weeks(prefix)  # Reuse function to count "下" occurrences / 复用函数计算"下"的个数

        # Calculate the target month
        # 计算目标月份
        target_month = today.month + month_offset
        target_year = today.year

        # Handle year-crossing cases
        # 处理跨年情况
        while target_month > 12:
            target_month -= 12
            target_year += 1

        # Calculate the start and end dates of the target month
        # 计算月份的起止日期
        month_start = datetime.date(target_year, target_month, 1)
        last_day = cal_mod.monthrange(target_year, target_month)[1]
        month_end = datetime.date(target_year, target_month, last_day)

        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(month_start, month_end),
        ))

    # 11. Match specific Gregorian dates (e.g., "7月15日", "2023年7月15日", "7月15号")
    # 11. 匹配具体公历日期（如 "7月15日"、"2023年7月15日"、"7月15号"）
    for match in re.finditer(r"(?:阳历)?(\d{4}年)?(\d{1,2})月(\d{1,2})[日号]", text):
        year_str = match.group(1)
        month_num = int(match.group(2))
        day_num = int(match.group(3))
        if 1 <= month_num <= 12 and 1 <= day_num <= 31:
            if year_str:
                year_num = int(year_str.rstrip("年"))
            else:
                year_num = today.year
            try:
                target_date = datetime.date(year_num, month_num, day_num)
                annotations.append(TimeAnnotation(
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(target_date),
                ))
            except ValueError:
                pass

    # 12. Match lunar/traditional calendar prefix + numeric date (e.g., "阴历8月15日", "农历3月21日")
    # 12. 匹配阴历/农历前缀 + 数字格式日期（如 "阴历8月15日"、"农历3月21日"）
    for match in re.finditer(r"(?:阴历|农历)(\d{1,2})月(\d{1,2})[日号]?", text):
        lunar_month_num = int(match.group(1))
        lunar_day_num = int(match.group(2))
        if 1 <= lunar_month_num <= 12 and 1 <= lunar_day_num <= 30:
            try:
                solar_date = _resolve_lunar_date(lunar_month_num, lunar_day_num, today)
                annotations.append(TimeAnnotation(
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(solar_date),
                ))
            except ValueError:
                pass

    # 12b. Match lunar prefix + Chinese month-day format (e.g., "农历三月十五", "阴历三月十八")
    # 12b. 匹配阴历/农历前缀 + 中文月日格式（如 "农历三月十五"、"阴历三月十八"）
    # When an explicit "农历"/"阴历" prefix is present,
    # any Chinese numeric month + Chinese day should be recognized as lunar
    # 有明确的"农历"/"阴历"前缀时，普通中文数字月份 + 任意中文日期均应识别为农历
    lunar_cn_with_prefix_pattern = rf"(?:阴历|农历){LUNAR_DATE_PATTERN}"
    for match in re.finditer(lunar_cn_with_prefix_pattern, text):
        month_cn = match.group(1)
        day_cn = match.group(2)
        lunar_month = LUNAR_MONTH_CN_MAP.get(month_cn)
        lunar_day = LUNAR_DAY_CN_MAP.get(day_cn)
        if lunar_month is not None and lunar_day is not None:
            try:
                solar_date = _resolve_lunar_date(lunar_month, lunar_day, today)
                annotations.append(TimeAnnotation(
                    original_text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    date_label=format_date(solar_date),
                ))
            except ValueError:
                pass

    # 13. Match unprefixed "周X" (e.g., "周三参观博物馆", defaults to current week)
    # 13. 匹配无前缀的 "周X"（如 "周三参观博物馆"，默认指本周）
    for match in re.finditer(r"(?<![下这本])周([一二三四五六日天])", text):
        weekday_cn = match.group(1)
        weekday_index = WEEKDAY_CN_MAP[weekday_cn]
        target = _resolve_relative_weekday(0, weekday_index, today)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date(target),
        ))

    # 14. Match standalone month expressions (e.g., "7月", "三月")
    # 14. 匹配单独的月份（如 "7月"、"三月"）
    for match in re.finditer(rf"(\d{{1,2}})月(?!\d)", text):
        month_num = int(match.group(1))
        if 1 <= month_num <= 12:
            year_num = today.year
            month_start = datetime.date(year_num, month_num, 1)
            last_day = cal_mod.monthrange(year_num, month_num)[1]
            month_end = datetime.date(year_num, month_num, last_day)
            annotations.append(TimeAnnotation(
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date_range(month_start, month_end),
            ))

    # 15. Match religious festivals (Easter, Ramadan, supports year prefix)
    # 15. 匹配宗教节日（复活节、斋月，支持年份前缀）
    for match in re.finditer(rf"({YEAR_PREFIX_PATTERN})?(复活节|斋月|感恩节)", text):
        year_prefix = match.group(1)
        festival_name = match.group(2)
        target_year = _resolve_year_prefix(year_prefix, today)
        year = target_year if target_year is not None else today.year
        if festival_name == "复活节":
            target_date = _compute_easter(year)
            if target_year is None and target_date < today:
                target_date = _compute_easter(year + 1)
            annotations.append(TimeAnnotation(
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date(target_date),
            ))
        elif festival_name == "感恩节":
            target_date = _compute_thanksgiving(year)
            if target_year is None and target_date < today:
                target_date = _compute_thanksgiving(year + 1)
            annotations.append(TimeAnnotation(
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date(target_date),
            ))
        elif festival_name == "斋月":
            ramadan_start = _compute_ramadan_start(year)
            ramadan_end = ramadan_start + datetime.timedelta(days=29)
            annotations.append(TimeAnnotation(
                original_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                date_label=format_date_range(ramadan_start, ramadan_end),
            ))

    # 16. Match annual cycles (Q1-Q4, S1-S2, first/second half of year, supports year prefix)
    # 16. 匹配年度周期（Q1-Q4、S1-S2、上半年、下半年，支持年份前缀）
    cycle_names = "|".join(
        re.escape(name) for name in sorted(ANNUAL_CYCLE_MAP.keys(), key=len, reverse=True)
    )
    for match in re.finditer(rf"({YEAR_PREFIX_PATTERN})?({cycle_names})", text):
        year_prefix = match.group(1)
        cycle_name = match.group(2)
        start_month, end_month = ANNUAL_CYCLE_MAP[cycle_name]
        target_year = _resolve_year_prefix(year_prefix, today)
        year = target_year if target_year is not None else today.year
        cycle_start = datetime.date(year, start_month, 1)
        last_day = cal_mod.monthrange(year, end_month)[1]
        cycle_end = datetime.date(year, end_month, last_day)
        annotations.append(TimeAnnotation(
            original_text=match.group(),
            start_pos=match.start(),
            end_pos=match.end(),
            date_label=format_date_range(cycle_start, cycle_end),
        ))

    if not annotations:
        return text

    # Deduplicate: if annotations overlap, keep the longer one (e.g., "下周末" takes priority over "下周")
    # 去重：如果有重叠的标注，保留更长的那个（如 "下周末" 优先于 "下周"）
    annotations = _remove_overlapping_annotations(annotations)

    # Build context information: append date info as context at the end of the sentence
    # 构建上下文信息：将日期信息作为上下文补充在句末
    today_label = format_date(today, lang)

    # Sort by position to maintain the order of time expressions in context
    # 按位置排序，保持时间表达式在上下文中的顺序
    annotations.sort(key=lambda a: a.start_pos)

    # Generate context in different formats based on language
    # 根据语言生成不同格式的上下文
    if lang == 'zh':
        context_parts = [f"今天是{today_label}"]
        for annotation in annotations:
            context_parts.append(f"{annotation.original_text}是{annotation.date_label}")
        context = "，".join(context_parts)
        return f"{text}（{context}）"
    else:  # en
        context_parts = [f"Today is {today_label}"]
        for annotation in annotations:
            context_parts.append(f"{annotation.original_text} is {annotation.date_label}")
        context = ", ".join(context_parts)
        return f"{text} ({context})"

def _remove_overlapping_annotations(
    annotations: list[TimeAnnotation],
) -> list[TimeAnnotation]:
    """Remove overlapping annotations, keeping the longer (more specific) one.
    移除重叠的标注，保留更长（更具体）的那个。
    """
    if not annotations:
        return []
    sorted_annotations = sorted(annotations, key=lambda a: (a.start_pos, -(a.end_pos - a.start_pos)))
    result: list[TimeAnnotation] = [sorted_annotations[0]]
    for annotation in sorted_annotations[1:]:
        last = result[-1]
        if annotation.start_pos >= last.end_pos:
            result.append(annotation)
        elif (annotation.end_pos - annotation.start_pos) > (last.end_pos - last.start_pos):
            result[-1] = annotation
    return result


# ============ Holiday Query Functions ============
# ============ 节假日查询函数 ============

def _normalize_cn_scope(scope: str) -> str:
    """
    Normalize a Chinese scope string to English scope format.

    Chinese numeral mapping (supports 一 to 十二):
      "一" -> 1, "两" -> 2, "二" -> 2, "三" -> 3, ..., "十二" -> 12

    Supported Chinese scope examples:
      "本周" / "这周"              -> "this_week"
      "下周" / "下一周"            -> "next_week"
      "下个月" / "下一个月" / "下月" -> "next_month"
      "半年" / "未来半年"          -> "half_year"
      "未来N周" / "N周"            -> "weeks=N"
      "未来N个月" / "N个月"        -> "months=N"

    将中文 scope 字符串标准化为英文 scope 格式。

    中文数字映射（支持一至十二）：
      "一" -> 1, "两" -> 2, "二" -> 2, "三" -> 3, ..., "十二" -> 12

    支持的中文 scope 示例：
      "本周" / "这周"              -> "this_week"
      "下周" / "下一周"            -> "next_week"
      "下个月" / "下一个月" / "下月" -> "next_month"
      "半年" / "未来半年"          -> "half_year"
      "未来N周" / "N周"            -> "weeks=N"
      "未来N个月" / "N个月"        -> "months=N"
    """
    # Chinese numerals -> Arabic numerals mapping
    # 中文数字 -> 阿拉伯数字映射
    CN_NUM_MAP = {
        "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12,
    }

    scope = scope.strip()

    # Fixed alias mapping
    # 固定别名映射
    FIXED_ALIAS: dict[str, str] = {
        "本周": "this_week",
        "这周": "this_week",
        "下周": "next_week",
        "下一周": "next_week",
        "下个月": "next_month",
        "下一个月": "next_month",
        "下月": "next_month",
        "半年": "half_year",
        "未来半年": "half_year",
        "本月": "this_month",
        "这个月": "this_month",
        "这月": "this_month",
        "当月": "this_month",
    }
    if scope in FIXED_ALIAS:
        return FIXED_ALIAS[scope]

    # "未来N周" / "N周" (N can be Chinese numeral or Arabic numeral)
    # "未来N周" / "N周"（N 可以是中文数字或阿拉伯数字）
    weeks_cn = re.fullmatch(r"(?:未来)?([一两二三四五六七八九十十一十二]+|\d+)周", scope)
    if weeks_cn:
        raw = weeks_cn.group(1)
        n = CN_NUM_MAP.get(raw, None)
        if n is None:
            n = int(raw)
        return f"weeks={n}"

    # "未来N个月" / "N个月" (N can be Chinese numeral or Arabic numeral)
    # "未来N个月" / "N个月"（N 可以是中文数字或阿拉伯数字）
    months_cn = re.fullmatch(r"(?:未来)?([一两二三四五六七八九十十一十二]+|\d+)个月", scope)
    if months_cn:
        raw = months_cn.group(1)
        n = CN_NUM_MAP.get(raw, None)
        if n is None:
            n = int(raw)
        return f"months={n}"

    # No conversion needed; return as-is (English format or invalid format handled downstream)
    # 无需转换，原样返回（英文格式或非法格式交给后续处理）
    return scope


def _resolve_holiday_scope(
    scope: str, today: datetime.date
) -> tuple[datetime.date, datetime.date]:
    """
    Parse a scope string into a (start_date, end_date) date range.

    Supports both Chinese and English scope formats:

    English formats:
      - "half_year"  : next 180 days from today (default)
      - "this_week"  : Monday to Sunday of the current week
      - "next_week"  : Monday to Sunday of next week
      - "next_month" : first to last day of next month
      - "weeks=N"    : next N weeks from today (N is a positive integer)
      - "months=N"   : next N months from today (N is a positive integer)

    Chinese formats:
      - "本周" / "这周"               : this week
      - "下周" / "下一周"              : next week
      - "下个月" / "下一个月" / "下月"  : next month
      - "半年" / "未来半年"             : next half year
      - "未来N周" / "N周"              : next N weeks
      - "未来N个月" / "N个月"           : next N months

    Args:
        scope: Scope string (Chinese or English)
        today: Reference date

    Returns:
        Tuple of (start_date, end_date)

    Raises:
        ValueError: When scope format is invalid or N is not a positive integer

    将 scope 字符串解析为 (start_date, end_date) 的日期范围。

    同时支持中文和英文 scope 格式：

    英文格式：
      - "half_year"  ：从 today 起未来 180 天（默认）
      - "this_week"  ：本周一到本周日
      - "next_week"  ：下周一到下周日
      - "next_month" ：下个月第一天到最后一天
      - "weeks=N"    ：从 today 起未来 N 周（N 为正整数）
      - "months=N"   ：从 today 起未来 N 个月（N 为正整数）

    中文格式：
      - "本周" / "这周"               ：本周
      - "下周" / "下一周"              ：下周
      - "下个月" / "下一个月" / "下月"  ：下个月
      - "半年" / "未来半年"             ：未来半年
      - "未来N周" / "N周"              ：未来 N 周
      - "未来N个月" / "N个月"           ：未来 N 个月

    Args:
        scope: 查询范围字符串（中英文均可）
        today: 参考日期

    Returns:
        (start_date, end_date) 元组

    Raises:
        ValueError: 当 scope 格式无效或 N 不是正整数时
    """
    # First normalize Chinese scope to English format
    # 先将中文 scope 标准化为英文格式
    scope = _normalize_cn_scope(scope)

    if scope == "half_year":
        return today, today + datetime.timedelta(days=180)

    if scope == "this_week":
        monday = today - datetime.timedelta(days=today.weekday())
        sunday = monday + datetime.timedelta(days=6)
        return monday, sunday

    if scope == "next_week":
        monday = today - datetime.timedelta(days=today.weekday())
        next_monday = monday + datetime.timedelta(days=7)
        next_sunday = next_monday + datetime.timedelta(days=6)
        return next_monday, next_sunday

    if scope == "this_month":
        # First to last day of the current month
        # 本月第一天到最后一天
        month_start = datetime.date(today.year, today.month, 1)
        last_day = cal_mod.monthrange(today.year, today.month)[1]
        month_end = datetime.date(today.year, today.month, last_day)
        return month_start, month_end

    if scope == "next_month":
        # First day of next month
        # 下个月的第一天
        if today.month == 12:
            target_year, target_month = today.year + 1, 1
        else:
            target_year, target_month = today.year, today.month + 1
        month_start = datetime.date(target_year, target_month, 1)
        last_day = cal_mod.monthrange(target_year, target_month)[1]
        month_end = datetime.date(target_year, target_month, last_day)
        return month_start, month_end

    # weeks=N format
    # weeks=N
    weeks_match = re.fullmatch(r"weeks=(\d+)", scope)
    if weeks_match:
        n = int(weeks_match.group(1))
        if n <= 0:
            raise ValueError(f"weeks 的值必须为正整数，当前为 {n}")
        return today, today + datetime.timedelta(weeks=n) - datetime.timedelta(days=1)

    # months=N format
    # months=N
    months_match = re.fullmatch(r"months=(\d+)", scope)
    if months_match:
        n = int(months_match.group(1))
        if n <= 0:
            raise ValueError(f"months 的值必须为正整数，当前为 {n}")
        # Calculate the year and month N months later
        # 计算 N 个月后的年月
        target_month = today.month + n
        target_year = today.year + (target_month - 1) // 12
        target_month = (target_month - 1) % 12 + 1
        last_day = cal_mod.monthrange(target_year, target_month)[1]
        end_date = datetime.date(target_year, target_month, last_day)
        return today, end_date

    raise ValueError(
        f"不支持的 scope 格式: '{scope}'。"
        "支持的格式为: 'half_year', 'this_week', 'next_week', 'this_month', 'next_month', 'weeks=N', 'months=N'"
    )


def get_holidays(
    scope: str = "half_year",
    today: Optional[datetime.date] = None,
) -> list[dict]:
    """
    Query Chinese public holiday and make-up workday information within a specified time range.

    Args:
        scope: Query range, supports the following formats (Chinese or English):
            - "half_year" / "半年" / "未来半年" (default): next 180 days
            - "this_week" / "本周" / "这周": current week (Monday to Sunday)
            - "next_week" / "下周" / "下一周": next week (Monday to Sunday)
            - "next_month" / "下个月" / "下一个月" / "下月": next month
            - "weeks=N" / "N周" / "未来N周": next N weeks from today (N is a positive integer)
            - "months=N" / "N个月" / "未来N个月": next N months from today (N is a positive integer)
        today: Reference date, defaults to the current date

    Returns:
        List of holiday records sorted by start date in ascending order.
        Each record is a dict containing:
            - type (str)  : Record type, values:
                - "holiday" : Chinese statutory public holiday
                - "weekend" : Regular weekend that can be rested (make-up workday weekends excluded)
            - name (str)  : Name, e.g., "春节", "周末"
            - start (str) : Start date in ISO format (YYYY-MM-DD)
            - end (str)   : End date in ISO format (YYYY-MM-DD)
            - days (int)  : Number of days

        Note: Make-up workdays (Saturday/Sunday that require work) are not included;
        only restable dates are shown.

    Examples:
        >>> from fcalendar import holiday
        >>> holiday()                      # Default: next half year
        >>> holiday("this_week")           # Holiday info for this week
        >>> holiday("next_week")           # Holiday info for next week
        >>> holiday("next_month")          # Holiday info for next month
        >>> holiday("weeks=3")             # Holiday info for next 3 weeks
        >>> holiday("months=2")            # Holiday info for next 2 months
        >>> holiday("本周")               # Chinese scope also supported
        >>> holiday("未来三周")            # Chinese numerals also supported

    Raises:
        ValueError: When scope format is invalid

    查询指定时间范围内的中国放假/调休信息。

    Args:
        scope: 查询范围，支持以下格式（中英文均可）：
            - "half_year" / "半年" / "未来半年"（默认）：未来 180 天
            - "this_week" / "本周" / "这周"：本周（周一至周日）
            - "next_week" / "下周" / "下一周"：下周（周一至周日）
            - "next_month" / "下个月" / "下一个月" / "下月"：下个月
            - "weeks=N" / "N周" / "未来N周"：从今天起未来 N 周（N 为正整数）
            - "months=N" / "N个月" / "未来N个月"：从今天起未来 N 个月（N 为正整数）
        today: 参考日期，默认为当前日期

    Returns:
        放假日期列表，按起始日期升序排列，每条记录为 dict，包含：
            - type (str)  ：记录类型，取值：
                - "holiday" ：中国法定节假日
                - "weekend" ：可正常休息的普通周末（调休上班的周末不在此列）
            - name (str)  ：名称，如 "春节"、"周末"
            - start (str) ：起始日期，ISO 格式（YYYY-MM-DD）
            - end (str)   ：结束日期，ISO 格式（YYYY-MM-DD）
            - days (int)  ：天数

        注意：调休上班（周六/日需要工作）不在返回结果中，只展示可放假的日期。

    Examples:
        >>> from fcalendar import holiday
        >>> holiday()                      # 默认：未来半年
        >>> holiday("this_week")           # 本周放假信息
        >>> holiday("next_week")           # 下周放假信息
        >>> holiday("next_month")          # 下个月放假信息
        >>> holiday("weeks=3")             # 未来 3 周放假信息
        >>> holiday("months=2")            # 未来 2 个月放假信息
        >>> holiday("本周")               # 中文 scope 同样支持
        >>> holiday("未来三周")            # 中文数字也支持

    Raises:
        ValueError: 当 scope 格式无效时
    """
    if today is None:
        today = datetime.date.today()

    start_date, end_date = _resolve_holiday_scope(scope, today)

    # Collect statutory holiday dates grouped by English holiday name
    # 按节假日英文名收集法定假期日期
    holiday_dates_by_name: dict[str, list[datetime.date]] = {}
    # Regular weekends that can be taken off
    # (Saturday/Sunday with is_holiday=True but no holiday name, and not make-up workdays)
    # 可正常休息的普通周末（周六/日 且 is_holiday=True 但无假期名称，且非调休上班）
    plain_weekend_dates: list[datetime.date] = []

    current = start_date
    while current <= end_date:
        try:
            on_holiday, name = get_holiday_detail(current)
            is_weekend_day = current.weekday() >= 5  # Saturday=5, Sunday=6 / 周六=5, 周日=6
            if on_holiday and name is not None:
                # Statutory holiday (including holiday days extended to weekends)
                # 法定假期（含被延长到周末的假期日）
                name_str = name if isinstance(name, str) else str(name)
                if name_str not in holiday_dates_by_name:
                    holiday_dates_by_name[name_str] = []
                holiday_dates_by_name[name_str].append(current)
            elif on_holiday and name is None and is_weekend_day:
                # Regular weekend (not occupied by make-up workday, can rest normally)
                # 普通周末（未被调休占用，可正常休息）
                plain_weekend_dates.append(current)
            # Make-up workdays (is_workday=True and is_weekend_day) are excluded from results
            # 调休上班（is_workday=True 且 is_weekend_day）不纳入结果
        except Exception:
            pass
        current += datetime.timedelta(days=1)

    results: list[dict] = []

    # Statutory holidays (type="holiday")
    # 法定假期（type="holiday"）
    for en_name, dates in holiday_dates_by_name.items():
        cn_name = HOLIDAY_EN_TO_CN.get(en_name, en_name)
        segments = _group_consecutive_dates(dates)
        for segment in segments:
            results.append({
                "type": "holiday",
                "name": cn_name,
                "start": segment[0].isoformat(),
                "end": segment[-1].isoformat(),
                "days": len(segment),
            })

    # Regular weekends (type="weekend"), merged by consecutive segments
    # 普通周末（type="weekend"），按连续段合并
    for segment in _group_consecutive_dates(plain_weekend_dates):
        results.append({
            "type": "weekend",
            "name": "周末",
            "start": segment[0].isoformat(),
            "end": segment[-1].isoformat(),
            "days": len(segment),
        })

    # Sort by start date in ascending order
    # 按起始日期升序排列
    results.sort(key=lambda x: x["start"])
    return results

"""测试 fcalendar 包的英文时间表达式识别功能

这个测试文件验证 fcalendar 包可以正确识别和标注英文时间表达式。
"""

import datetime
from fcalendar import query


def test_english_language_detection():
    """测试英文语言自动检测"""
    result = query("meeting tomorrow", datetime.date(2026, 2, 13))
    print(f"\n[test_english_language_detection] Input: meeting tomorrow")
    print(f"[test_english_language_detection] Output: {result}")
    assert result == "meeting tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)"


def test_english_relative_time_today():
    """测试英文相对时间：today"""
    result = query("meeting today", datetime.date(2026, 2, 13))
    print(f"\n[test_english_relative_time_today] Output: {result}")
    assert result == "meeting today (Today is February 13, 2026, today is February 13, 2026)"


def test_english_relative_time_tomorrow():
    """测试英文相对时间：tomorrow"""
    result = query("meeting tomorrow", datetime.date(2026, 2, 13))
    print(f"\n[test_english_relative_time_tomorrow] Output: {result}")
    assert result == "meeting tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)"


def test_english_relative_time_day_after_tomorrow():
    """测试英文相对时间：day after tomorrow"""
    result = query("travel day after tomorrow", datetime.date(2026, 2, 13))
    print(f"\n[test_english_relative_time_day_after_tomorrow] Output: {result}")
    assert result == "travel day after tomorrow (Today is February 13, 2026, day after tomorrow is February 15, 2026)"


def test_english_next_week():
    """测试英文：next week"""
    result = query("appointment next week", datetime.date(2026, 2, 13))
    print(f"\n[test_english_next_week] Output: {result}")
    assert result == "appointment next week (Today is February 13, 2026, next week is February 20, 2026)"


def test_english_next_month():
    """测试英文：next month"""
    result = query("business trip next month", datetime.date(2026, 2, 13))
    print(f"\n[test_english_next_month] Output: {result}")
    assert result == "business trip next month (Today is February 13, 2026, next month is March 1, 2026 - March 31, 2026)"


def test_english_weekday_monday():
    """测试英文星期：Monday"""
    result = query("meeting Monday", datetime.date(2026, 2, 13))
    print(f"\n[test_english_weekday_monday] Output: {result}")
    assert result == "meeting Monday (Today is February 13, 2026, Monday is February 16, 2026)"


def test_english_next_monday():
    """测试英文：next Monday"""
    result = query("meeting next Monday", datetime.date(2026, 2, 13))
    print(f"\n[test_english_next_monday] Output: {result}")
    assert result == "meeting next Monday (Today is February 13, 2026, next Monday is February 16, 2026)"


def test_english_weekday_wednesday():
    """测试英文星期：Wednesday"""
    result = query("visit museum Wednesday", datetime.date(2026, 2, 13))
    print(f"\n[test_english_weekday_wednesday] Output: {result}")
    assert result == "visit museum Wednesday (Today is February 13, 2026, Wednesday is February 18, 2026)"


def test_english_this_weekend():
    """测试英文：this weekend"""
    result = query("party this weekend", datetime.date(2026, 2, 13))
    print(f"\n[test_english_this_weekend] Output: {result}")
    assert result == "party this weekend (Today is February 13, 2026, this weekend is February 14, 2026 - February 15, 2026)"


def test_english_next_weekend():
    """测试英文：next weekend"""
    result = query("travel next weekend", datetime.date(2026, 2, 13))
    print(f"\n[test_english_next_weekend] Output: {result}")
    assert result == "travel next weekend (Today is February 13, 2026, next weekend is February 21, 2026 - February 22, 2026)"


def test_english_festival_christmas():
    """测试英文节日：Christmas"""
    result = query("buy gifts for Christmas", datetime.date(2026, 2, 13))
    print(f"\n[test_english_festival_christmas] Output: {result}")
    assert result == "buy gifts for Christmas (Today is February 13, 2026, Christmas is December 25, 2026)"


def test_english_festival_halloween():
    """测试英文节日：Halloween"""
    result = query("Halloween party", datetime.date(2026, 2, 13))
    print(f"\n[test_english_festival_halloween] Output: {result}")
    assert result == "Halloween party (Today is February 13, 2026, Halloween is October 31, 2026)"


def test_english_festival_valentine():
    """测试英文节日：Valentine's Day"""
    result = query("Valentine's Day flowers", datetime.date(2026, 2, 13))
    print(f"\n[test_english_festival_valentine] Output: {result}")
    assert result == "Valentine's Day flowers (Today is February 13, 2026, Valentine's Day is February 14, 2026)"


def test_english_specific_date_with_year():
    """测试英文具体日期（带年份）：January 15, 2027"""
    result = query("conference on January 15, 2027", datetime.date(2026, 2, 13))
    print(f"\n[test_english_specific_date_with_year] Output: {result}")
    assert result == "conference on January 15, 2027 (Today is February 13, 2026, January 15, 2027 is January 15, 2027)"


def test_english_specific_date_without_year():
    """测试英文具体日期（不带年份）：July 15th"""
    result = query("vacation July 15th", datetime.date(2026, 2, 13))
    print(f"\n[test_english_specific_date_without_year] Output: {result}")
    assert result == "vacation July 15th (Today is February 13, 2026, July 15th is July 15, 2026)"


def test_english_specific_date_january():
    """测试英文具体日期：January 15"""
    result = query("meeting on January 15", datetime.date(2026, 2, 13))
    print(f"\n[test_english_specific_date_january] Output: {result}")
    assert result == "meeting on January 15 (Today is February 13, 2026, January 15 is January 15, 2027)"


def test_english_multiple_expressions():
    """测试多个英文时间表达式"""
    result = query("meeting tomorrow, travel next weekend, Christmas party", datetime.date(2026, 2, 13))
    print(f"\n[test_english_multiple_expressions] Output: {result}")
    assert result == "meeting tomorrow, travel next weekend, Christmas party (Today is February 13, 2026, tomorrow is February 14, 2026, next weekend is February 21, 2026 - February 22, 2026, Christmas is December 25, 2026)"


def test_english_manual_lang_parameter():
    """测试手动指定语言参数"""
    result = query("tomorrow", datetime.date(2026, 2, 13), lang='en')
    print(f"\n[test_english_manual_lang_parameter] Output: {result}")
    assert result == "tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)"


def test_chinese_still_works():
    """测试中文功能不受影响"""
    result = query("明天开会", datetime.date(2026, 2, 13))
    print(f"\n[test_chinese_still_works] Output: {result}")
    assert result == "明天开会（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日）"


def test_english_no_time_expression():
    """测试无时间表达式的英文文本"""
    result = query("hello world", datetime.date(2026, 2, 13))
    print(f"\n[test_english_no_time_expression] Output: {result}")
    assert result == "hello world"


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    import pytest
    pytest.main([__file__, "-v", "-s"])

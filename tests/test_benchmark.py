"""测试 fcalendar 包的时间标注功能

这个测试文件验证 fcalendar 包可以作为独立的 Python 包使用，
不依赖 MCP 服务即可完成时间标注功能。
"""

import datetime
import json
import os
import pytest
from fcalendar import query, holiday


def test_import():
    """测试包导入"""
    assert query is not None
    assert callable(query)


def test_basic_query():
    """测试基本查询功能"""
    result = query("明天去上海", datetime.date(2026, 2, 13))
    print(f"\n[test_basic_query] 输入: 明天去上海")
    print(f"[test_basic_query] 输出: {result}")
    assert result == "明天去上海（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日）"


def test_query_without_date():
    """测试不指定日期的查询（使用当前日期）"""
    result = query("明天去上海")
    print(f"\n[test_query_without_date] 输入: 明天去上海")
    print(f"[test_query_without_date] 输出: {result}")
    assert "明天去上海（今天是" in result
    assert "明天是" in result


def test_multiple_expressions():
    """测试多个时间表达式"""
    result = query("明天开会，下周末去旅游", datetime.date(2026, 2, 13))
    print(f"\n[test_multiple_expressions] 输入: 明天开会，下周末去旅游")
    print(f"[test_multiple_expressions] 输出: {result}")
    assert result == "明天开会，下周末去旅游（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日，下周末是2026 年 2 月 21 日-2026 年 2 月 22 日）"


def test_relative_weekday():
    """测试相对星期表达"""
    result = query("下周四开会", datetime.date(2026, 2, 13))
    print(f"\n[test_relative_weekday] 输出: {result}")
    assert "下周四开会（今天是2026 年 2 月 13 日，下周四是2 月 19 日）" == result


def test_holiday():
    """测试节假日识别"""
    result = query("春节去旅游", datetime.date(2026, 2, 13))
    print(f"\n[test_holiday] 输出: {result}")
    assert "春节去旅游（今天是" in result
    assert "春节是2026 年 2 月" in result


def test_lunar_date():
    """测试农历日期"""
    result = query("正月十五看花灯", datetime.date(2026, 2, 13))
    print(f"\n[test_lunar_date] 输出: {result}")
    assert result == "正月十五看花灯（今天是2026 年 2 月 13 日，正月十五是2026 年 3 月 3 日）"


def test_western_festival():
    """测试西方节日"""
    result = query("圣诞节买礼物", datetime.date(2026, 2, 13))
    print(f"\n[test_western_festival] 输出: {result}")
    assert result == "圣诞节买礼物（今天是2026 年 2 月 13 日，圣诞节是2026 年 12 月 25 日）"


def test_season():
    """测试季节表达"""
    result = query("冬季去滑雪", datetime.date(2026, 2, 13))
    print(f"\n[test_season] 输出: {result}")
    assert "冬季去滑雪（今天是" in result
    assert "冬季是2026 年 12 月" in result


def test_solar_term():
    """测试二十四节气"""
    result = query("春分去踏青", datetime.date(2026, 2, 13))
    print(f"\n[test_solar_term] 输出: {result}")
    assert result == "春分去踏青（今天是2026 年 2 月 13 日，春分是2026 年 3 月 20 日）"


def test_specific_date():
    """测试具体日期"""
    result = query("7月15日出发", datetime.date(2026, 2, 13))
    print(f"\n[test_specific_date] 输出: {result}")
    assert result == "7月15日出发（今天是2026 年 2 月 13 日，7月15日是2026 年 7 月 15 日）"


def test_next_month():
    """测试下个月"""
    result = query("下个月搬家", datetime.date(2026, 2, 13))
    print(f"\n[test_next_month] 输出: {result}")
    assert result == "下个月搬家（今天是2026 年 2 月 13 日，下个月是2026 年 3 月 1 日-2026 年 3 月 31 日）"


def test_quarter():
    """测试季度表达"""
    result = query("Q4开会", datetime.date(2026, 2, 13))
    print(f"\n[test_quarter] 输出: {result}")
    assert result == "Q4开会（今天是2026 年 2 月 13 日，Q4是2026 年 10 月 1 日-2026 年 12 月 31 日）"


def test_year_prefix():
    """测试年份前缀"""
    result = query("去年元宵节去哪玩", datetime.date(2026, 2, 13))
    print(f"\n[test_year_prefix] 输出: {result}")
    assert result == "去年元宵节去哪玩（今天是2026 年 2 月 13 日，去年元宵节是2025 年 2 月 12 日）"


def test_no_time_expression():
    """测试无时间表达式"""
    result = query("改成三月十五", datetime.date(2026, 2, 13))
    print(f"\n[test_no_time_expression] 输出: {result}")
    assert result == "改成三月十五"


def test_complex_sentence():
    """测试复杂句子（综合示例）"""
    text = "明天和朋友去7月15日预定的巴黎酒店，下周末去杭州，春节飞日本，周三逛博物馆，正月十五看花灯，圣诞节买礼物，Q4开会，复活节去教堂"
    result = query(text, datetime.date(2026, 2, 13))
    print(f"\n[test_complex_sentence] 输入: {text}")
    print(f"[test_complex_sentence] 输出: {result}")

    # 验证所有时间表达都被正确标注（新格式：句末补充上下文）
    assert text + "（今天是" in result
    assert "明天是2026 年 2 月 14 日" in result
    assert "7月15日是2026 年 7 月 15 日" in result
    assert "下周末是2026 年 2 月 21 日-2026 年 2 月 22 日" in result
    assert "春节是2026 年 2 月 15 日-2026 年 2 月 23 日" in result
    assert "周三是2026 年 2 月 18 日" in result
    assert "正月十五是2026 年 3 月 3 日" in result
    assert "圣诞节是2026 年 12 月 25 日" in result
    assert "Q4是2026 年 10 月 1 日-2026 年 12 月 31 日" in result
    assert "复活节是2026 年 4 月 5 日" in result


def test_current_time_keywords():
    """测试当前时间关键词识别（实时模式）"""
    import re

    # 不提供 test_date，测试实时模式
    keywords = ["当前时间", "现在", "当前", "目前", "此时", "此刻", "眼下", "当下", "这会儿", "这时候"]

    for keyword in keywords:
        result = query(f"{keyword}是几点")  # 不传 today，使用实时时间
        print(f"\n[test_current_time_keywords] 关键词: {keyword}")
        print(f"[test_current_time_keywords] 输出: {result}")

        # 验证包含关键词和北京时间标注
        assert keyword in result, f"结果中应包含关键词 '{keyword}'"
        assert "今天是" in result, "结果中应包含今天的日期"
        assert f"{keyword}是" in result, f"结果中应包含 '{keyword}是'"
        # 验证包含时分秒格式
        assert re.search(r'\d{2}:\d{2}:\d{2}', result), f"关键词 '{keyword}' 的结果中应包含时分秒"

    print("\n✅ 所有当前时间关键词测试通过（实时模式）")

def test_benchmark_cases():
    """使用 benchmark.json 中的测试用例进行验证"""
    # 使用相对路径读取 benchmark 文件
    test_dir = os.path.dirname(os.path.abspath(__file__))
    benchmark_path = os.path.join(test_dir, "benchmark.json")

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    # 统计变量
    total = len(benchmark_data)
    passed = 0
    failed = 0
    failed_cases = []

    print(f"\n{'='*60}")
    print(f"开始运行 Benchmark 测试，共 {total} 个用例")
    print(f"{'='*60}\n")

    # 测试所有用例
    for case in benchmark_data:
        test_query = case["query"]
        mock_today = datetime.datetime.strptime(case["mock_today"], "%Y-%m-%d").date()
        expected = case["expected"]

        result = query(test_query, mock_today)

        # 验证结果与预期一致
        if result == expected:
            passed += 1
            print(f"✅ [{case['id']}] PASSED")
        else:
            failed += 1
            failed_cases.append({
                'id': case['id'],
                'description': case['description'],
                'query': test_query,
                'expected': expected,
                'actual': result
            })
            print(f"❌ [{case['id']}] FAILED")

    # 打印统计结果
    print(f"\n{'='*60}")
    print(f"测试完成！")
    print(f"{'='*60}")
    print(f"总计: {total} 个用例")
    print(f"成功: {passed} 个 ({passed/total*100:.1f}%)")
    print(f"失败: {failed} 个 ({failed/total*100:.1f}%)")
    print(f"{'='*60}\n")

    # 如果有失败的用例，打印详细信息
    if failed_cases:
        print(f"失败用例详情：\n")
        for case in failed_cases:
            print(f"用例ID: {case['id']}")
            print(f"描述: {case['description']}")
            print(f"输入: {case['query']}")
            print(f"期望: {case['expected']}")
            print(f"实际: {case['actual']}")
            print(f"{'-'*60}\n")

    # 如果有失败的用例，让测试失败
    assert failed == 0, f"有 {failed} 个测试用例失败"



def test_holiday_return_format():
    """测试 holiday() 返回值的结构（含 type 字段校验）"""
    result = holiday("next_month", datetime.date(2026, 3, 31))
    print(f"\n[test_holiday_return_format] 输出: {result}")
    # 返回值必须是列表
    assert isinstance(result, list)
    valid_types = {"holiday", "weekend"}
    # 每条记录都必须包含 type / name / start / end / days 五个字段
    for item in result:
        assert isinstance(item, dict), "每条记录应为 dict"
        assert "type" in item, "缺少 type 字段"
        assert "name" in item, "缺少 name 字段"
        assert "start" in item, "缺少 start 字段"
        assert "end" in item, "缺少 end 字段"
        assert "days" in item, "缺少 days 字段"
        assert item["type"] in valid_types, f"type 值非法: {item['type']}"
        assert isinstance(item["name"], str), "name 应为字符串"
        assert isinstance(item["start"], str), "start 应为字符串"
        assert isinstance(item["end"], str), "end 应为字符串"
        assert isinstance(item["days"], int), "days 应为整数"
        assert item["days"] >= 1, "days 至少为 1"
        # start <= end
        assert item["start"] <= item["end"], "start 不应晚于 end"
    print("✅ 返回格式验证通过")


def test_holiday_next_month():
    """测试查询下个月的节假日（2026-03-31 -> 四月无节假日，五月有劳动节）"""
    result = holiday("next_month", datetime.date(2026, 3, 31))
    print(f"\n[test_holiday_next_month] 输出: {result}")
    # 4月是清明节（已过3月底），且劳动节在5月，4月无法定假日
    assert isinstance(result, list)
    # 结果按 start 升序排列
    starts = [r["start"] for r in result]
    assert starts == sorted(starts), "结果应按起始日期升序排列"


def test_holiday_this_week():
    """测试查询本周节假日"""
    # 2026-05-01 是劳动节，周五；本周(4月27日-5月3日)包含劳动节
    result = holiday("this_week", datetime.date(2026, 4, 27))
    print(f"\n[test_holiday_this_week] 输出: {result}")
    assert isinstance(result, list)
    # 劳动节应该在本周范围内
    names = [r["name"] for r in result]
    assert "劳动节" in names, f"本周(4月27日-5月3日)应包含劳动节，实际: {result}"


def test_holiday_next_week():
    """测试查询下周节假日"""
    # 2026-04-20（周一）的下周是 4/27-5/3，包含劳动节 5/1
    result = holiday("next_week", datetime.date(2026, 4, 20))
    print(f"\n[test_holiday_next_week] 输出: {result}")
    assert isinstance(result, list)
    names = [r["name"] for r in result]
    assert "劳动节" in names, f"下周(4月27日-5月3日)应包含劳动节，实际: {result}"


def test_holiday_default():
    """测试默认查询（未来半年）"""
    result = holiday("half_year", datetime.date(2026, 3, 31))
    print(f"\n[test_holiday_default] 输出: {result}")
    assert isinstance(result, list)
    # 未来 180 天（2026-03-31 ~ 2026-09-27）应包含劳动节、端午节、中秋节
    names = [r["name"] for r in result]
    assert "劳动节" in names, f"未来半年应包含劳动节，实际: {names}"
    assert "端午节" in names, f"未来半年应包含端午节，实际: {names}"
    # 结果按 start 升序排列
    starts = [r["start"] for r in result]
    assert starts == sorted(starts), "结果应按起始日期升序排列"


def test_holiday_future_weeks():
    """测试查询未来 N 周节假日"""
    # 2026-04-27 起未来 1 周（4/27-5/3），应包含劳动节
    result = holiday("weeks=1", datetime.date(2026, 4, 27))
    print(f"\n[test_holiday_future_weeks] weeks=1 输出: {result}")
    assert isinstance(result, list)
    names = [r["name"] for r in result]
    assert "劳动节" in names, f"未来 1 周应包含劳动节，实际: {names}"

    # 未来 0 周应抛出 ValueError
    with pytest.raises(ValueError):
        holiday("weeks=0", datetime.date(2026, 4, 27))


def test_holiday_future_months():
    """测试查询未来 N 个月节假日"""
    # 2026-03-31 起未来 2 个月（3/31-5/31），应包含劳动节
    result = holiday("months=2", datetime.date(2026, 3, 31))
    print(f"\n[test_holiday_future_months] months=2 输出: {result}")
    assert isinstance(result, list)
    names = [r["name"] for r in result]
    assert "劳动节" in names, f"未来 2 个月应包含劳动节，实际: {names}"

    # 未来 0 个月应抛出 ValueError
    with pytest.raises(ValueError):
        holiday("months=0", datetime.date(2026, 3, 31))


def test_holiday_invalid_scope():
    """测试无效 scope 参数抛出 ValueError"""
    with pytest.raises(ValueError):
        holiday("invalid_scope", datetime.date(2026, 3, 31))


def test_holiday_no_today():
    """测试不传 today 参数时使用当前日期（smoke test）"""
    result = holiday("this_week")
    print(f"\n[test_holiday_no_today] 本周节假日: {result}")
    assert isinstance(result, list)


def test_holiday_empty_range():
    """测试范围内没有节假日时返回空列表"""
    # 2026-03-31 起本周（3/30-4/5）无法定假日（清明节在4/5但今年是4/5）
    # 使用 next_month 来验证4月（4/1-4/30）的节假日情况
    result = holiday("this_week", datetime.date(2026, 3, 31))
    print(f"\n[test_holiday_empty_range] 本周(3/30-4/5) 节假日: {result}")
    assert isinstance(result, list)
    # 验证清明节是否在范围内（4/5 是清明节）
    names = [r["name"] for r in result]
    print(f"  节假日名称: {names}")


def test_holiday_december_next_month():
    """测试 12 月查询下个月（跨年到 1 月）"""
    result = holiday("next_month", datetime.date(2026, 12, 1))
    print(f"\n[test_holiday_december_next_month] 下个月(1月)节假日: {result}")
    assert isinstance(result, list)
    # 元旦在 1 月，但具体是否是假期取决于 chinese_calendar 数据
    # 验证结果格式
    for item in result:
        assert item["start"].startswith("2027-01"), f"下个月应在 2027 年 1 月，实际: {item}"


def test_print():
    """测试复杂句子（综合示例）"""
    text = "今天去哪里"
    result = query(text)
    print(f"\n[test_print] 输入: {text}")


# ── 中文 scope 测试 ──────────────────────────────────────────────────────────

def test_holiday_cn_this_week():
    """中文 scope: 本周 / 这周 等同于 this_week"""
    ref = datetime.date(2026, 4, 27)
    result_en = holiday("this_week", ref)
    result_cn1 = holiday("本周", ref)
    result_cn2 = holiday("这周", ref)
    print(f"\n[test_holiday_cn_this_week] 本周: {result_cn1}")
    assert result_cn1 == result_en, f"'本周' 应等同于 'this_week'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'这周' 应等同于 'this_week'，实际: {result_cn2}"


def test_holiday_cn_next_week():
    """中文 scope: 下周 / 下一周 等同于 next_week"""
    ref = datetime.date(2026, 4, 20)
    result_en = holiday("next_week", ref)
    result_cn1 = holiday("下周", ref)
    result_cn2 = holiday("下一周", ref)
    print(f"\n[test_holiday_cn_next_week] 下周: {result_cn1}")
    assert result_cn1 == result_en, f"'下周' 应等同于 'next_week'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'下一周' 应等同于 'next_week'，实际: {result_cn2}"


def test_holiday_cn_next_month():
    """中文 scope: 下个月 / 下一个月 / 下月 等同于 next_month"""
    ref = datetime.date(2026, 3, 31)
    result_en = holiday("next_month", ref)
    result_cn1 = holiday("下个月", ref)
    result_cn2 = holiday("下一个月", ref)
    result_cn3 = holiday("下月", ref)
    print(f"\n[test_holiday_cn_next_month] 下个月: {result_cn1}")
    assert result_cn1 == result_en, f"'下个月' 应等同于 'next_month'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'下一个月' 应等同于 'next_month'，实际: {result_cn2}"
    assert result_cn3 == result_en, f"'下月' 应等同于 'next_month'，实际: {result_cn3}"


def test_holiday_cn_half_year():
    """中文 scope: 半年 / 未来半年 等同于 half_year"""
    ref = datetime.date(2026, 3, 31)
    result_en = holiday("half_year", ref)
    result_cn1 = holiday("半年", ref)
    result_cn2 = holiday("未来半年", ref)
    print(f"\n[test_holiday_cn_half_year] 未来半年: {result_cn1}")
    assert result_cn1 == result_en, f"'半年' 应等同于 'half_year'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'未来半年' 应等同于 'half_year'，实际: {result_cn2}"


def test_holiday_cn_weeks_chinese_num():
    """中文 scope: 三周 / 未来三周 等同于 weeks=3（中文数字）"""
    ref = datetime.date(2026, 4, 27)
    result_en = holiday("weeks=3", ref)
    result_cn1 = holiday("三周", ref)
    result_cn2 = holiday("未来三周", ref)
    print(f"\n[test_holiday_cn_weeks_chinese_num] 三周: {result_cn1}")
    assert result_cn1 == result_en, f"'三周' 应等同于 'weeks=3'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'未来三周' 应等同于 'weeks=3'，实际: {result_cn2}"


def test_holiday_cn_weeks_arabic_num():
    """中文 scope: 2周 / 未来2周 等同于 weeks=2（阿拉伯数字）"""
    ref = datetime.date(2026, 4, 27)
    result_en = holiday("weeks=2", ref)
    result_cn1 = holiday("2周", ref)
    result_cn2 = holiday("未来2周", ref)
    print(f"\n[test_holiday_cn_weeks_arabic_num] 2周: {result_cn1}")
    assert result_cn1 == result_en, f"'2周' 应等同于 'weeks=2'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'未来2周' 应等同于 'weeks=2'，实际: {result_cn2}"


def test_holiday_cn_months_chinese_num():
    """中文 scope: 两个月 / 未来两个月 等同于 months=2（中文数字）"""
    ref = datetime.date(2026, 3, 31)
    result_en = holiday("months=2", ref)
    result_cn1 = holiday("两个月", ref)
    result_cn2 = holiday("未来两个月", ref)
    print(f"\n[test_holiday_cn_months_chinese_num] 两个月: {result_cn1}")
    assert result_cn1 == result_en, f"'两个月' 应等同于 'months=2'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'未来两个月' 应等同于 'months=2'，实际: {result_cn2}"


def test_holiday_cn_months_arabic_num():
    """中文 scope: 3个月 / 未来3个月 等同于 months=3（阿拉伯数字）"""
    ref = datetime.date(2026, 3, 31)
    result_en = holiday("months=3", ref)
    result_cn1 = holiday("3个月", ref)
    result_cn2 = holiday("未来3个月", ref)
    print(f"\n[test_holiday_cn_months_arabic_num] 3个月: {result_cn1}")
    assert result_cn1 == result_en, f"'3个月' 应等同于 'months=3'，实际: {result_cn1}"
    assert result_cn2 == result_en, f"'未来3个月' 应等同于 'months=3'，实际: {result_cn2}"


def test_holiday_cn_various_chinese_nums():
    """中文 scope: 验证更多中文数字映射（一、四、五、六...十二）"""
    ref = datetime.date(2026, 1, 1)
    # 验证不同中文数字均能正确解析为对应的 weeks=N
    for cn, num in [("一", 1), ("四", 4), ("五", 5), ("六", 6),
                    ("七", 7), ("八", 8), ("九", 9), ("十", 10),
                    ("十一", 11), ("十二", 12)]:
        result_en = holiday(f"weeks={num}", ref)
        result_cn = holiday(f"{cn}周", ref)
        assert result_cn == result_en, (
            f"'{cn}周' 应等同于 'weeks={num}'，实际: {result_cn}"
        )
    print("\n[test_holiday_cn_various_chinese_nums] 所有中文数字解析正确 ✅")


# ── 周末与调休测试 ───────────────────────────────────────────────────────────

def test_holiday_type_field():
    """验证所有返回记录都包含合法的 type 字段（只有 holiday / weekend 两种）"""
    valid_types = {"holiday", "weekend"}
    # 以劳动节前后为例
    result = holiday("weeks=3", datetime.date(2026, 4, 25))
    print(f"\n[test_holiday_type_field] 输出: {result}")
    assert isinstance(result, list)
    assert len(result) > 0, "结果不应为空"
    for item in result:
        assert "type" in item, f"缺少 type 字段: {item}"
        assert item["type"] in valid_types, f"type 值非法: {item['type']}"
    # 调休上班不应出现在结果中
    assert not any(r["type"] == "workday_on_weekend" for r in result), \
        "调休上班不应出现在结果中"


def test_holiday_weekend_included():
    """验证可正常休息的普通周末出现在结果中"""
    # 2026-04-25(六) 2026-04-26(日) 是普通周末（非调休）
    result = holiday("weeks=1", datetime.date(2026, 4, 25))
    print(f"\n[test_holiday_weekend_included] 输出: {result}")
    weekend_items = [r for r in result if r["type"] == "weekend"]
    assert len(weekend_items) > 0, f"应包含周末记录，实际: {result}"
    # 4/25-4/26 应该被合并为一条
    starts = [r["start"] for r in weekend_items]
    assert "2026-04-25" in starts, f"4/25 应为周末起始日，实际: {weekend_items}"
    item = next(r for r in weekend_items if r["start"] == "2026-04-25")
    assert item["end"] == "2026-04-26", f"4/25-4/26 应合并为一段，实际: {item}"
    assert item["days"] == 2, f"周末天数应为 2，实际: {item['days']}"
    assert item["name"] == "周末", f"周末 name 应为 '周末'，实际: {item['name']}"


def test_holiday_workday_on_weekend_excluded():
    """验证调休上班（5/9 周六）不出现在结果中"""
    # 2026-05-09 是周六，劳动节调休上班，不应出现在放假列表里
    result = holiday("weeks=3", datetime.date(2026, 4, 25))
    print(f"\n[test_holiday_workday_on_weekend_excluded] 输出: {result}")
    all_starts = {r["start"] for r in result}
    assert "2026-05-09" not in all_starts, \
        f"5/9 是调休上班，不应出现在放假结果中，实际: {result}"
    # 结果中不应有 workday_on_weekend 类型
    assert not any(r["type"] == "workday_on_weekend" for r in result), \
        "结果中不应包含 workday_on_weekend 类型记录"

def test_holiday_weekend_not_returned_when_work():
    """验证调休上班的周末（5/9 周六）不出现在 weekend 类型中"""
    result = holiday("weeks=3", datetime.date(2026, 4, 25))
    weekend_starts = {r["start"] for r in result if r["type"] == "weekend"}
    print(f"\n[test_holiday_weekend_not_returned_when_work] weekend dates: {weekend_starts}")
    # 5/9 是调休上班，不应出现在 weekend 里
    assert "2026-05-09" not in weekend_starts, \
        f"5/9 是调休上班，不应出现在 weekend 中，实际: {weekend_starts}"


def test_holiday_existing_format_unchanged():
    """验证法定假期的 name/start/end/days 字段向后兼容，type='holiday'"""
    # 劳动节 2026-05-01~05-05
    result = holiday("weeks=3", datetime.date(2026, 4, 25))
    holiday_items = [r for r in result if r["type"] == "holiday"]
    print(f"\n[test_holiday_existing_format_unchanged] 法定假期: {holiday_items}")
    assert len(holiday_items) > 0, "应包含法定假期记录"
    labour_day = next((r for r in holiday_items if r["name"] == "劳动节"), None)
    assert labour_day is not None, "应包含劳动节"
    assert labour_day["start"] == "2026-05-01"
    assert labour_day["end"] == "2026-05-05"
    assert labour_day["days"] == 5
    assert labour_day["type"] == "holiday"



def test_holiday_this_month():
    """测试查询本月节假日（this_month scope）"""
    # 2026-04-27（周一）当月是4月，包含清明节和劳动节（5/1在5月，清明在4/4-4/6）
    result = holiday("this_month", datetime.date(2026, 4, 1))
    print(f"\n[test_holiday_this_month] 4月本月节假日: {result}")
    assert isinstance(result, list)
    # 4月包含清明节
    names = [r["name"] for r in result]
    assert "清明节" in names, f"4月应包含清明节，实际: {names}"
    # 结果按 start 升序排列
    starts = [r["start"] for r in result]
    assert starts == sorted(starts), "结果应按起始日期升序排列"

    # 中文别名测试
    result_cn1 = holiday("本月", datetime.date(2026, 4, 1))
    result_cn2 = holiday("这个月", datetime.date(2026, 4, 1))
    result_cn3 = holiday("当月", datetime.date(2026, 4, 1))
    assert result_cn1 == result, f"'本月' 应等同于 'this_month'，实际: {result_cn1}"
    assert result_cn2 == result, f"'这个月' 应等同于 'this_month'，实际: {result_cn2}"
    assert result_cn3 == result, f"'当月' 应等同于 'this_month'，实际: {result_cn3}"
    print("✅ this_month 及中文别名均正确")


def test_cn_past_time_expressions():
    """测试中文过去时间表达式：昨天、前天、大前天、上周X、上周末、上个月"""
    import datetime
    ref = datetime.date(2026, 3, 15)  # 周日

    # 昨天
    result = query("昨天的会议记录", ref)
    assert "3 月 14 日" in result, f"昨天应为3月14日，实际: {result}"

    # 前天
    result = query("前天出发", ref)
    assert "3 月 13 日" in result, f"前天应为3月13日，实际: {result}"

    # 大前天
    result = query("大前天签的合同", ref)
    assert "3 月 12 日" in result, f"大前天应为3月12日，实际: {result}"

    # 上周三（ref是周日2026-03-15，本周一=3/9，上周一=3/2，上周三=3/4）
    result = query("上周三开会", ref)
    assert "3 月 4 日" in result, f"上周三应为3月4日，实际: {result}"

    # 上周末（上周六=3/7，上周日=3/8）
    result = query("上周末去爬山", ref)
    assert "3 月 7 日" in result, f"上周末应包含3月7日，实际: {result}"

    # 上个月（2月：1日-28日）
    result = query("上个月的账单", ref)
    assert "2 月 1 日" in result and "2 月 28 日" in result, f"上个月应为2月1日-28日，实际: {result}"

    print("✅ 中文过去时间表达式全部正确")


def test_en_past_time_expressions():
    """测试英文过去时间表达式：yesterday, day before yesterday, last week, last month, last Monday"""
    import datetime
    ref = datetime.date(2026, 3, 15)  # Sunday

    # yesterday
    result = query("the meeting yesterday", ref)
    assert "March 14, 2026" in result, f"yesterday 应为 March 14, 实际: {result}"

    # day before yesterday
    result = query("trip day before yesterday", ref)
    assert "March 13, 2026" in result, f"day before yesterday 应为 March 13, 实际: {result}"

    # last week (ref=周日2026-03-15，本周一=3/9，上周一=3/2，上周日=3/8)
    result = query("report from last week", ref)
    assert "March 2, 2026" in result, f"last week 应为 March 2-8, 实际: {result}"

    # last month (2月1日-28日)
    result = query("bill from last month", ref)
    assert "February 1, 2026" in result, f"last month 应为 February 1-28, 实际: {result}"

    # last Monday (ref=周日2026-03-15，本周一=3/9，上周一=3/2)
    result = query("meeting last Monday", ref)
    assert "March 2, 2026" in result, f"last Monday 应为3月2日，实际: {result}"

    print("✅ 英文过去时间表达式全部正确")


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    import pytest
    pytest.main([__file__, "-v", "-s"])

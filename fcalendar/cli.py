#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fcalendar CLI 入口

用法：
    fcalendar query <text> [--today YYYY-MM-DD] [--lang zh|en]
    fcalendar holiday [--scope <scope>] [--today YYYY-MM-DD]

所有输出为单行 JSON，输出到 stdout；错误信息输出到 stderr。
"""

import argparse
import datetime
import json
import sys

from fcalendar import holiday as _holiday
from fcalendar import query as _query


def _parse_today(today_str: str) -> datetime.date:
    """将 YYYY-MM-DD 字符串解析为 date 对象"""
    try:
        return datetime.date.fromisoformat(today_str)
    except ValueError:
        print(f"错误：--today 参数格式无效，应为 YYYY-MM-DD，实际收到: {today_str}", file=sys.stderr)
        sys.exit(1)


def cmd_query(args: argparse.Namespace) -> None:
    """处理 query 子命令"""
    today = _parse_today(args.today) if args.today else None
    lang = args.lang if args.lang else None
    try:
        result = _query(args.text, today=today, lang=lang)
        output = {"input": args.text, "result": result}
        print(json.dumps(output, ensure_ascii=False))
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


def cmd_holiday(args: argparse.Namespace) -> None:
    """处理 holiday 子命令"""
    today = _parse_today(args.today) if args.today else None
    scope = args.scope or "half_year"
    try:
        result = _holiday(scope=scope, today=today)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, Exception) as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the fcalendar CLI.
    
    主入口函数，处理命令行参数并执行相应命令。
    """
    parser = argparse.ArgumentParser(
        prog="fcalendar",
        description="fcalendar - 中国日期时间表达式识别与节假日查询工具",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.11.0"
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    # ── query 子命令 ──────────────────────────────────────────────────────────
    query_parser = subparsers.add_parser(
        "query",
        help="识别并标注文本中的时间表达式",
        description=(
            "识别并标注文本中的时间表达式，输出 JSON：{input, result}。\n"
            "result 为标注后的文本，附带具体日期说明。"
        ),
    )
    query_parser.add_argument("text", help="要识别的文本，如：\"下周开会\" 或 \"meeting next Monday\"")
    query_parser.add_argument(
        "--today",
        metavar="YYYY-MM-DD",
        help="参考日期，默认为当前日期",
    )
    query_parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        metavar="zh|en",
        help="语言代码，zh=中文，en=英文。默认自动检测",
    )
    query_parser.set_defaults(func=cmd_query)

    # ── holiday 子命令 ────────────────────────────────────────────────────────
    holiday_parser = subparsers.add_parser(
        "holiday",
        help="查询指定范围内的放假信息（法定假期 + 可休息的普通周末）",
        description=(
            "查询指定范围内的放假信息，输出 JSON 数组，每条记录包含：\n"
            "  type  : 'holiday'（法定假期）或 'weekend'（普通周末）\n"
            "  name  : 假期名称，如 '劳动节'、'周末'\n"
            "  start : 起始日期（YYYY-MM-DD）\n"
            "  end   : 结束日期（YYYY-MM-DD）\n"
            "  days  : 天数\n\n"
            "scope 支持以下格式（中英文均可）：\n"
            "  half_year / 半年 / 未来半年  （默认，未来 180 天）\n"
            "  this_week / 本周 / 这周\n"
            "  next_week / 下周 / 下一周\n"
            "  next_month / 下个月 / 下月\n"
            "  weeks=N / N周 / 未来N周      （N 为正整数）\n"
            "  months=N / N个月 / 未来N个月  （N 为正整数）"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    holiday_parser.add_argument(
        "--scope",
        metavar="SCOPE",
        default="half_year",
        help="查询范围，默认 half_year（未来 180 天）。支持中英文，如：本周、next_week、weeks=3",
    )
    holiday_parser.add_argument(
        "--today",
        metavar="YYYY-MM-DD",
        help="参考日期，默认为当前日期",
    )
    holiday_parser.set_defaults(func=cmd_holiday)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

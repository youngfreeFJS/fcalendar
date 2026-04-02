English | [简体中文](README_CN.md)

# fcalendar

A powerful Python library and CLI tool for recognizing and annotating Chinese/English time expressions, and querying Chinese public holiday schedules.

## ✨ Features

- 🌍 **Multi-language Support**: Automatic language detection, supports both Chinese and English input/output
- 🎯 **Relative Time**: tomorrow, next week, next month, etc.
- 📅 **Chinese Legal Holidays**: Spring Festival, National Day, Mid-Autumn Festival, etc.
- 🌙 **Lunar Calendar**: Traditional festivals, lunar dates
- 🎄 **Western Festivals**: Christmas, Halloween, Valentine's Day, etc.
- 🌸 **24 Solar Terms**: Spring Equinox, Winter Solstice, etc.
- 🍂 **Seasons**: Spring, Summer, Autumn, Winter
- 📊 **Quarters and Cycles**: Q1-Q4, first/second half of year
- 📆 **Specific Dates**: Supports various date formats
- 🔄 **Year Prefixes**: last year, next year, 2024, etc.
- ⏰ **Real-time**: Supports current time queries (returns Beijing time)
- 🗓️ **Holiday Query**: Query Chinese public holidays and weekends within a specified range
- 💻 **CLI Support**: All core features accessible via command-line interface

## 📦 Installation

### Install from PyPI

```bash
pip install fcalendar
```

### Install from Aliyun PyPI (Internal Network)

```bash
pip install fcalendar
```

### Install from Source

```bash
git clone https://github.com/youngfreefjs/fcalendar.git
cd fcalendar
pip install -e .
```
## 🚀 Quick Start

### Python API

```python
from fcalendar import query, holiday
import datetime

# Time expression recognition
result = query("meeting tomorrow", datetime.date(2026, 2, 13))
print(result)
# Output: meeting tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)

# Holiday query
result = holiday("next_month", datetime.date(2026, 3, 31))
print(result)
# Output: [{'type': 'holiday', 'name': '清明节', 'start': '2026-04-04', 'end': '2026-04-06', 'days': 3}, ...]
```

### CLI

```bash
# Time expression recognition
fcalendar query "meeting next Monday"
# Output: {"input": "meeting next Monday", "result": "meeting next Monday (Today is ..., next Monday is April 6, 2026)"}

# Holiday query (supports Chinese and English scope)
fcalendar holiday --scope next_month
fcalendar holiday --scope 本周
fcalendar holiday --scope "weeks=3"
fcalendar holiday --scope 未来两个月
```

## 🌍 Language Support

fcalendar supports both **Chinese** and **English** with automatic language detection:

### Automatic Language Detection

The library automatically detects the input language and returns output in the same language:

```python
# Chinese input → Chinese output
query("明天开会", datetime.date(2026, 2, 13))
# Output: 明天开会（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日）

# English input → English output
query("meeting tomorrow", datetime.date(2026, 2, 13))
# Output: meeting tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)
```

### Manual Language Specification

You can also manually specify the language using the `lang` parameter:

```python
# Force English output
query("tomorrow", datetime.date(2026, 2, 13), lang='en')
# Output: tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)

# Force Chinese output
query("明天", datetime.date(2026, 2, 13), lang='zh')
# Output: 明天（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日）
```

### Supported English Expressions

- **Relative time**: today, tomorrow, day after tomorrow, next week, next month
- **Weekdays**: Monday, Tuesday, next Monday, this weekend, next weekend
- **Festivals**: Christmas, Halloween, Valentine's Day, Easter, Thanksgiving
- **Specific dates**: January 15, 2026, July 15th, Jan 15

> **Note**: For Chinese documentation and examples, please see [README_CN.md](README_CN.md)

## 📖 Usage Examples
### Real-time Query

```python
# Query current time (returns Beijing time)
result = query("现在是几点")
print(result)
# Output: 现在是几点（今天是2026 年 3 月 24 日，现在是2026 年 3 月 24 日 21:35:42）

# Supports various current time keywords
keywords = ["当前时间", "现在", "当前", "目前", "此时", "此刻", "眼下", "当下", "这会儿", "这时候", "今天"]
```

## 📖 Supported Time Expressions
### 1️⃣ Relative Time and Real-time

```python
# Relative time
query("meeting tomorrow", datetime.date(2026, 2, 13))
# Output: meeting tomorrow (Today is February 13, 2026, tomorrow is February 14, 2026)

query("travel day after tomorrow", datetime.date(2026, 2, 13))
# Output: travel day after tomorrow (Today is February 13, 2026, day after tomorrow is February 15, 2026)

query("appointment next week", datetime.date(2026, 2, 13))
# Output: appointment next week (Today is February 13, 2026, next week is February 20, 2026)

query("meeting next Monday", datetime.date(2026, 2, 13))
# Output: meeting next Monday (Today is February 13, 2026, next Monday is February 16, 2026)

query("travel next weekend", datetime.date(2026, 2, 13))
# Output: travel next weekend (Today is February 13, 2026, next weekend is February 21, 2026 - February 22, 2026)

query("party this weekend", datetime.date(2026, 2, 13))
# Output: party this weekend (Today is February 13, 2026, this weekend is February 14, 2026 - February 15, 2026)

query("visit museum Wednesday", datetime.date(2026, 2, 13))
# Output: visit museum Wednesday (Today is February 13, 2026, Wednesday is February 18, 2026)

query("business trip next month", datetime.date(2026, 2, 13))
# Output: business trip next month (Today is February 13, 2026, next month is March 1, 2026 - March 31, 2026)

# Real-time keywords (returns Beijing time)
query("what time is it now", datetime.date(2026, 2, 13))
# Output: what time is it now (Today is February 13, 2026, now is Beijing time February 13, 2026 00:00:00)

query("current time", datetime.date(2026, 2, 13))
# Output: current time (Today is February 13, 2026, current time is Beijing time February 13, 2026 00:00:00)
```
### 2️⃣ Western Festivals

```python
query("buy gifts for Christmas", datetime.date(2026, 2, 13))
# Output: buy gifts for Christmas (Today is February 13, 2026, Christmas is December 25, 2026)

query("Halloween party", datetime.date(2026, 2, 13))
# Output: Halloween party (Today is February 13, 2026, Halloween is October 31, 2026)

query("Valentine's Day flowers", datetime.date(2026, 2, 13))
# Output: Valentine's Day flowers (Today is February 13, 2026, Valentine's Day is February 14, 2026)

query("Easter church service", datetime.date(2026, 2, 13))
# Output: Easter church service (Today is February 13, 2026, Easter is April 5, 2026)

query("Thanksgiving dinner", datetime.date(2026, 2, 13))
# Output: Thanksgiving dinner (Today is February 13, 2026, Thanksgiving is November 26, 2026)

query("Independence Day fireworks", datetime.date(2026, 2, 13))
# Output: Independence Day fireworks (Today is February 13, 2026, Independence Day is July 4, 2026)
```

### 3️⃣ Specific Dates

```python
# Month and day
query("meeting on January 15", datetime.date(2026, 2, 13))
# Output: meeting on January 15 (Today is February 13, 2026, January 15 is January 15, 2027)

query("vacation July 15th", datetime.date(2026, 2, 13))
# Output: vacation July 15th (Today is February 13, 2026, July 15th is July 15, 2026)

# With year
query("conference on January 15, 2027", datetime.date(2026, 2, 13))
# Output: conference on January 15, 2027 (Today is February 13, 2026, January 15, 2027 is January 15, 2027)
```

### 4️⃣ Quarters and Cycles

```python
query("Q1 meeting", datetime.date(2026, 2, 13))
# Output: Q1 meeting (Today is February 13, 2026, Q1 is January 1, 2026 - March 31, 2026)

query("Q4 summary", datetime.date(2026, 2, 13))
# Output: Q4 summary (Today is February 13, 2026, Q4 is October 1, 2026 - December 31, 2026)
```

### 5️⃣ Complex Combined Examples

```python
# Multiple time expressions
text = "meeting tomorrow, travel next weekend, Christmas party"
result = query(text, datetime.date(2026, 2, 13))
print(result)
# Output: meeting tomorrow, travel next weekend, Christmas party (Today is February 13, 2026, tomorrow is February 14, 2026, next weekend is February 21, 2026 - February 22, 2026, Christmas is December 25, 2026)

# Comprehensive example
text = "meeting tomorrow, hotel reservation on July 15th, travel next weekend, visit museum Wednesday, buy gifts for Christmas, Q4 meeting, Easter church service"
result = query(text, datetime.date(2026, 2, 13))
# All time expressions will be correctly recognized and annotated
```

## 🗓️ Holiday Query API

`holiday(scope, today)` queries Chinese public holidays and normal weekends within a given time range. Workdays-on-weekends (调休上班) are excluded to keep the output clean.

```python
from fcalendar import holiday
import datetime

# Next month's holidays
result = holiday("next_month", datetime.date(2026, 3, 31))
# [{'type': 'holiday', 'name': '清明节', 'start': '2026-04-04', 'end': '2026-04-06', 'days': 3},
#  {'type': 'weekend', 'name': '周末', 'start': '2026-04-11', 'end': '2026-04-12', 'days': 2}, ...]

# This week
holiday("this_week")
holiday("本周")       # Chinese scope also supported

# Next 3 weeks / 2 months
holiday("weeks=3")
holiday("三周")        # Chinese numeral
holiday("months=2")
holiday("未来两个月")
```

**Return fields per record:**

| Field | Type | Description |
|-------|------|-------------|
| `type` | str | `"holiday"` (public holiday) or `"weekend"` (normal restful weekend) |
| `name` | str | Name, e.g. `"劳动节"`, `"周末"` |
| `start` | str | Start date, ISO format (YYYY-MM-DD) |
| `end` | str | End date, ISO format (YYYY-MM-DD) |
| `days` | int | Number of days |

**Supported scope values:**

| Scope | Alias | Description |
|-------|-------|-------------|
| `half_year` | `半年`, `未来半年` | Next 180 days (default) |
| `this_week` | `本周`, `这周` | Current week |
| `next_week` | `下周`, `下一周` | Next week |
| `next_month` | `下个月`, `下月` | Full next month |
| `weeks=N` | `N周`, `未来N周` | Next N weeks |
| `months=N` | `N个月`, `未来N个月` | Next N months |

---

## 💻 CLI

All core features are accessible via the `fcalendar` command-line tool.

### Install

```bash
pip install fcalendar
```

### Commands

```bash
# Time expression recognition → single-line JSON output
fcalendar query "Spring Festival travel plan"
# {"input": "Spring Festival travel plan", "result": "Spring Festival travel plan (Today is ..., Spring Festival is ...)"}

fcalendar query "下周一开会" --today 2026-03-31
fcalendar query "meeting next Monday" --lang en

# Holiday query → JSON array output
fcalendar holiday                            # default: next 180 days
fcalendar holiday --scope this_week
fcalendar holiday --scope 本周              # Chinese scope
fcalendar holiday --scope weeks=3
fcalendar holiday --scope 未来两个月
fcalendar holiday --scope next_month --today 2026-09-01

# Help
fcalendar --help
fcalendar query --help
fcalendar holiday --help
```

---

## 🛠️ Development

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v

# Run benchmark tests
uv run pytest tests/test_benchmark.py::test_benchmark_cases -v -s

# Run a single test
uv run pytest tests/test_benchmark.py::test_basic_query -v
```

### Test Coverage

The project contains **44+ test cases** covering all time expression types:

- ✅ Relative time (tomorrow, next week, next month)
- ✅ Real-time keywords (current time, now, etc.)
- ✅ Chinese legal holidays
- ✅ Lunar calendar dates and traditional festivals
- ✅ Western festivals
- ✅ 24 solar terms
- ✅ Seasons and quarters
- ✅ Specific dates
- ✅ Year prefixes (last year, next year, 2024, etc.)
- ✅ Complex combined expressions
- ✅ Holiday query (public holidays + weekends)
- ✅ Chinese scope expressions (本周, 未来三周, etc.)

Run tests to see detailed results:

```bash
$ uv run pytest tests/test_benchmark.py::test_benchmark_cases -v -s

============================================================
开始运行 Benchmark 测试，共 47 个用例
============================================================

✅ [relative_weekday_01] PASSED
✅ [relative_weekend_01] PASSED
✅ [holiday_spring_festival_01] PASSED
✅ [current_time_01] PASSED
...
============================================================
测试完成！
============================================================
总计: 47 个用例
成功: 47 个 (100.0%)
失败: 0 个 (0.0%)
============================================================
```

## 📋 Dependencies

- Python >= 3.10
- chinesecalendar >= 1.9.0 (Chinese legal holiday data)
- lunardate >= 0.2.2 (Lunar calendar date conversion)

## 📂 Project Structure

```
fcalendar/
├── fcalendar/               # Core package
│   ├── __init__.py          # Package initialization, exports query / holiday
│   ├── core.py              # Core time annotation and holiday query logic
│   └── cli.py               # CLI entry point (fcalendar command)
├── fcalendar-skill/         # AI Agent skill documentation
│   └── SKILL.md             # Skill config for AI Agent integration
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── benchmark.json       # Test case data (200+ cases)
│   └── test_benchmark.py    # Test code (44+ test functions)
├── setup.py                 # Traditional packaging configuration
├── pyproject.toml           # Modern packaging configuration (uv)
├── publish.sh               # Publishing script (Aliyun PyPI)
└── README.md                # Project documentation
```

## 🔧 Core Functions

### `annotate_time_expressions(text, today=None, lang=None)`

Main function that recognizes and annotates time expressions in text.

**Parameters:**
- `text` (str): Text to be annotated
- `today` (datetime.date, optional): Reference date, defaults to current date
- `lang` (str, optional): Language code ('zh' for Chinese, 'en' for English). If None, automatically detects language

**Returns:**
- str: Annotated text in format `original text (context information)`

**Features:**
- **Multi-language support**: Automatically detects input language and returns output in the same language
- Automatically deduplicates overlapping annotations, keeping longer (more specific) expressions
- Supports simultaneous annotation of multiple time expressions
- Preserves original text integrity, adding annotation information in parentheses
- Supports real-time queries (returns Beijing time when `today` parameter is not provided)

### `query(text, today=None, lang=None)`

Convenience function, alias for `annotate_time_expressions`.

**Parameters:**
- `text` (str): Text to be annotated
- `today` (datetime.date, optional): Reference date, defaults to current date
- `lang` (str, optional): Language code ('zh' for Chinese, 'en' for English). If None, automatically detects language

## 🚀 Publishing

Use the provided publishing script:

```bash
bash publish.sh
```

## 📌 Version Management

Current version: **0.11.0**

Version numbers need to be synchronized in the following locations:
- `__version__` in `fcalendar/__init__.py`
- `version` in `pyproject.toml`
- `setup.py` automatically reads version from `__init__.py`

## 🙏 Acknowledgements

This project is built upon the following open-source libraries:

- [**chinese-calendar**](https://github.com/LKI/chinese-calendar) — Chinese legal holiday data for Python, by [@LKI](https://github.com/LKI). Used for accurate Chinese public holiday and workday-on-weekend detection.
- [**python-lunardate**](https://github.com/lidaobing/python-lunardate) — Lunar calendar date conversion for Python, by [@lidaobing](https://github.com/lidaobing). Used for converting between lunar and Gregorian dates, powering traditional festival and lunar date recognition.

---

## 📄 License

MIT License



## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📝 Changelog

### v0.12.0
- ✨ Added `holiday()` API: query Chinese public holidays and weekends within a specified range
- ✨ Added CLI (`fcalendar query` / `fcalendar holiday`): all core features accessible via command line
- ✨ `holiday()` scope supports Chinese and English, including Chinese numerals (一、两、三...十二)
- ✨ Added `fcalendar-skill/SKILL.md` for AI Agent integration
- 📝 Updated documentation and test coverage (44+ test functions)

### v0.11.0
- ✨ Added real-time keyword support (current time, now, etc.)
- ✨ Support for multiple stacking expressions (week after next, three days from now, etc.)
- 🐛 Fixed edge cases in lunar date recognition
- 📝 Improved documentation and test cases
- 🎨 Optimized annotation format for better readability

[English](README.md) | 简体中文

强大的中文时间表达式识别与标注 Python 库，同时提供中国节假日查询能力和 CLI 命令行工具。

## ✨ 功能特性

- 🎯 **智能时间识别**：自动识别文本中的各种中文时间表达式
- ⏰ **实时时间支持**：支持"当前时间"、"现在"等实时时间关键词，返回北京时间
- 📅 **中国法定节假日**：自动识别并标注法定节假日日期范围（春节、国庆等）
- 🌙 **农历日期支持**：支持农历日期和传统节日（正月十五、七夕、中秋等）
- 🌍 **西方节日**：支持西方节日识别（圣诞节、复活节、感恩节等）
- 🌸 **二十四节气**：支持二十四节气日期计算（春分、冬至等）
- 🔄 **相对时间**：支持相对时间表达（明天、后天、大后天、下周、下个月等）
- 📊 **季度和季节**：支持 Q1-Q4、上半年/下半年、春夏秋冬等表达
- 🔢 **年份前缀**：支持"去年"、"明年"、"2024年"等年份前缀
- 🎨 **灵活叠加**：支持"下下周"、"大大后天"等多重叠加表达
- 📝 **上下文标注**：在原文末尾添加括号标注，保持原文完整性

## 📦 安装

### 从 PyPI 安装

```bash
pip install fcalendar
```

### 从 Aliyun PyPI 安装（内网）

```bash
pip install fcalendar 

### 从源码安装

```bash
git clone https://github.com/youngfreefjs/fcalendar.git
cd fcalendar
pip install -e .
```
## 🚀 快速开始

### Python API

```python
from fcalendar import query, holiday
import datetime

# 时间表达式识别
result = query("明天开会", datetime.date(2026, 2, 13))
print(result)
# 输出: 明天开会（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日）

# 节假日查询
result = holiday("next_month", datetime.date(2026, 3, 31))
print(result)
# 输出: [{'type': 'holiday', 'name': '清明节', 'start': '2026-04-04', 'end': '2026-04-06', 'days': 3}, ...]
```

### CLI 命令行

```bash
# 时间表达式识别
fcalendar query "下周一开会"
# 输出: {"input": "下周一开会", "result": "下周一开会（今天是...，下周一是2026年4月6日）"}

# 节假日查询（支持中英文 scope）
fcalendar holiday --scope next_month
fcalendar holiday --scope 本周
fcalendar holiday --scope "weeks=3"
fcalendar holiday --scope 未来两个月
```
### 实时时间查询

```python
# 查询当前时间（返回北京时间）
result = query("现在是几点")
print(result)
# 输出: 现在是几点（今天是2026 年 3 月 24 日，现在是2026 年 3 月 24 日 21:35:42）

# 支持多种当前时间关键词
keywords = ["当前时间", "现在", "当前", "目前", "此时", "此刻", "眼下", "当下", "这会儿", "这时候", "今天"]
```

## 📖 支持的时间表达式

### 1️⃣ 相对时间

```python
query("明天开会", datetime.date(2026, 2, 13))
# 输出: 明天开会（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日）

query("后天有个面试", datetime.date(2026, 2, 13))
# 输出: 后天有个面试（今天是2026 年 2 月 13 日，后天是2026 年 2 月 15 日）

query("大后天回老家", datetime.date(2026, 2, 13))
# 输出: 大后天回老家（今天是2026 年 2 月 13 日，大后天是2026 年 2 月 16 日）

query("大大后天出发", datetime.date(2026, 2, 13))
# 输出: 大大后天出发（今天是2026 年 2 月 13 日，大大后天是2026 年 2 月 17 日）

query("下周四去香港", datetime.date(2026, 2, 13))
# 输出: 下周四去香港（今天是2026 年 2 月 13 日，下周四是2 月 19 日）

query("下下周末去旅游", datetime.date(2026, 2, 13))
# 输出: 下下周末去旅游（今天是2026 年 2 月 13 日，下下周末是2026 年 2 月 28 日-2026 年 3 月 1 日）

query("下个月搬家", datetime.date(2026, 2, 13))
# 输出: 下个月搬家（今天是2026 年 2 月 13 日，下个月是2026 年 3 月 1 日-2026 年 3 月 31 日）

query("下下个月入职", datetime.date(2026, 2, 13))
# 输出: 下下个月入职（今天是2026 年 2 月 13 日，下下个月是2026 年 4 月 1 日-2026 年 4 月 30 日）

query("周三参观博物馆", datetime.date(2026, 2, 13))
# 输出: 周三参观博物馆（今天是2026 年 2 月 13 日，周三是2026 年 2 月 18 日）
```

### 2️⃣ 中国法定节假日

```python
query("春节去日本", datetime.date(2026, 2, 13))
# 输出: 春节去日本（今天是2026 年 2 月 13 日，春节是2026 年 2 月 15 日-2026 年 2 月 23 日）

query("国庆节出去旅游", datetime.date(2026, 2, 13))
# 输出: 国庆节出去旅游（今天是2026 年 2 月 13 日，国庆节是2026 年 10 月 1 日-2026 年 10 月 8 日）

query("劳动节去三亚", datetime.date(2026, 2, 13))
# 输出: 劳动节去三亚（今天是2026 年 2 月 13 日，劳动节是2026 年 5 月 1 日-2026 年 5 月 5 日）

query("端午节回家", datetime.date(2026, 2, 13))
# 输出: 端午节回家（今天是2026 年 2 月 13 日，端午节是2026 年 6 月 19 日-2026 年 6 月 21 日）

query("中秋节团圆", datetime.date(2026, 2, 13))
# 输出: 中秋节团圆（今天是2026 年 2 月 13 日，中秋节是2026 年 9 月 25 日-2026 年 9 月 27 日）

query("去年春节在哪过的", datetime.date(2026, 2, 13))
# 输出: 去年春节在哪过的（今天是2026 年 2 月 13 日，去年春节是2025 年 1 月 28 日-2025 年 2 月 3 日）

query("2024年国庆节", datetime.date(2026, 2, 13))
# 输出: 2024年国庆节（今天是2026 年 2 月 13 日，2024年国庆节是2024 年 10 月 1 日-2024 年 10 月 7 日）
```

### 3️⃣ 农历日期和传统节日

```python
# 农历日期（中文格式）
query("正月十五看花灯", datetime.date(2026, 2, 13))
# 输出: 正月十五看花灯（今天是2026 年 2 月 13 日，正月十五是2026 年 3 月 3 日）

query("八月十五回家团圆", datetime.date(2026, 3, 15))
# 输出: 八月十五回家团圆（今天是2026 年 3 月 15 日，八月十五是2026 年 9 月 25 日）

query("腊月二十三祭灶", datetime.date(2026, 2, 13))
# 输出: 腊月二十三祭灶（今天是2026 年 2 月 13 日，腊月二十三是2027 年 1 月 31 日）

query("三月初三上巳节", datetime.date(2026, 3, 15))
# 输出: 三月初三上巳节（今天是2026 年 3 月 15 日，三月初三是2026 年 4 月 19 日）

# 农历日期（数字格式）
query("农历8月15日赏月", datetime.date(2026, 3, 15))
# 输出: 农历8月15日赏月（今天是2026 年 3 月 15 日，农历8月15日是2026 年 9 月 25 日）

query("阴历三月十八号的票", datetime.date(2026, 3, 15))
# 输出: 阴历三月十八号的票（今天是2026 年 3 月 15 日，阴历三月十八是2026 年 5 月 4 日）

# 传统节日
query("元宵节去哪玩", datetime.date(2026, 2, 13))
# 输出: 元宵节去哪玩（今天是2026 年 2 月 13 日，元宵节是2026 年 3 月 3 日）

query("七夕去约会", datetime.date(2026, 3, 15))
# 输出: 七夕去约会（今天是2026 年 3 月 15 日，七夕是2026 年 8 月 19 日）

query("重阳节登高", datetime.date(2026, 3, 15))
# 输出: 重阳节登高（今天是2026 年 3 月 15 日，重阳是2026 年 10 月 18 日）

query("去年元宵节", datetime.date(2026, 2, 13))
# 输出: 去年元宵节（今天是2026 年 2 月 13 日，去年元宵节是2025 年 2 月 12 日）
```

### 4️⃣ 西方节日

```python
query("圣诞节买礼物", datetime.date(2026, 2, 13))
# 输出: 圣诞节买礼物（今天是2026 年 2 月 13 日，圣诞节是2026 年 12 月 25 日）

query("万圣节去哪玩", datetime.date(2026, 2, 13))
# 输出: 万圣节去哪玩（今天是2026 年 2 月 13 日，万圣节是2026 年 10 月 31 日）

query("情人节送什么花", datetime.date(2026, 2, 13))
# 输出: 情人节送什么花（今天是2026 年 2 月 13 日，情人节是2026 年 2 月 14 日）

query("复活节去教堂", datetime.date(2026, 2, 13))
# 输出: 复活节去教堂（今天是2026 年 2 月 13 日，复活节是2026 年 4 月 5 日）

query("感恩节聚餐", datetime.date(2026, 2, 13))
# 输出: 感恩节聚餐（今天是2026 年 2 月 13 日，感恩节是2026 年 11 月 26 日）

query("愚人节整蛊", datetime.date(2026, 2, 13))
# 输出: 愚人节整蛊（今天是2026 年 2 月 13 日，愚人节是2026 年 4 月 1 日）

query("2024年圣诞节", datetime.date(2026, 2, 13))
# 输出: 2024年圣诞节（今天是2026 年 2 月 13 日，2024年圣诞节是2024 年 12 月 25 日）
```

### 5️⃣ 季节和节气

```python
# 季节
query("冬季去滑雪", datetime.date(2026, 2, 13))
# 输出: 冬季去滑雪（今天是2026 年 2 月 13 日，冬季是2026 年 12 月 1 日-2027 年 2 月 28 日）

query("夏天去海边", datetime.date(2026, 2, 13))
# 输出: 夏天去海边（今天是2026 年 2 月 13 日，夏天是2026 年 6 月 1 日-2026 年 8 月 31 日）

query("春季踏青", datetime.date(2026, 2, 13))
# 输出: 春季踏青（今天是2026 年 2 月 13 日，春季是2026 年 3 月 1 日-2026 年 5 月 31 日）

query("秋天赏枫", datetime.date(2026, 2, 13))
# 输出: 秋天赏枫（今天是2026 年 2 月 13 日，秋天是2026 年 9 月 1 日-2026 年 11 月 30 日）

# 二十四节气
query("春分去踏青", datetime.date(2026, 2, 13))
# 输出: 春分去踏青（今天是2026 年 2 月 13 日，春分是2026 年 3 月 20 日）

query("冬至吃饺子", datetime.date(2026, 2, 13))
# 输出: 冬至吃饺子（今天是2026 年 2 月 13 日，冬至是2026 年 12 月 21 日）

query("立春迎新", datetime.date(2026, 2, 13))
# 输出: 立春迎新（今天是2026 年 2 月 13 日，立春是2026 年 2 月 4 日）

query("夏至日最长", datetime.date(2026, 2, 13))
# 输出: 夏至日最长（今天是2026 年 2 月 13 日，夏至是2026 年 6 月 21 日）
```

### 6️⃣ 季度和周期

```python
query("Q1开会", datetime.date(2026, 2, 13))
# 输出: Q1开会（今天是2026 年 2 月 13 日，Q1是2026 年 1 月 1 日-2026 年 3 月 31 日）

query("Q4总结", datetime.date(2026, 2, 13))
# 输出: Q4总结（今天是2026 年 2 月 13 日，Q4是2026 年 10 月 1 日-2026 年 12 月 31 日）

query("上半年完成目标", datetime.date(2026, 2, 13))
# 输出: 上半年完成目标（今天是2026 年 2 月 13 日，上半年是2026 年 1 月 1 日-2026 年 6 月 30 日）

query("下半年规划", datetime.date(2026, 2, 13))
# 输出: 下半年规划（今天是2026 年 2 月 13 日，下半年是2026 年 7 月 1 日-2026 年 12 月 31 日）

query("S1发布", datetime.date(2026, 2, 13))
# 输出: S1发布（今天是2026 年 2 月 13 日，S1是2026 年 1 月 1 日-2026 年 6 月 30 日）

query("2024年Q3", datetime.date(2026, 2, 13))
# 输出: 2024年Q3（今天是2026 年 2 月 13 日，2024年Q3是2024 年 7 月 1 日-2024 年 9 月 30 日）
```

### 7️⃣ 具体日期

```python
# 公历日期
query("7月15日出发", datetime.date(2026, 2, 13))
# 输出: 7月15日出发（今天是2026 年 2 月 13 日，7月15日是2026 年 7 月 15 日）

query("2023年7月15日去旅行", datetime.date(2026, 2, 13))
# 输出: 2023年7月15日去旅行（今天是2026 年 2 月 13 日，2023年7月15日是2023 年 7 月 15 日）

query("阳历8月8日", datetime.date(2026, 2, 13))
# 输出: 阳历8月8日（今天是2026 年 2 月 13 日，阳历8月8日是2026 年 8 月 8 日）

# 月份
query("7月去哪玩", datetime.date(2026, 2, 13))
# 输出: 7月去哪玩（今天是2026 年 2 月 13 日，7月是2026 年 7 月 1 日-2026 年 7 月 31 日）

query("三月赏花", datetime.date(2026, 2, 13))
# 输出: 三月赏花（今天是2026 年 2 月 13 日，三月是2026 年 3 月 1 日-2026 年 3 月 31 日）
```

### 8️⃣ 复杂组合示例

```python
# 多个时间表达式
text = "明天开会，下周末去旅游，春节飞日本"
result = query(text, datetime.date(2026, 2, 13))
print(result)
# 输出: 明天开会，下周末去旅游，春节飞日本（今天是2026 年 2 月 13 日，明天是2026 年 2 月 14 日，下周末是2026 年 2 月 21 日-2026 年 2 月 22 日，春节是2026 年 2 月 15 日-2026 年 2 月 23 日）

# 综合示例
text = "明天和朋友去7月15日预定的巴黎酒店，下周末去杭州，春节飞日本，周三逛博物馆，正月十五看花灯，圣诞节买礼物，Q4开会，复活节去教堂"
result = query(text, datetime.date(2026, 2, 13))
# 所有时间表达式都会被正确识别和标注
```

## 🗓️ 节假日查询 API

`holiday(scope, today)` 查询指定范围内的中国法定节假日和可休息的普通周末，调休上班不纳入结果。

```python
from fcalendar import holiday
import datetime

# 下个月的节假日
result = holiday("next_month", datetime.date(2026, 3, 31))
# [{'type': 'holiday', 'name': '清明节', 'start': '2026-04-04', 'end': '2026-04-06', 'days': 3},
#  {'type': 'weekend', 'name': '周末', 'start': '2026-04-11', 'end': '2026-04-12', 'days': 2}, ...]

# 本周
holiday("this_week")
holiday("本周")       # 中文 scope 同样支持

# 未来 3 周 / 2 个月
holiday("weeks=3")
holiday("三周")        # 中文数字
holiday("months=2")
holiday("未来两个月")
```

**返回字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | str | `"holiday"`（法定假期）或 `"weekend"`（普通可休息周末） |
| `name` | str | 名称，如 `"劳动节"`、`"周末"` |
| `start` | str | 起始日期，ISO 格式（YYYY-MM-DD） |
| `end` | str | 结束日期，ISO 格式（YYYY-MM-DD） |
| `days` | int | 天数 |

**scope 支持格式：**

| 英文格式 | 中文别名 | 说明 |
|----------|----------|------|
| `half_year` | `半年`, `未来半年` | 未来 180 天（默认） |
| `this_week` | `本周`, `这周` | 本周（周一至周日） |
| `next_week` | `下周`, `下一周` | 下周（周一至周日） |
| `next_month` | `下个月`, `下月` | 下个自然月 |
| `weeks=N` | `N周`, `未来N周` | 未来 N 周 |
| `months=N` | `N个月`, `未来N个月` | 未来 N 个月 |

---

## 💻 CLI 命令行工具

fcalendar 所有核心能力均可通过 `fcalendar` 命令行工具调用。

### 安装

```bash
pip install fcalendar
```

### 命令用法

```bash
# 时间表达式识别 → 单行 JSON 输出
fcalendar query "春节去哪里旅游"
# {"input": "春节去哪里旅游", "result": "春节去哪里旅游（今天是...，春节是...）"}

fcalendar query "下周一开会" --today 2026-03-31
fcalendar query "meeting next Monday" --lang en

# 节假日查询 → JSON 数组输出
fcalendar holiday                            # 默认：未来 180 天
fcalendar holiday --scope this_week
fcalendar holiday --scope 本周              # 中文 scope
fcalendar holiday --scope weeks=3
fcalendar holiday --scope 未来两个月
fcalendar holiday --scope next_month --today 2026-09-01

# 帮助
fcalendar --help
fcalendar query --help
fcalendar holiday --help
```

---

## 🛠️ 开发

本项目使用 `uv` 进行依赖管理：

```bash
# 安装依赖
uv sync

# 运行所有测试
uv run pytest tests/ -v

# 运行 benchmark 测试
uv run pytest tests/test_benchmark.py::test_benchmark_cases -v -s

# 运行单个测试
uv run pytest tests/test_benchmark.py::test_basic_query -v
```

### 测试覆盖

项目包含 **44+ 个测试用例**，覆盖所有时间表达式类型：

- ✅ 相对时间（明天、下周、下个月）
- ✅ 实时时间关键词（当前时间、现在等）
- ✅ 中国法定节假日
- ✅ 农历日期和传统节日
- ✅ 西方节日
- ✅ 二十四节气
- ✅ 季节和季度
- ✅ 具体日期
- ✅ 年份前缀（去年、明年、2024年等）
- ✅ 复杂组合表达
- ✅ 节假日查询（法定假期 + 周末）
- ✅ 中文 scope 表达式（本周、未来三周等）

运行测试查看详细结果：

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

## 📋 依赖

- Python >= 3.10
- chinesecalendar >= 1.9.0（中国法定节假日数据）
- lunardate >= 0.2.2（农历日期转换）

## 📂 项目结构

```
fcalendar/
├── fcalendar/               # 核心包
│   ├── __init__.py          # 包初始化，导出 query / holiday
│   ├── core.py              # 核心时间标注和节假日查询逻辑
│   └── cli.py               # CLI 入口（fcalendar 命令）
├── fcalendar-skill/         # AI Agent Skill 文档
│   └── SKILL.md             # Skill 配置，供 AI Agent 集成使用
├── tests/                   # 测试套件
│   ├── __init__.py
│   ├── benchmark.json       # 测试用例数据（200+ 个用例）
│   └── test_benchmark.py    # 测试代码（44+ 个测试函数）
├── setup.py                 # 传统打包配置
├── pyproject.toml           # 现代打包配置（uv）
└── README.md                # 项目文档
```

## 🔧 核心功能说明

### `annotate_time_expressions(text, today=None)`

主函数，识别并标注文本中的时间表达式。

**参数：**
- `text` (str): 待标注的文本
- `today` (datetime.date, optional): 参考日期，默认为当前日期

**返回：**
- str: 标注后的文本，格式为 `原文（今天是X，时间表达1是Y，时间表达2是Z）`

**特性：**
- 自动去重重叠的标注，保留更长（更具体）的表达
- 支持多个时间表达式同时标注
- 保持原文完整性，标注信息添加在括号中
- 支持实时时间查询（不传 `today` 参数时返回北京时间）

### `query(text, today=None)`

便捷函数，`annotate_time_expressions` 的别名。

## 🚀 发布

使用提供的发布脚本：

```bash
bash publish.sh
```

## 📌 版本管理

当前版本：**0.11.0**

版本号需要在以下位置保持同步：
- `fcalendar/__init__.py` 中的 `__version__`
- `pyproject.toml` 中的 `version`
- `setup.py` 会自动从 `__init__.py` 读取版本号

## 🙏 致谢

本项目基于以下优秀的开源库构建，感谢作者的贡献：

- [**chinese-calendar**](https://github.com/LKI/chinese-calendar) — 中国法定节假日 Python 数据库，作者 [@LKI](https://github.com/LKI)。用于准确识别中国法定假期和调休工作日。
- [**python-lunardate**](https://github.com/lidaobing/python-lunardate) — 农历日期转换 Python 库，作者 [@lidaobing](https://github.com/lidaobing)。用于农历与公历之间的互转，支撑传统节日和农历日期的识别功能。

---

## 📄 许可证

MIT License


## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

### v0.12.0
- ✨ 新增 `holiday()` API：查询指定范围内的中国法定节假日和周末
- ✨ 新增 CLI（`fcalendar query` / `fcalendar holiday`）：所有核心能力支持命令行调用
- ✨ `holiday()` 的 scope 参数支持中英文及中文数字（一、两、三...十二）
- ✨ 新增 `fcalendar-skill/SKILL.md`，支持 AI Agent 集成
- 📝 更新文档，测试覆盖率提升（44+ 个测试函数）

### v0.11.0
- ✨ 新增实时时间关键词支持（当前时间、现在等）
- ✨ 支持多重叠加表达（下下周、大大后天等）
- 🐛 修复农历日期识别的边界情况
- 📝 完善文档和测试用例
- 🎨 优化标注格式，提升可读性
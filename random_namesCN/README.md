# 随机中文姓名生成包 (random-namesCN)

一个轻量级 Python 工具包，用于**随机生成中文姓名**。支持单姓、复姓与单字名、双字名、三字名的任意组合，可生成 2~5 字姓名。姓/名字典与代码分离，所有数据维护在包内 `data/*.csv` 中，便于独立扩充。

---

## ✨ 主要功能

- **6 种组合全覆盖**：单姓 / 复姓 × 单字名 / 双字名 / 三字名，得到 2~5 字姓名。
- **参数化生成**：`random_chinese_name(surname_type, given_name_len)` 可指定姓类型与名长度，留空则随机。
- **快捷别名函数**：`random_two_name` 等 6 个便捷函数按固定组合直接调用。
- **数据/代码分离**：姓、名字典以 CSV 形式存放在包内 `data/` 目录，单独维护无需改代码。
- **纯标准库实现**：仅依赖 `random` / `pkgutil`，无任何第三方依赖。

---

## 📦 安装

本包为自用包，直接在源码目录下安装即可。

### 方式一：常规安装

```bash
cd random_namesCN
pip install .
```

### 方式二：开发模式（可编辑安装，修改源码立即生效）

```bash
cd random_namesCN
pip install -e .
```

---

## 🚀 快速开始

```python
from random_namesCN import random_chinese_name, random_chinese_name_parts

# 不传参：6 种组合中随机选一种
print(random_chinese_name())  # 如：东方丽彤

# 指定姓类型与名长度
print(random_chinese_name("single", 1))     # 单姓 + 单字名 = 2 字，如：赵丽
print(random_chinese_name("single", 2))     # 单姓 + 双字名 = 3 字，如：赵辉宸
print(random_chinese_name("single", 3))     # 单姓 + 三字名 = 4 字，如：赵丁炎炎
print(random_chinese_name("compound", 1))   # 复姓 + 单字名 = 3 字，如：公良丽
print(random_chinese_name("compound", 2))   # 复姓 + 双字名 = 4 字，如：公良辉宸
print(random_chinese_name("compound", 3))   # 复姓 + 三字名 = 5 字，如：公良丁炎炎

# 姓、名分开返回（便于做称呼拼接、姓替换等）
surname, given = random_chinese_name_parts("compound", 2)
print(surname, given)              # 如：公良 辉宸
print(surname + "女士")            # 如：公良女士
print(surname[0] + "女士")         # 如：公女士（复姓缩写）
```

---

## 🧩 组合矩阵

| 姓 \ 名      | 单字名 | 双字名 | 三字名 |
|--------------|--------|--------|--------|
| **单姓**     | 2 字   | 3 字   | 4 字   |
| **复姓**     | 3 字   | 4 字   | 5 字   |

---

## 📚 API

### `random_chinese_name_parts(surname_type=None, given_name_len=None)`

主入口，生成随机中文名字，返回 **(姓, 名) 元组**，便于后续做姓替换、称呼拼接（如 `欧阳女士` / `欧女士`）等处理。

| 参数 | 类型 | 说明 |
|------|------|------|
| `surname_type` | `str` / `None` | `'single'`(单姓) / `'compound'`(复姓)，`None` 表示随机 |
| `given_name_len` | `int` / `None` | `1` / `2` / `3`，`None` 表示随机 |

**返回值：** `(surname, given)` 元组。非法参数会抛 `ValueError`。

### `random_chinese_name(surname_type=None, given_name_len=None)`

`random_chinese_name_parts` 的薄封装，把 `(姓, 名)` 拼成完整姓名字符串。

### 快捷别名

| 函数 | 组合 | 字数 |
|------|------|------|
| `random_two_name()` | 单姓 + 单字名 | 2 |
| `random_three_name()` | 单姓 + 双字名 | 3 |
| `random_three_names()` | 复姓 + 单字名 | 3 |
| `random_four_name()` | 复姓 + 双字名 | 4 |
| `random_four_name_single()` | 单姓 + 三字名 | 4 |
| `random_five_name()` | 复姓 + 三字名 | 5 |

---

## ⚠️ 异常

- `surname_type` 非 `'single'` / `'compound'` → 抛出 `ValueError`。
- `given_name_len` 非 `1` / `2` / `3` → 抛出 `ValueError`。
- 包内 `data/*.csv` 文件缺失 → 抛出 `FileNotFoundError`。

---

## 🗂️ 数据维护

所有姓名字典以 CSV 形式存放在包内 `random_namesCN/data/`，每行一个条目：

| 文件 | 内容 | 条目数 |
|------|------|--------|
| `单字姓.csv` | 单字姓（赵、钱、孙 …） | 832 |
| `复姓.csv` | 复姓（公良、宇文 …） | 101 |
| `单字名.csv` | 单字名（丽、云、亮 …） | 79 |
| `双字名.csv` | 双字名（辉宸、云萱 …） | 3125 |
| `三字名.csv` | 三字名（丁炎炎、泽晴英 …） | 8000 |

要增删名字，直接编辑对应 CSV 文件即可，**无需修改 Python 代码**。打包时通过 `setup.py` 的 `package_data` 自动包含 `data/*.csv`。

---

## 📁 模块结构

```
random_namesCN/
├── README.md
├── setup.py
├── tests/
│   └── test_random_name.py    # 单元测试
└── random_namesCN/
    ├── __init__.py            # 导出主要 API
    ├── random_name.py         # 生成逻辑
    └── data/                  # 姓/名字典（CSV）
        ├── 单字姓.csv
        ├── 复姓.csv
        ├── 单字名.csv
        ├── 双字名.csv
        └── 三字名.csv
```

---

## 🧪 测试

使用 Python 标准库 `unittest`，无需额外依赖：

```bash
cd random_namesCN
python -m unittest tests.test_random_name -v
```

---

## 📝 License

MIT © 2026 Soleil

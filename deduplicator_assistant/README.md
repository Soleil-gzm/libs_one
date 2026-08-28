# 对话去重工具包 (deduplicator-assistant)

一个轻量级 Python 工具包，用于**检测并删除对话中相邻且重复/高度相似的 `user + assistant` 轮次**，同时支持**单独分析重复情况**。特别适用于客服对话、聊天记录等场景。

---

## ✨ 主要功能

- **去重处理** (`process`)：原地修改对话列表，删除相邻重复的 `assistant` 轮次及其前面的 `user` 轮次，保留第一次出现。
- **重复检测** (`analyze_file` / `find_adjacent_duplicates`)：分析数据，找出所有包含相邻重复 `assistant` 的对话，并输出重复详情（索引、内容、相似度），不会修改原数据。
- **灵活配置**：可自定义相似度阈值（0.0~1.0），可选择忽略数字（金额、日期等占位符），适应不同业务需求。
- **内存友好**：支持原地修改，也可返回统计信息。

---

## 📦 安装

### 方式一：通过 Git 安装（推荐）

```bash
pip install git+https://github.com/你的用户名/deduplicator-assistant.git
```

### 方式二：本地开发模式（便于修改源码）

```bash
git clone https://github.com/你的用户名/deduplicator-assistant.git
cd deduplicator-assistant
pip install -e .
```

---

## 🚀 快速开始

### 1. 数据格式要求

输入数据应为 **JSON 数组**，每个元素是一个对话对象，至少包含 `"messages"` 字段，`messages` 是一个列表，每条消息包含 `"role"`（`system`/`user`/`assistant`）和 `"content"` 字符串。

**示例：**
```json
[
  {
    "messages": [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "你好"},
      {"role": "assistant", "content": "您好，请问有什么可以帮助您？"},
      {"role": "user", "content": "我想查询账单"},
      {"role": "assistant", "content": "您好，请问有什么可以帮助您？"}   // 与上一条 assistant 重复
    ]
  }
]
```

---

### 2. 去重处理（删除重复轮次）

```python
import json
from deduplicator_assistant import process

# 读取数据
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 去重（原地修改 data）
processed_data, stats = process(
    data,
    threshold=0.85,          # 相似度阈值，0.85 表示相似度 ≥ 85% 即视为重复
    ignore_numbers=True,     # 忽略数字（金额、日期等）
    return_stats=True        # 返回统计信息
)

print(f"删除了 {stats['removed_pairs']} 对重复轮次")
print(f"修改了 {stats['modified_dialogues']} 个对话")

# 保存结果
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=2)
```

**参数说明：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | `list` | 必填 | 对话列表（JSON 数组） |
| `threshold` | `float` | `1.0` | 相似度阈值，范围 0.0~1.0 |
| `ignore_numbers` | `bool` | `True` | 是否忽略数字（仅比较文字部分） |
| `return_stats` | `bool` | `False` | 是否返回统计信息；若为 `True`，返回 `(data, stats)`，否则仅返回 `data` |

**统计信息字典：**
- `total_dialogues`：总对话数
- `duplicate_dialogues`：存在重复的对话数
- `removed_pairs`：总共删除的 `(user + assistant)` 轮对数
- `modified_dialogues`：实际被修改的对话数

---

### 3. 分析重复情况（只检测，不修改）

如果您只想查看哪些对话存在重复，而不删除它们，可以使用分析功能。

#### 3.1 分析整个数据列表（内存操作）

```python
from deduplicator_assistant import find_adjacent_duplicates

with open('data.json') as f:
    data = json.load(f)

results = find_adjacent_duplicates(data, threshold=0.85, ignore_numbers=True)

for item in results:
    idx = item['dialogue_index']
    pairs = item['duplicate_pairs']
    print(f"对话 {idx} 有 {len(pairs)} 对重复 assistant")
    for idx1, idx2, c1, c2, score in pairs:
        print(f"  - 索引 {idx1} 和 {idx2} 相似度 {score:.2f}")
```

#### 3.2 直接分析 JSON 文件并保存报告

```python
from deduplicator_assistant import analyze_file

analyze_file(
    input_path='data.json',
    output_path='duplicates_report.json',
    threshold=0.85,
    ignore_numbers=True
)
```

报告文件会为每个包含重复的对话添加两个额外字段：
- `_has_adjacent_assistant_duplicate`：固定为 `True`
- `_duplicate_pairs`：重复对详情，每个元素为 `(assistant1索引, assistant2索引, 内容1, 内容2, 相似度)`

---

### 4. 检测单个对话（细粒度控制）

```python
from deduplicator_assistant import find_adjacent_duplicates_in_dialogue

messages = [...]  # 一个对话的 messages 列表
pairs = find_adjacent_duplicates_in_dialogue(messages, threshold=0.85)

if pairs:
    print("发现重复 assistant 轮次：")
    for idx1, idx2, c1, c2, score in pairs:
        print(f"  {idx1} ↔ {idx2} (相似度 {score:.2f})")
```

---

## 🧠 去重逻辑详解

- **仅处理相邻的 `assistant` 轮次**：比较对话中按顺序出现的第 N 个和第 N+1 个 `assistant` 消息（它们之间可能隔着一个 `user`）。
- **保留第一个**：若判定为重复，则删除**后一个** `assistant` 及其前面的 `user` 消息。
- **连续重复压平**：对于连续多个相同/相似的 `assistant`（如 A1, A2, A3），一趟遍历即可全部删除 A2 和 A3（保留 A1），无需多次运行。
- **不受中间轮次影响**：如果两个相同的 `assistant` 被其他非重复轮次隔开（如 A1(X), A2(Y), A3(X)），当前逻辑不会跨过 A2 去匹配 A1 和 A3，因此**不会误删**，但也不会去重这种“间隔重复”。若需要，可多次运行或自行扩展。

---

## 🛠 辅助函数

如果您需要自定义相似度计算，可调用：

```python
from deduplicator_assistant import normalize_content, calculate_similarity

text1 = "欠款362.53元"
text2 = "欠款362.53元"
sim = calculate_similarity(text1, text2, ignore_numbers=True)  # 忽略数字后比较
print(sim)  # 输出 1.0
```

- `normalize_content(text, ignore_numbers)`：返回归一化后的文本（移除数字）。
- `calculate_similarity(text1, text2, ignore_numbers)`：返回相似度（0~1）。

---

## 📄 命令行工具（可选）

如果您的包配置了 `entry_points`，安装后可直接在终端使用：

```bash
deduplicate-dialogue --input data.json --output clean.json --threshold 0.85
```

目前该工具未内置，您可根据需要自行扩展（参考 `setup.py` 中的 `console_scripts` 配置）。

---

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request 到 [GitHub 仓库](https://github.com/你的用户名/deduplicator-assistant)。

---

## 📝 License

MIT © 2026 Soleil
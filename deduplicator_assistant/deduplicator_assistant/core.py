"""
对话去重模块：删除相邻且内容重复/高度相似的 user+assistant 轮次
策略：保留第一次出现的轮次，删除后续重复的轮次
支持返回统计信息
"""

import re
from difflib import SequenceMatcher
import json
from pathlib import Path


def normalize_content(text: str, ignore_numbers: bool = True) -> str:
    if ignore_numbers:
        return re.sub(r"\d+", "", text)
    return text


def calculate_similarity(text1: str, text2: str, ignore_numbers: bool = True) -> float:
    s1 = normalize_content(text1, ignore_numbers)
    s2 = normalize_content(text2, ignore_numbers)
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    return SequenceMatcher(None, s1, s2).ratio()


def is_similar(
    text1: str, text2: str, threshold: float, ignore_numbers: bool = True
) -> tuple:
    score = calculate_similarity(text1, text2, ignore_numbers)
    if threshold >= 1.0:
        return (score >= 0.9999), score
    return (score >= threshold), score


def process(
    data,
    threshold: float = 1.0,
    ignore_numbers: bool = True,
    return_stats: bool = False,
):
    """
    去除相邻且重复/高度相似的 user+assistant 轮次，保留第一次出现。

    :param data: 对话列表（json.load 后的对象），会原地修改
    :param threshold: 相似度阈值 0.0~1.0
    :param ignore_numbers: 是否忽略数字
    :param return_stats: 是否返回统计信息，默认 False 只返回处理后的数据
    :return: 如果 return_stats=False，返回处理后的 data；否则返回 (data, stats_dict)
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold 必须在 0.0~1.0 之间，当前值: {threshold}")

    stats = {
        "total_dialogues": len(data),
        "duplicate_dialogues": 0,  # 对重复的对话数
        "removed_pairs": 0,  # 删除的 user+assistant 轮对数
        "modified_dialogues": 0,  # 实际修改了 messages 的对话数
    }

    for dialogue in data:
        messages = dialogue.get("messages", [])
        if len(messages) < 4:
            continue

        assistant_indices = [
            i for i, msg in enumerate(messages) if msg.get("role") == "assistant"
        ]
        if len(assistant_indices) < 2:
            continue

        to_remove = set()
        has_dup = False
        removed_in_dialogue = 0

        # 与上一个幸存的 assistant 比较，一趟即可压平任意长度的连续重复
        last_kept_idx = None
        for idx in assistant_indices:
            if idx in to_remove:
                continue

            if last_kept_idx is None:
                last_kept_idx = idx
                continue

            content1 = messages[last_kept_idx].get("content", "")
            content2 = messages[idx].get("content", "")
            sim, _ = is_similar(content1, content2, threshold, ignore_numbers)

            if sim:
                # 标记删除当前的 assistant
                to_remove.add(idx)
                removed_in_dialogue += 1
                has_dup = True

                # 删除它前面的 user
                user_idx = idx - 1
                if user_idx >= 0 and messages[user_idx].get("role") == "user":
                    to_remove.add(user_idx)
                else:
                    for j in range(idx - 1, -1, -1):
                        if messages[j].get("role") == "user":
                            to_remove.add(j)
                            break
                # last_kept_idx 保持不变，继续与同一段幸存者比较
            else:
                last_kept_idx = idx

        if to_remove:
            dialogue["messages"] = [
                msg for idx, msg in enumerate(messages) if idx not in to_remove
            ]
            stats["modified_dialogues"] += 1

        if has_dup:
            stats["duplicate_dialogues"] += 1
            stats["removed_pairs"] += removed_in_dialogue

    if return_stats:
        return data, stats
    return data


def find_adjacent_duplicates_in_dialogue(messages, threshold=1.0, ignore_numbers=True):
    """
    检测一个对话中所有相邻的 assistant 消息对是否重复。
    返回列表，每个元素为 (idx1, idx2, content1, content2, similarity_score)
    """
    assistants = [
        (i, msg.get("content", ""))
        for i, msg in enumerate(messages)
        if msg.get("role") == "assistant"
    ]
    if len(assistants) < 2:
        return []

    duplicates = []
    for j in range(len(assistants) - 1):
        idx1, content1 = assistants[j]
        idx2, content2 = assistants[j + 1]
        sim, _ = is_similar(content1, content2, threshold, ignore_numbers)
        if sim:
            duplicates.append(
                (
                    idx1,
                    idx2,
                    content1,
                    content2,
                    calculate_similarity(content1, content2, ignore_numbers),
                )
            )
    return duplicates


def find_adjacent_duplicates(data, threshold=1.0, ignore_numbers=True):
    """
    分析整个对话列表，找出每个对话中存在的相邻 assistant 重复对。
    返回一个列表，每个元素为 dict，包含：
        - 'dialogue_index': 对话在 data 中的索引
        - 'duplicate_pairs': 重复对列表（与 find_adjacent_duplicates_in_dialogue 返回格式一致）
        - 'dialogue': 原始对话的浅拷贝（或深拷贝，根据需要）
    """
    results = []
    for idx, dialogue in enumerate(data):
        messages = dialogue.get("messages", [])
        pairs = find_adjacent_duplicates_in_dialogue(
            messages, threshold, ignore_numbers
        )
        if pairs:
            results.append(
                {
                    "dialogue_index": idx,
                    "duplicate_pairs": pairs,
                    "dialogue": dialogue.copy(),  # 浅拷贝，保留原始数据
                }
            )
    return results


def analyze_file(input_path, output_path, threshold=1.0, ignore_numbers=True):
    """
    读取 JSON 文件，分析每个对话，将包含重复 assistant 的对话保存到新文件。
    输出文件中会额外添加 '_has_adjacent_assistant_duplicate' 和 '_duplicate_pairs' 字段。
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("输入 JSON 根元素必须是列表")

    result_data = []
    for idx, dialogue in enumerate(data):
        messages = dialogue.get("messages", [])
        pairs = find_adjacent_duplicates_in_dialogue(
            messages, threshold, ignore_numbers
        )
        if pairs:
            dialogue_copy = dialogue.copy()
            dialogue_copy["_has_adjacent_assistant_duplicate"] = True
            dialogue_copy["_duplicate_pairs"] = pairs
            result_data.append(dialogue_copy)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    return result_data  # 返回保存的数据，便于后续使用

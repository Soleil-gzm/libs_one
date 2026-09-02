# -*- coding: utf-8 -*-

import random
from pkgutil import get_data


def _load_csv(filename):
    """从包内 data/ 目录加载 CSV 名字列表（每行一个）

    使用 pkgutil.get_data 读取，安装成包后也能正确找到数据文件。
    utf-8-sig 自动吞掉可能的 BOM。
    """
    raw = get_data(__package__, "data/" + filename)
    if raw is None:
        raise FileNotFoundError("无法加载包内数据文件 data/" + filename)
    text = raw.decode("utf-8-sig")
    return [line.strip() for line in text.splitlines() if line.strip()]


# 数据单独维护在 random_namesCN/data/ 下的 CSV 文件中
_last_names = _load_csv("单字姓.csv")
_compound_last_names = _load_csv("复姓.csv")
_first_names_single = _load_csv("单字名.csv")
_first_names_double = _load_csv("双字名.csv")
_first_names_triple = _load_csv("三字名.csv")

# 姓/名池查表
_SURNAME_POOLS = {"single": _last_names, "compound": _compound_last_names}
_GIVEN_POOLS = {1: _first_names_single, 2: _first_names_double, 3: _first_names_triple}


def random_chinese_name_parts(surname_type=None, given_name_len=None):
    """生成随机中文名字，返回 (姓, 名) 元组

    组合矩阵（6 种组合）：
      单姓 + 单字名 = 2 字   例：('赵', '丽')
      单姓 + 双字名 = 3 字   例：('赵', '辉宸')
      单姓 + 三字名 = 4 字   例：('赵', '丁炎炎')
      复姓 + 单字名 = 3 字   例：('公良', '丽')
      复姓 + 双字名 = 4 字   例：('公良', '辉宸')
      复姓 + 三字名 = 5 字   例：('公良', '丁炎炎')

    姓和名分开返回，便于后续做姓替换、称呼拼接（如 '欧阳女士' / '欧女士'）等处理。

    :param surname_type: 'single'(单姓) / 'compound'(复姓)，None 表示随机
    :param given_name_len: 1 / 2 / 3，None 表示随机
    :return: (surname, given) 元组
    """
    if surname_type is None:
        surname_type = random.choice(["single", "compound"])
    if given_name_len is None:
        given_name_len = random.choice([1, 2, 3])

    if surname_type not in _SURNAME_POOLS:
        raise ValueError("surname_type 必须是 'single' 或 'compound'")
    if given_name_len not in _GIVEN_POOLS:
        raise ValueError("given_name_len 必须是 1、2 或 3")

    surname = random.choice(_SURNAME_POOLS[surname_type])
    given = random.choice(_GIVEN_POOLS[given_name_len])
    return surname, given


def random_chinese_name(surname_type=None, given_name_len=None):
    """生成随机中文名字（拼接后的完整姓名字符串）

    参数与返回值说明见 :func:`random_chinese_name_parts`，本函数仅把后者返回的
    (姓, 名) 拼成一个字符串。

    :return: str
    """
    surname, given = random_chinese_name_parts(surname_type, given_name_len)
    return surname + given


def random_two_name():
    """2 字名：单姓 + 单字名"""
    return random_chinese_name("single", 1)


def random_three_name():
    """3 字名：单姓 + 双字名"""
    return random_chinese_name("single", 2)


def random_three_names():
    """3 字复姓名：复姓 + 单字名"""
    return random_chinese_name("compound", 1)


def random_four_name():
    """4 字复姓名：复姓 + 双字名"""
    return random_chinese_name("compound", 2)


def random_four_name_single():
    """4 字单姓名：单姓 + 三字名"""
    return random_chinese_name("single", 3)


def random_five_name():
    """5 字复姓名：复姓 + 三字名"""
    return random_chinese_name("compound", 3)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
纯数字口语化转换（只支持 low 模式）
- 处理整数、小数、正负数
- 通过后处理将“二”+（千/百/万/亿）且前面不是“十”的替换为“两”
- 小数部分自动去除末尾多余的零（如 100.50 → 一百点五）
"""

import re
from decimal import Decimal
from typing import Union
from warnings import warn

# ============ 常量定义 ============
NUMBER_LOW_AN2CN = {
    0: "零",
    1: "一",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "六",
    7: "七",
    8: "八",
    9: "九",
}

UNIT_LOW_ORDER_AN2CN = [
    "",
    "十",
    "百",
    "千",
    "万",
    "十",
    "百",
    "千",
    "亿",
    "十",
    "百",
    "千",
    "万",
    "十",
    "百",
    "千",
]
# ==================================


def number_to_chinese(inputs: Union[str, int, float]) -> str:
    """
    阿拉伯数字转中文小写数字（口语化）
    :param inputs: 数字，可以是字符串、整数或浮点数
    :return: 中文读法字符串
    """
    if inputs is None or inputs == "":
        raise ValueError("输入数据为空！")

    # 转换为字符串（避免科学计数法）
    if not isinstance(inputs, str):
        inputs = format(Decimal(str(inputs)), "f")

    # 校验字符是否合法（只允许数字、小数点、负号）
    if not all(c in "0123456789.-" for c in inputs):
        raise ValueError(f"输入包含非法字符：{inputs}")

    # 处理负号
    sign = ""
    if inputs[0] == "-":
        sign = "负"
        inputs = inputs[1:]

    # 分割整数和小数
    parts = inputs.split(".")
    if len(parts) == 1:
        integer_part = parts[0]
        decimal_part = ""
    elif len(parts) == 2:
        integer_part, decimal_part = parts
    else:
        raise ValueError(f"输入格式错误（多个小数点）：{inputs}")

    # 转换整数部分
    int_cn = _integer_convert(integer_part)

    # ---- 口语化后处理：把“二”+（千/百/万/亿）且前面不是“十”的替换为“两” ----
    int_cn = re.sub(r'(?<![十])二(百|千|万|亿)', r'两\1', int_cn)

    # ---- 处理小数部分（去掉末尾无意义的零） ----
    if decimal_part:
        # 去除小数部分末尾的零
        decimal_part = decimal_part.rstrip('0')
        if decimal_part:
            dec_cn = _decimal_convert(decimal_part)
        else:
            dec_cn = ""
    else:
        dec_cn = ""

    # 拼接结果
    if int_cn == "零" and dec_cn:
        result = "零" + dec_cn
    else:
        result = int_cn + dec_cn

    return sign + result


def _integer_convert(integer_data: str) -> str:
    """整数部分转换（沿用 cn2an 的 low 模式算法，只做了简单的“两”替换已在外部处理）"""
    if integer_data == "":
        return "零"
    integer_data = str(int(integer_data))  # 去除前导零
    if integer_data == "0":
        return "零"

    length = len(integer_data)
    if length > len(UNIT_LOW_ORDER_AN2CN):
        raise ValueError(f"超出支持的最大位数（{len(UNIT_LOW_ORDER_AN2CN)} 位）")

    output = ""
    for i, ch in enumerate(integer_data):
        digit = int(ch)
        unit = UNIT_LOW_ORDER_AN2CN[length - i - 1]

        if digit == 0:
            # 如果是万、亿等大单位（索引 % 4 == 0），补“零”+单位
            if (length - i - 1) % 4 == 0:
                output += "零" + unit
            else:
                # 否则只补“零”（如果前面已有内容且末尾不是零）
                if output and not output.endswith("零"):
                    output += "零"
        else:
            # 这里我们不再单独判断“两”，统一交给后处理
            output += NUMBER_LOW_AN2CN[digit] + unit

    # 整理多余的零
    output = output.replace("零零", "零")
    output = output.replace("零万", "万").replace("零亿", "亿")
    output = output.replace("亿万", "亿")
    output = re.sub(r"([万亿])零([一二三四五六七八九][千])", r"\1\2", output)
    output = output.strip("零")

    # 处理“一十”开头（如 10 → 十）
    if output.startswith("一十"):
        output = output[1:]

    return output if output else "零"


def _decimal_convert(decimal_data: str) -> str:
    """小数部分转换（点 + 逐位数字，此时 decimal_data 已去除末尾零）"""
    if not decimal_data:
        return ""
    if len(decimal_data) > 16:
        decimal_data = decimal_data[:16]
        warn(f"小数部分过长，已截取前16位：{decimal_data}")

    output = "点"
    for ch in decimal_data:
        output += NUMBER_LOW_AN2CN[int(ch)]
    return output


# ========== 测试 ==========
if __name__ == "__main__":
    test_cases = [
        # "0",
        # "10",
        # "100",
        # "1000",
        # "10000",
        # "100000",
        # "1000000",
        # "200",
        # "2000",
        # "20000",
        # "200000",
        # "22000",
        # "22200",
        # "2220202",
        # "12",
        # "102",
        # "1002",
        # "100000000",
        # "100.50",
        # "0.5",
        # "0.05",
        # "-100",
        # "1.23",
        # "0.0001",
        # "1000000000000",
        # "21200",          # 预期 两万一千二百（？）
        # "100.05",         # 预期 一百点零五（小数中间有零保留）
        "2",
        "22",
        "222.354",
        "2222.002",
        "22222.222",
        "222222.02",
        "2222222.2",
    ]
    for case in test_cases:
        try:
            print(f"{case:>15} → {number_to_chinese(case)}")
        except Exception as e:
            print(f"{case:>15} → 错误: {e}")
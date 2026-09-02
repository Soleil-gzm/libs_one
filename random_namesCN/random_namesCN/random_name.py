# -*- coding: utf-8 -*-

import json
import random
from pkgutil import get_data


def _load_names(filename):
    """从包内 data/ 目录加载 JSON 名字列表

    使用 pkgutil.get_data 读取，安装成包后也能正确找到数据文件。
    """
    raw = get_data(__package__, "data/" + filename)
    if raw is None:
        raise FileNotFoundError("无法加载包内数据文件 data/" + filename)
    return json.loads(raw.decode("utf-8"))


# 数据单独维护在 random_namesCN/data/ 下的 JSON 文件中
__last_names = _load_names("last_names.json")
__last_names2 = _load_names("compound_last_names.json")
__first_names = _load_names("first_names.json")


def random_chinese_name():
    """生成随机中文名字

    包括的名字格式：2个字名字**，3个字名字***，4个字名字****

    :return:
    """
    name_len = random.choice([i for i in range(4)])
    if name_len == 0:
        name = random_two_name()
    elif name_len == 1:
        name = random_three_name()
    elif name_len == 2:
        name = random_three_names()
    else:
        name = random_four_name()
    return name


def random_two_name():
    """随机生成2位中文名字

    例如：李湘

    :return: str
    """
    return "".join(
        random.choices(__last_names, k=1) + random.choices(__first_names, k=1)
    )


def random_three_name():
    """随机生成3位普通中文名字

    例如：王阳明

    :return: str
    """
    return "".join(
        random.choices(__last_names, k=1) + random.choices(__first_names, k=2)
    )


def random_three_names():
    """随机生成3位复性中文名字

    例如：司马光 ｜ 百里奚

    :return: str
    """
    return "".join(
        random.choices(__last_names2, k=1) + random.choices(__first_names, k=1)
    )


def random_four_name():
    """随机生成4位复性中文名字

    例如：司马荣光

    :return: str
    """
    return "".join(
        random.choices(__last_names2, k=1) + random.choices(__first_names, k=2)
    )

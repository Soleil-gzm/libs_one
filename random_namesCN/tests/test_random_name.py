# -*- coding: utf-8 -*-

"""random_namesCN 单元测试。

运行方式（在 random_namesCN/ 目录下）：
    python -m unittest tests.test_random_name -v
"""

import random
import unittest

from random_namesCN import (
    random_chinese_name,
    random_two_name,
    random_three_name,
    random_three_names,
    random_four_name,
    random_four_name_single,
    random_five_name,
)
from random_namesCN.random_name import (
    _last_names,
    _compound_last_names,
    _first_names_single,
    _first_names_double,
    _first_names_triple,
    _load_csv,
)

# 重复采样次数：用统计方式校验随机行为
N = 200


class TestDataPools(unittest.TestCase):
    """校验 5 个 CSV 字典已加载且字段长度符合预期。"""

    def test_all_pools_non_empty(self):
        pools = {
            "单字姓": _last_names,
            "复姓": _compound_last_names,
            "单字名": _first_names_single,
            "双字名": _first_names_double,
            "三字名": _first_names_triple,
        }
        for name, pool in pools.items():
            with self.subTest(pool=name):
                self.assertGreater(len(pool), 0, f"{name} 池为空")

    def test_single_surnames_are_one_char(self):
        for s in _last_names:
            self.assertEqual(len(s), 1, f"单字姓应为 1 字，实际：{s}")

    def test_compound_surnames_are_two_char(self):
        for s in _compound_last_names:
            self.assertEqual(len(s), 2, f"复姓应为 2 字，实际：{s}")

    def test_single_given_are_one_char(self):
        for s in _first_names_single:
            self.assertEqual(len(s), 1, f"单字名应为 1 字，实际：{s}")

    def test_double_given_are_two_char(self):
        for s in _first_names_double:
            self.assertEqual(len(s), 2, f"双字名应为 2 字，实际：{s}")

    def test_triple_given_are_three_char(self):
        for s in _first_names_triple:
            self.assertEqual(len(s), 3, f"三字名应为 3 字，实际：{s}")

    def test_no_empty_or_whitespace_entries(self):
        for pool_name, pool in [
            ("单字姓", _last_names),
            ("复姓", _compound_last_names),
            ("单字名", _first_names_single),
            ("双字名", _first_names_double),
            ("三字名", _first_names_triple),
        ]:
            with self.subTest(pool=pool_name):
                for entry in pool:
                    self.assertEqual(entry, entry.strip(), f"{pool_name} 含空白：{entry!r}")
                    self.assertTrue(entry, f"{pool_name} 含空条目")


class TestLoadCsv(unittest.TestCase):
    """校验 _load_csv 的边界行为。"""

    def test_missing_file_raises_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            _load_csv("__definitely_not_exists__.csv")


class TestCombinationLength(unittest.TestCase):
    """6 种组合的姓名长度必须正确。"""

    cases = [
        (random_two_name, 2, "单姓+单字"),
        (random_three_name, 3, "单姓+双字"),
        (random_three_names, 3, "复姓+单字"),
        (random_four_name, 4, "复姓+双字"),
        (random_four_name_single, 4, "单姓+三字"),
        (random_five_name, 5, "复姓+三字"),
    ]

    def test_each_combination_length(self):
        for func, expected_len, desc in self.cases:
            with self.subTest(combination=desc):
                for _ in range(N):
                    name = func()
                    self.assertEqual(len(name), expected_len, f"{desc} 长度异常：{name!r}")


class TestParameterizedAPI(unittest.TestCase):
    """random_chinese_name 参数化行为。"""

    def test_default_random_valid_length(self):
        for _ in range(N):
            name = random_chinese_name()
            self.assertIn(len(name), {2, 3, 4, 5}, f"默认随机生成长度非法：{name!r}")

    def test_explicit_combinations_length(self):
        matrix = [
            ("single", 1, 2),
            ("single", 2, 3),
            ("single", 3, 4),
            ("compound", 1, 3),
            ("compound", 2, 4),
            ("compound", 3, 5),
        ]
        for st, gl, expected in matrix:
            with self.subTest(surname_type=st, given_len=gl):
                for _ in range(50):
                    self.assertEqual(
                        len(random_chinese_name(st, gl)),
                        expected,
                    )

    def test_invalid_surname_type_raises(self):
        for bad in ["x", "Compound", "", "single2", 1, 0]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    random_chinese_name(bad, 1)

    def test_invalid_given_len_raises(self):
        for bad in [0, 4, -1, "1", 1.5, None if False else 99]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    random_chinese_name("single", bad)

    def test_none_means_random(self):
        # surname_type / given_name_len 任一为 None 应正常工作（随机）
        for _ in range(N):
            name = random_chinese_name(None, None)
            self.assertIn(len(name), {2, 3, 4, 5})
            name2 = random_chinese_name("single", None)
            self.assertIn(len(name2), {2, 3, 4})
            name3 = random_chinese_name(None, 1)
            self.assertIn(len(name3), {2, 3})


class TestSurnameFromPool(unittest.TestCase):
    """生成的姓名首部必须来自对应姓池。"""

    def test_single_surname_in_pool(self):
        for _ in range(N):
            name = random_chinese_name("single", 1)
            self.assertIn(name[0], _last_names, f"单姓不在池中：{name!r}")

    def test_compound_surname_in_pool(self):
        for _ in range(N):
            name = random_chinese_name("compound", 1)
            self.assertIn(name[:2], _compound_last_names, f"复姓不在池中：{name!r}")

    def test_given_part_in_pool(self):
        # 抽 1/2/3 字名分别校验名部分来自对应池
        for gl, pool in [
            (1, _first_names_single),
            (2, _first_names_double),
            (3, _first_names_triple),
        ]:
            with self.subTest(given_len=gl):
                for _ in range(50):
                    name = random_chinese_name("single", gl)
                    given = name[1:]
                    self.assertEqual(len(given), gl)
                    self.assertIn(given, pool, f"名部分不在池中：{given!r}")


class TestVariety(unittest.TestCase):
    """统计性校验：大量生成应产生足够多样的结果。"""

    def test_default_generates_variety(self):
        names = {random_chinese_name() for _ in range(2000)}
        # 至少 500 个不同姓名（池子组合后远超此数）
        self.assertGreater(len(names), 500, f"生成的姓名多样性不足：{len(names)} 个不同")

    def test_all_six_lengths_appear(self):
        # 在足够多的样本中，2/3/4/5 字姓名都应出现
        seen_lengths = {len(random_chinese_name()) for _ in range(3000)}
        self.assertEqual(seen_lengths, {2, 3, 4, 5}, f"未覆盖所有字数：{seen_lengths}")

    def test_all_combinations_appear(self):
        # 通过显式参数覆盖所有 6 种组合能正常返回
        seen = set()
        for st in ("single", "compound"):
            for gl in (1, 2, 3):
                seen.add((st, gl, len(random_chinese_name(st, gl))))
        expected = {
            ("single", 1, 2),
            ("single", 2, 3),
            ("single", 3, 4),
            ("compound", 1, 3),
            ("compound", 2, 4),
            ("compound", 3, 5),
        }
        self.assertEqual(seen, expected)


class TestReproducibility(unittest.TestCase):
    """相同 seed 下结果应可复现。"""

    def test_same_seed_same_output(self):
        seed = random.randint(0, 10 ** 9)
        random.seed(seed)
        a = [random_chinese_name() for _ in range(20)]
        random.seed(seed)
        b = [random_chinese_name() for _ in range(20)]
        self.assertEqual(a, b, f"相同 seed={seed} 结果不一致")


if __name__ == "__main__":
    unittest.main()

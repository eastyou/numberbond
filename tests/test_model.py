"""数的分合与出题测试。"""

import unittest
from dataclasses import FrozenInstanceError

from numberbond.model import (
    MAX_WHOLE,
    MIN_WHOLE,
    MISSING,
    NumberBond,
    NumberBondError,
    check_part,
    check_whole,
    generate_bonds,
    ten_frame,
)


class GeneratedSplitTest(unittest.TestCase):
    """逐一验证 2–20 中偶数总数的各种分法。"""


def _make_split_test(whole, left):
    right = whole - left

    def test(self):
        bond = NumberBond(whole, left, right, "whole")
        self.assertEqual(bond.left + bond.right, whole)
        self.assertEqual(bond.answer, whole)

    test.__doc__ = "%d 分成 %d 和 %d" % (whole, left, right)
    return test


for _whole in range(2, MAX_WHOLE + 1, 2):
    for _left in range(1, _whole):
        setattr(
            GeneratedSplitTest,
            "test_%02d_%02d" % (_whole, _left),
            _make_split_test(_whole, _left),
        )


class CheckTest(unittest.TestCase):
    def test_whole_bounds(self):
        self.assertEqual(check_whole(MIN_WHOLE), MIN_WHOLE)
        self.assertEqual(check_whole(MAX_WHOLE), MAX_WHOLE)

    def test_whole_too_small(self):
        with self.assertRaises(NumberBondError):
            check_whole(1)

    def test_whole_too_large(self):
        with self.assertRaises(NumberBondError):
            check_whole(21)

    def test_whole_bool(self):
        with self.assertRaises(NumberBondError):
            check_whole(True)

    def test_whole_float(self):
        with self.assertRaises(NumberBondError):
            check_whole(5.5)

    def test_whole_string(self):
        with self.assertRaises(NumberBondError):
            check_whole("5")

    def test_part_zero(self):
        self.assertEqual(check_part(0), 0)

    def test_part_negative(self):
        with self.assertRaises(NumberBondError):
            check_part(-1)

    def test_part_float(self):
        with self.assertRaises(NumberBondError):
            check_part(2.5)

    def test_custom_name(self):
        with self.assertRaisesRegex(NumberBondError, "左边"):
            check_part(-3, "左边部分")


class BondTest(unittest.TestCase):
    def test_missing_whole(self):
        bond = NumberBond(10, 3, 7, "whole")
        self.assertEqual(bond.answer, 10)
        self.assertEqual(bond.prompt, "3 和 7 合起来是多少？")

    def test_missing_left(self):
        bond = NumberBond(10, 3, 7, "left")
        self.assertEqual(bond.answer, 3)
        self.assertEqual(bond.prompt, "总数 10，一部分是 7，另一部分是多少？")

    def test_missing_right(self):
        bond = NumberBond(10, 3, 7, "right")
        self.assertEqual(bond.answer, 7)
        self.assertEqual(bond.answer_text, "7")

    def test_zero_part(self):
        bond = NumberBond(6, 0, 6, "left")
        self.assertEqual(bond.answer, 0)

    def test_sum_mismatch(self):
        with self.assertRaises(NumberBondError):
            NumberBond(10, 4, 7, "whole")

    def test_bad_missing(self):
        with self.assertRaises(NumberBondError):
            NumberBond(10, 4, 6, "middle")

    def test_whole_out_of_range(self):
        with self.assertRaises(NumberBondError):
            NumberBond(30, 10, 20, "whole")

    def test_negative_part(self):
        with self.assertRaises(NumberBondError):
            NumberBond(5, -1, 6, "whole")

    def test_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            NumberBond(10, 3, 7, "whole").left = 4


class TenFrameTest(unittest.TestCase):
    def test_length(self):
        self.assertEqual(len(ten_frame(4)), 10)

    def test_filled_prefix(self):
        self.assertEqual(ten_frame(3), [True, True, True, False, False, False, False, False, False, False])

    def test_zero(self):
        self.assertFalse(any(ten_frame(0)))

    def test_full(self):
        self.assertTrue(all(ten_frame(10)))

    def test_negative(self):
        with self.assertRaises(NumberBondError):
            ten_frame(-1)

    def test_too_many(self):
        with self.assertRaises(NumberBondError):
            ten_frame(11)

    def test_float(self):
        with self.assertRaises(NumberBondError):
            ten_frame(2.5)

    def test_bool(self):
        with self.assertRaises(NumberBondError):
            ten_frame(True)


class GenerationTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_bonds(8, seed=1)), 8)

    def test_deterministic(self):
        self.assertEqual(generate_bonds(6, seed=3), generate_bonds(6, seed=3))

    def test_unique(self):
        items = generate_bonds(10, seed=2)
        keys = {(item.whole, item.left, item.right, item.missing) for item in items}
        self.assertEqual(len(keys), len(items))

    def test_range(self):
        for item in generate_bonds(10, 5, 7, seed=4):
            self.assertGreaterEqual(item.whole, 5)
            self.assertLessEqual(item.whole, 7)

    def test_single_missing(self):
        for item in generate_bonds(6, missing=("left",), seed=5):
            self.assertEqual(item.missing, "left")

    def test_invalid_count(self):
        for bad in (0, -1, 2.5, True, "8"):
            with self.assertRaises(NumberBondError):
                generate_bonds(bad)

    def test_too_many(self):
        with self.assertRaises(NumberBondError):
            generate_bonds(41)

    def test_invalid_bounds(self):
        with self.assertRaises(NumberBondError):
            generate_bonds(2, 1, 5)
        with self.assertRaises(NumberBondError):
            generate_bonds(2, 8, 5)

    def test_empty_missing(self):
        with self.assertRaises(NumberBondError):
            generate_bonds(2, missing=())

    def test_unknown_missing(self):
        with self.assertRaises(NumberBondError):
            generate_bonds(2, missing=("whole", "middle"))

    def test_impossible(self):
        with self.assertRaises(NumberBondError):
            generate_bonds(10, 4, 4, missing=("whole",))

    def test_answer_matches(self):
        for item in generate_bonds(20, 4, 12, seed=9):
            self.assertEqual(item.left + item.right, item.whole)
            self.assertIn(item.missing, MISSING)


if __name__ == "__main__":
    unittest.main()

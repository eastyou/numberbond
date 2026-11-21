"""分合图、十格阵与练习纸渲染测试。"""

import unittest

from numberbond.model import NumberBond, NumberBondError
from numberbond.render import render_bond, render_ten_frame, render_worksheet


class BondSvgTest(unittest.TestCase):
    def test_root(self):
        svg = render_bond(NumberBond(10, 3, 7, "whole"))
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("数的分合", svg)

    def test_three_values(self):
        svg = render_bond(NumberBond(10, 3, 7, "whole"))
        self.assertEqual(svg.count("<text"), 3)
        self.assertIn(">3<", svg)
        self.assertIn(">7<", svg)
        self.assertIn(">?<", svg)

    def test_question_mark(self):
        svg = render_bond(NumberBond(10, 3, 7, "whole"))
        self.assertIn(">?<", svg)

    def test_missing_part(self):
        svg = render_bond(NumberBond(10, 3, 7, "left"))
        self.assertIn(">?<", svg)
        self.assertNotIn(">3<", svg)
        self.assertIn(">7<", svg)

    def test_dashed_circle(self):
        svg = render_bond(NumberBond(10, 3, 7, "whole"))
        self.assertIn("stroke-dasharray", svg)

    def test_custom_size(self):
        svg = render_bond(NumberBond(8, 4, 4, "whole"), size=300)
        self.assertIn('width="300"', svg)

    def test_invalid_size(self):
        with self.assertRaises(NumberBondError):
            render_bond(NumberBond(8, 4, 4, "whole"), size=100)

    def test_bad_bond(self):
        with self.assertRaises(NumberBondError):
            render_bond(("8", "4"))


class TenFrameSvgTest(unittest.TestCase):
    def test_rect_count(self):
        self.assertEqual(render_ten_frame(4).count("<rect"), 10)

    def test_dot_count(self):
        self.assertEqual(render_ten_frame(4).count("<circle"), 4)

    def test_zero_dots(self):
        self.assertEqual(render_ten_frame(0).count("<circle"), 0)

    def test_full_frame(self):
        self.assertEqual(render_ten_frame(10).count("<circle"), 10)

    def test_custom_size(self):
        self.assertIn('width="300"', render_ten_frame(5, size=300))

    def test_invalid_size(self):
        with self.assertRaises(NumberBondError):
            render_ten_frame(5, size=80)

    def test_invalid_count(self):
        with self.assertRaises(NumberBondError):
            render_ten_frame(12)


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.problems = [
            NumberBond(10, 3, 7, "whole"),
            NumberBond(8, 5, 3, "left"),
            NumberBond(15, 6, 9, "right"),
        ]

    def test_document(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn("数的分合练习", page)
        self.assertTrue(page.endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 3)

    def test_ten_frames_only_small(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('aria-label="十格阵"'), 2)

    def test_answers(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertIn(">7<", page)

    def test_no_answers(self):
        page = render_worksheet(self.problems)
        self.assertNotIn("参考答案", page)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="10 的分成")
        self.assertIn("<title>10 的分成</title>", page)

    def test_empty(self):
        with self.assertRaises(NumberBondError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(NumberBondError):
            render_worksheet([("10", "3")])

    def test_escaping(self):
        page = render_worksheet(self.problems, title="<i>分合</i>")
        self.assertNotIn("<i>分合</i>", page)
        self.assertIn("&lt;i&gt;", page)


if __name__ == "__main__":
    unittest.main()

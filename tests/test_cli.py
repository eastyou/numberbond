"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from numberbond.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_frame_stdout(self):
        code, out, _ = run(["frame", "4"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)
        self.assertEqual(out.count("<circle"), 4)

    def test_frame_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "frame.svg"
            code, out, _ = run(["frame", "7", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_frame_invalid(self):
        code, _, err = run(["frame", "11"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_bond_default_left(self):
        code, out, _ = run(["bond", "10"])
        self.assertEqual(code, 0)
        self.assertIn(">?<", out)
        self.assertEqual(out.count(">5<"), 2)

    def test_bond_missing(self):
        code, out, _ = run(["bond", "8", "--left", "3", "--missing", "left"])
        self.assertEqual(code, 0)
        self.assertIn(">?<", out)

    def test_bond_invalid(self):
        code, _, err = run(["bond", "1"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_bond_bad_choices(self):
        with self.assertRaises(SystemExit):
            main(["bond", "8", "--missing", "middle"])

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "2", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_sheet_bad_missing(self):
        code, _, err = run(["sheet", "--missing", "whole,middle"])
        self.assertEqual(code, 2)
        self.assertIn("空缺", err)

    def test_sheet_empty_missing(self):
        code, _, err = run(["sheet", "--missing", " , "])
        self.assertEqual(code, 2)
        self.assertIn("空缺", err)

    def test_sheet_bad_range(self):
        code, _, err = run(["sheet", "--min", "8", "--max", "5"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "b.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()

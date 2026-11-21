"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    MAX_WHOLE,
    MIN_WHOLE,
    MISSING,
    NumberBond,
    NumberBondError,
    generate_bonds,
    ten_frame,
)
from .render import render_bond, render_ten_frame, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="numberbond",
        description="数的分合：十格阵、圆点图与求部分求总数的练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet = subparsers.add_parser("sheet", help="生成 A4 练习纸 HTML")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--min", dest="min_whole", type=int, default=4, help="最小总数，默认 4")
    sheet.add_argument("--max", dest="max_whole", type=int, default=10, help="最大总数，默认 10")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument(
        "--missing",
        default=",".join(MISSING),
        help="空缺位置，用逗号分隔：whole、left、right",
    )
    sheet.add_argument("--title", default="数的分合练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    bond = subparsers.add_parser("bond", help="输出单个分合图 SVG")
    bond.add_argument("whole", type=int, help="总数（%d–%d）" % (MIN_WHOLE, MAX_WHOLE))
    bond.add_argument("--left", type=int, default=None, help="左边部分，默认取一半")
    bond.add_argument(
        "--missing", default="whole", choices=MISSING, help="空缺位置，默认 whole"
    )
    bond.add_argument("--size", type=int, default=240, help="宽度，默认 240")
    bond.add_argument("-o", "--output", default=None, help="输出文件")

    frame = subparsers.add_parser("frame", help="输出十格阵 SVG")
    frame.add_argument("count", type=int, help="圆点数量（0–10）")
    frame.add_argument("--size", type=int, default=210, help="宽度，默认 210")
    frame.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_missing(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise NumberBondError("至少需要一种空缺位置")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "frame":
            _write_output(render_ten_frame(args.count, args.size), args.output)
            return 0
        if args.command == "bond":
            left = args.left if args.left is not None else args.whole // 2
            bond = NumberBond(args.whole, left, args.whole - left, args.missing)
            _write_output(render_bond(bond, args.size), args.output)
            return 0
        problems = generate_bonds(
            args.count,
            args.min_whole,
            args.max_whole,
            _parse_missing(args.missing),
            args.seed,
        )
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except NumberBondError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1

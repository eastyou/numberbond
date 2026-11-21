"""分合图、十格阵与 A4 练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import (
    NumberBond,
    NumberBondError,
    ten_frame,
)

_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 3mm; page-break-inside: avoid; }
.prompt { font-size: 13px; margin: 0 0 2mm; color: #323f4b; }
.frames { display: flex; gap: 3mm; justify-content: center; }
.answer-line { margin-top: 2mm; border-bottom: 1px dashed #9aa5b1; height: 22px; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2f6f4e; padding-left: 3mm; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def _circle(cx: float, cy: float, radius: float, text: str, missing: bool) -> List[str]:
    fill = "#fff7e6" if not missing else "#ffffff"
    stroke = "#c98a1b" if not missing else "#b02a37"
    dash = ' stroke-dasharray="4 3"' if missing else ""
    font_size = radius * (0.9 if text != "?" else 1.05)
    return [
        '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="1.8"%s/>'
        % (_fmt(cx), _fmt(cy), _fmt(radius), fill, stroke, dash),
        '<text x="%s" y="%s" font-size="%s" fill="#1f2933" text-anchor="middle" '
        'dominant-baseline="central">%s</text>'
        % (_fmt(cx), _fmt(cy + radius * 0.04), _fmt(font_size), text),
    ]


def render_bond(bond: NumberBond, size: int = 240) -> str:
    """绘制由三个圆组成的分合图，空缺处显示问号。"""
    if not isinstance(bond, NumberBond):
        raise NumberBondError("bond 必须是 NumberBond")
    if isinstance(size, bool) or not isinstance(size, int) or size < 140:
        raise NumberBondError("分合图尺寸必须是至少 140 的整数")

    width = float(size)
    height = round(size * 0.78, 2)
    radius = width * 0.15
    top = (width / 2.0, height * 0.26)
    left = (width * 0.25, height * 0.78)
    right = (width * 0.75, height * 0.78)

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s" '
        'role="img" aria-label="数的分合">' % (_fmt(width), _fmt(height), _fmt(width), _fmt(height)),
        "<title>数的分合</title>",
    ]
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#7b8794" stroke-width="2"/>'
        % (_fmt(top[0]), _fmt(top[1] + radius * 0.7), _fmt(left[0] + radius * 0.4), _fmt(left[1] - radius * 0.9))
    )
    parts.append(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#7b8794" stroke-width="2"/>'
        % (_fmt(top[0]), _fmt(top[1] + radius * 0.7), _fmt(right[0] - radius * 0.4), _fmt(right[1] - radius * 0.9))
    )

    whole_text = "?" if bond.missing == "whole" else str(bond.whole)
    left_text = "?" if bond.missing == "left" else str(bond.left)
    right_text = "?" if bond.missing == "right" else str(bond.right)
    parts.extend(_circle(top[0], top[1], radius, whole_text, bond.missing == "whole"))
    parts.extend(_circle(left[0], left[1], radius, left_text, bond.missing == "left"))
    parts.extend(_circle(right[0], right[1], radius, right_text, bond.missing == "right"))
    parts.append("</svg>")
    return "\n".join(parts)


def render_ten_frame(count: int, size: int = 210) -> str:
    """绘制 2×5 十格阵，前 count 格画圆点。"""
    flags = ten_frame(count)
    if isinstance(size, bool) or not isinstance(size, int) or size < 120:
        raise NumberBondError("十格阵尺寸必须是至少 120 的整数")

    cell = size / 5.0
    height = cell * 2
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%s" height="%s" '
        'role="img" aria-label="十格阵">' % (_fmt(float(size)), _fmt(height), _fmt(float(size)), _fmt(height)),
        "<title>十格阵</title>",
    ]
    for index, filled in enumerate(flags):
        row, col = divmod(index, 5)
        x = col * cell
        y = row * cell
        parts.append(
            '<rect x="%s" y="%s" width="%s" height="%s" fill="#ffffff" stroke="#323f4b" stroke-width="1.6"/>'
            % (_fmt(x), _fmt(y), _fmt(cell), _fmt(cell))
        )
        if filled:
            parts.append(
                '<circle cx="%s" cy="%s" r="%s" fill="#2f6f4e"/>'
                % (_fmt(x + cell / 2), _fmt(y + cell / 2), _fmt(cell * 0.28))
            )
    parts.append("</svg>")
    return "\n".join(parts)


def render_worksheet(
    problems: Sequence[NumberBond],
    title: str = "数的分合练习",
    answers: bool = False,
) -> str:
    """生成可打印的数的分合练习纸。"""
    items = list(problems)
    if not items:
        raise NumberBondError("至少需要一道题")
    for item in items:
        if not isinstance(item, NumberBond):
            raise NumberBondError("题目必须是 NumberBond")

    cards: List[str] = []
    for index, item in enumerate(items, 1):
        figures = [render_bond(item)]
        if item.whole <= 10:
            figures.append(render_ten_frame(item.whole))
        cards.append(
            '<div class="card">\n<p class="prompt">%d. %s</p>\n<div class="frames">%s</div>\n'
            '<div class="answer-line"></div>\n</div>'
            % (index, html.escape(item.prompt), "\n".join(figures))
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="grid">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = []
        for index, item in enumerate(items, 1):
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
                % (index, html.escape(item.prompt), html.escape(item.answer_text))
            )
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)

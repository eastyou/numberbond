"""数的分合：整体与部分、十格阵与出题。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple

MIN_WHOLE = 2
MAX_WHOLE = 20
MISSING: Tuple[str, ...] = ("whole", "left", "right")


class NumberBondError(ValueError):
    """数的分合相关的输入错误。"""


def check_whole(value: Any, name: str = "总数") -> int:
    """校验总数是 2–20 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise NumberBondError("%s必须是整数" % name)
    if value < MIN_WHOLE or value > MAX_WHOLE:
        raise NumberBondError(
            "%s必须在 %d–%d 之间：%d" % (name, MIN_WHOLE, MAX_WHOLE, value)
        )
    return value


def check_part(value: Any, name: str = "部分") -> int:
    """校验部分是非负整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise NumberBondError("%s必须是整数" % name)
    if value < 0:
        raise NumberBondError("%s不能为负数：%d" % (name, value))
    return value


@dataclass(frozen=True)
class NumberBond:
    """一道数的分合题，missing 指定哪个位置留空。"""

    whole: int
    left: int
    right: int
    missing: str = "whole"

    def __post_init__(self) -> None:
        check_whole(self.whole)
        check_part(self.left, "左边部分")
        check_part(self.right, "右边部分")
        if self.left + self.right != self.whole:
            raise NumberBondError(
                "%d + %d 不等于 %d" % (self.left, self.right, self.whole)
            )
        if self.missing not in MISSING:
            raise NumberBondError("未知空缺位置：%s" % self.missing)

    @property
    def answer(self) -> int:
        """空缺位置的数值。"""
        if self.missing == "whole":
            return self.whole
        if self.missing == "left":
            return self.left
        return self.right

    @property
    def prompt(self) -> str:
        if self.missing == "whole":
            return "%d 和 %d 合起来是多少？" % (self.left, self.right)
        if self.missing == "left":
            return "总数 %d，一部分是 %d，另一部分是多少？" % (self.whole, self.right)
        return "总数 %d，一部分是 %d，另一部分是多少？" % (self.whole, self.left)

    @property
    def answer_text(self) -> str:
        return str(self.answer)


def ten_frame(count: int) -> List[bool]:
    """返回十格阵的填充状态，前 count 格为 True。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise NumberBondError("圆点数量必须是整数")
    if count < 0 or count > 10:
        raise NumberBondError("圆点数量必须在 0–10 之间：%d" % count)
    return [index < count for index in range(10)]


def generate_bonds(
    count: int = 8,
    min_whole: int = 4,
    max_whole: int = 10,
    missing: Sequence[str] = MISSING,
    seed: Optional[int] = None,
) -> List[NumberBond]:
    """生成不重复的数的分合题。"""
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise NumberBondError("题目数量必须是正整数")
    if count > 40:
        raise NumberBondError("题目数量不能超过 40")
    check_whole(min_whole, "最小总数")
    check_whole(max_whole, "最大总数")
    if min_whole > max_whole:
        raise NumberBondError("最小总数不能大于最大总数")
    chosen = tuple(missing)
    if not chosen:
        raise NumberBondError("至少需要一种空缺位置")
    for position in chosen:
        if position not in MISSING:
            raise NumberBondError("未知空缺位置：%s" % position)

    rng = random.Random(seed)
    candidates = [
        NumberBond(whole, left, whole - left, position)
        for whole in range(min_whole, max_whole + 1)
        for left in range(0, whole + 1)
        for position in chosen
    ]
    if count > len(candidates):
        raise NumberBondError("可用题目不足 %d 道" % count)
    picked = rng.sample(candidates, count)
    return picked

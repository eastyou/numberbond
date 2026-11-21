# numberbond

[![CI](https://github.com/eastyou/numberbond/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/numberbond/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把“数的分合”画成三个圆，空缺位置用问号标出；配合 2×5 十格阵，帮低年级学生理解整体与部分的关系，生成可打印的 A4 练习纸。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成 8 道分合题，附答案
numberbond sheet --count 8 --answers -o sheet.html

# 只求部分，总数限定在 5–10
numberbond sheet --missing left,right --min 5 --max 10 -o part.html

# 输出单个分合图 SVG
numberbond bond 10 --left 3 --missing whole -o bond.svg

# 输出十格阵 SVG
numberbond frame 6 -o frame.svg
```

## 功能

- 三圆分合图：总数在上，两个部分在下
- 空缺位置可选总数、左边或右边
- 2×5 十格阵圆点图，总数不超过 10 时自动附上
- 题目去重、支持随机种子复现
- 输出 A4 打印样式，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou

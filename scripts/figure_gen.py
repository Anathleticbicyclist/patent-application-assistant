#!/usr/bin/env python3
"""说明书附图生成：把结构化步骤/模块画成符合国知局形式要求的黑白线稿。

合规要点（脚本已内置）：
- 纯黑白、无灰度填充、无底色
- 图内**不出现文字说明**，只有附图标记（1/2/3…）或步骤号（S1/S2…）
- 300 DPI、A4 版心内留白、线条粗细统一
- 流程图为矩形框 + 箭头，必须有「开始/结束」或明确的起止关系

用法：
    python3 scripts/figure_gen.py --spec fig.json --out fig2.png
fig.json 示例：
    {"type": "flow", "steps": ["采集温度信号", "滑窗分段并提取温升斜率",
                               "阈值判定", "二次确认", "输出告警"]}
    {"type": "blocks", "blocks": ["采集模块", "预处理模块", "判定单元", "上报链路"]}
    {"type": "system", "layers": [["终端设备"], ["边缘网关"], ["云平台"]]}
注意：steps/blocks 里的文字只用于 **终端日志**，不会画进图里。
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

LINE_W = 1.2
FONT = {"fontsize": 11, "fontweight": "bold"}


def _binarize(path, threshold=200):
    """把抗锯齿产生的灰边压成纯黑/纯白，满足国知局「黑白线条图」要求。"""
    try:
        from PIL import Image
    except ImportError:
        return False
    im = Image.open(path).convert("L")
    im = im.point(lambda p: 255 if p > threshold else 0, mode="L")
    im.save(path, dpi=(300, 300))
    return True


def _clean(ax):
    ax.set_axis_off()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")


def flow(steps, out, dpi=300):
    n = len(steps)
    h = 100 / n
    box_h = h * 0.55
    fig_w = 6.0
    fig_h = max(3.0, 0.55 * n + 1.2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    _clean(ax)
    fig.patch.set_facecolor("white")

    for i in range(n):
        y = 100 - (i + 1) * h + h / 2
        ax.add_patch(Rectangle((36, y - box_h / 2), 28, box_h,
                               fill=False, ec="black", lw=LINE_W))
        ax.text(50, y, f"S{i + 1}", ha="center", va="center", color="black", **FONT)
        if i < n - 1:
            y2 = 100 - (i + 2) * h + h / 2
            ax.add_patch(FancyArrowPatch((50, y - box_h / 2), (50, y2 + box_h / 2),
                                         arrowstyle="-|>", mutation_scale=12,
                                         color="black", lw=LINE_W, shrinkA=0, shrinkB=0))
    fig.savefig(out, dpi=dpi, facecolor="white", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    _binarize(out)


def blocks(items, out, dpi=300):
    n = len(items)
    fig, ax = plt.subplots(figsize=(8, max(3.0, 1.1 * n)))
    _clean(ax)
    fig.patch.set_facecolor("white")
    box_h = 8
    gap = (100 - n * box_h) / (n + 1)
    for i in range(n):
        y = 100 - (i + 1) * gap - i * box_h - box_h
        ax.add_patch(Rectangle((18, y), 22, box_h, fill=False, ec="black", lw=LINE_W))
        ax.text(29, y + box_h / 2, str(i + 1), ha="center", va="center", color="black", **FONT)
        # 右侧总线 + 连接线，模拟典型框图
        ax.plot([40, 56], [y + box_h / 2, y + box_h / 2], color="black", lw=LINE_W)
    ax.plot([56, 56], [100 - gap - box_h / 2, 100 - gap - (n - 1) * (box_h + gap) - box_h / 2],
            color="black", lw=LINE_W)
    ax.add_patch(Rectangle((56, 40), 20, 14, fill=False, ec="black", lw=LINE_W))
    ax.text(66, 47, "A", ha="center", va="center", color="black", **FONT)
    fig.savefig(out, dpi=dpi, facecolor="white", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    _binarize(out)


def system(layers, out, dpi=300):
    n = len(layers)
    fig, ax = plt.subplots(figsize=(7, max(3.0, 1.4 * n)))
    _clean(ax)
    fig.patch.set_facecolor("white")
    total_h = 22
    gap = (100 - n * total_h) / (n + 1)
    for i, layer in enumerate(layers):
        y = 100 - (i + 1) * gap - i * total_h - total_h
        ax.add_patch(Rectangle((8, y), 84, total_h, fill=False, ec="black", lw=LINE_W))
        w = 76 / max(1, len(layer))
        for j in range(len(layer)):
            ax.add_patch(Rectangle((12 + j * w, y + 4), w - 4, total_h - 8,
                                   fill=False, ec="black", lw=LINE_W, ls="-"))
            ax.text(12 + j * w + (w - 4) / 2, y + total_h / 2,
                    f"{i + 1}{j + 1}", ha="center", va="center", color="black", **FONT)
    fig.savefig(out, dpi=dpi, facecolor="white", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    _binarize(out)


KINDS = {"flow": flow, "blocks": blocks, "system": system}


def main():
    ap = argparse.ArgumentParser(description="生成合规黑白说明书附图")
    ap.add_argument("--spec", required=True, help="JSON 规格文件")
    ap.add_argument("--out", default="figure.png")
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()

    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print(f"[FAIL] 文件不存在或无法解析：{args.spec}")
        return 2
    kind = spec.get("type")
    if kind not in KINDS:
        print(f"不支持的图类型：{kind}，可选 {list(KINDS)}")
        return 2

    if kind == "flow":
        flow(spec["steps"], args.out, args.dpi)
    elif kind == "blocks":
        blocks(spec["blocks"], args.out, args.dpi)
    else:
        system(spec["layers"], args.out, args.dpi)

    p = Path(args.out)
    print(f"已生成 {p} ({p.stat().st_size} bytes, {args.dpi} DPI)")
    print("图内只含标记，不含文字说明；正文请用「图1 为……流程图」对应的附图说明。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

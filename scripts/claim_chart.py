#!/usr/bin/env python3
"""侵权比对（claim chart）生成器：把权利要求拆成要素，逐格对照被控方案。

核心规则（已内置判据）：
- **全覆盖原则**：只要有一个要素判为「不同」（DIFF），即不落入该权项。
- 「等同」（EQV）与「相同」（SAME）都算落入，但必须写明理由。
- 缺失要素（MISS）按「不同」处理。

输入：
1. 权利要求文本（md/docx）
2. 被控方案特征 JSON：
   [
     {"claim": "1", "element_id": "1-1", "target": "触发后2s内重采3次",
      "verdict": "SAME", "evidence": "产品逻辑说明书 p12", "note": ""},
     ...
   ]
   verdict ∈ SAME / EQV / DIFF / MISS / UNKNOWN

用法：
    python3 scripts/claim_chart.py --claims 权利要求书.md --map map.json --out chart.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

VERDICT_LABEL = {"SAME": "相同", "EQV": "等同", "DIFF": "不同", "MISS": "缺失", "UNKNOWN": "待判定"}
VERDICT_MARK = {"SAME": "✅", "EQV": "≈", "DIFF": "❌", "MISS": "❌", "UNKNOWN": "❓"}


def read_text(path):
    p = Path(path)
    if p.suffix.lower() == ".docx":
        try:
            from docx import Document
        except ImportError:
            raise SystemExit("读取 docx 需要 python-docx：pip install python-docx")
        return "\n".join(par.text for par in Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")


def extract_claims(text):
    """复用 claim_check 的切分逻辑，保持两脚本判定口径一致。"""
    sys.path.insert(0, str(Path(__file__).parent))
    from claim_check import extract_claims as _ec
    return _ec(text)


def build_chart(claims, mapping):
    """生成 markdown 表 + 逐权项结论。"""
    by_claim = {}
    for row in mapping:
        by_claim.setdefault(str(row.get("claim", "")).strip(), []).append(row)

    lines = ["# 侵权比对表（Claim Chart）", "",
             "> 本表为技术层面比对结果，不构成法律意见。侵权认定须由专利代理师/律师出具意见。", ""]
    verdicts = []

    for c in claims:
        key = str(c["no"])
        rows = by_claim.get(key)
        if not rows:
            verdicts.append((key, "未比对", "本权项未提供比对数据"))
            continue

        clean = re.sub(r"[#\s]+$", "", c["text"])
        lines += [f"## 权利要求 {key}", "",
                  f"**原文**：{clean[:400]}{'…' if len(clean) > 400 else ''}", "",
                  "| 要素 | 权利要求特征 | 被控方案对应实现 | 判定 | 依据 |",
                  "|---|---|---|---|---|"]

        worst = "SAME"
        order = {"SAME": 0, "EQV": 1, "UNKNOWN": 2, "MISS": 3, "DIFF": 4}
        for i, r in enumerate(rows, 1):
            v = str(r.get("verdict", "UNKNOWN")).upper()
            v = v if v in VERDICT_LABEL else "UNKNOWN"
            worst = v if order[v] > order[worst] else worst
            elem = r.get("element_id") or f"{key}-{i}"
            feat = r.get("feature") or (c["features"][i - 1] if i - 1 < len(c["features"]) else "（未提供）")
            lines.append(f"| {elem} | {feat} | {r.get('target', '—')} | "
                         f"{VERDICT_MARK[v]} {VERDICT_LABEL[v]} | {r.get('evidence', '—')} |")
        lines.append("")

        if worst in ("DIFF", "MISS"):
            concl = f"不落入（要素 {sum(1 for r in rows if str(r.get('verdict','')).upper() in ('DIFF','MISS'))} 处不同/缺失）"
        elif worst == "UNKNOWN":
            concl = "待补充证据后判定"
        elif worst == "EQV":
            concl = "可能落入（存在等同要素，需就「手段—功能—效果」实质相同举证）"
        else:
            concl = "落入（全部要素相同）"
        lines.append(f"**结论：{concl}**")
        lines.append("")
        verdicts.append((key, concl, ""))

    lines += ["## 汇总", "", "| 权项 | 结论 |", "|---|---|"]
    for k, v, _ in verdicts:
        lines.append(f"| {k} | {v} |")
    lines += ["", "## 规避提示（按判定自动给出方向）", ""]
    for k, v, _ in verdicts:
        if v.startswith("不落入"):
            continue
        rows = by_claim.get(k, [])
        for r in rows:
            if str(r.get("verdict", "")).upper() in ("SAME", "EQV"):
                lines.append(f"- 权项 {k} 的要素 `{r.get('element_id', '')}`（{r.get('feature', '')[:30]}…）"
                             f"是落入的关键：优先考虑**删减该特征**或**换用实质不同的手段**。")
    lines += ["", "> 规避手段是否奏效，仍取决于权项解释与等同原则的适用，需个案判断。", ""]
    return "\n".join(lines), verdicts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", required=True, help="权利要求文本文件")
    ap.add_argument("--map", required=True, help="比对数据 JSON")
    ap.add_argument("--out", default="claim-chart.md")
    args = ap.parse_args()

    claims = extract_claims(read_text(args.claims))
    if not claims:
        print("未解析到权利要求，检查「1. 」起始格式")
        return 2

    mapping = json.loads(Path(args.map).read_text(encoding="utf-8"))
    chart, verdicts = build_chart(claims, mapping)
    Path(args.out).write_text(chart, encoding="utf-8")

    print(chart)
    print(f"已写入 {args.out}")
    risky = [v for v in verdicts if v[1].startswith(("落入", "可能落入", "待补充"))]
    untested = [v[0] for v in verdicts if v[1] == "未比对"]
    print(f"需关注权项：{[r[0] for r in risky] or '无'}")
    if untested:
        print(f"未比对权项：{untested}（需补比对数据后重跑）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""一条命令跑完整个流程：机检 → 查新 → 权项 → 附图 → 比对 → 汇总。

设计原则：
- 每一步的产物自动命名、自动落到同一个目录，不再手工串命令；
- 某一步失败**不中断**后面的步骤（查新没凭据、比对缺映射都是正常态），
  但失败会写进汇总报告，最后统一给出「还差什么」；
- 不猜数据：文档里没有的关键词/映射就不跑那一步，并在报告里说明缺什么。

用法：
    python3 scripts/pipeline.py --doc 交底书.md --out ./run1
    python3 scripts/pipeline.py --doc 申请文件.md --keywords "热失控,thermal runaway" \
        --ipc H01M10 --fig fig.json --map claim-map.json --out ./run1
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable

STEP_ORDER = ["check", "search", "claims", "figure", "chart", "final"]


def run(script, args, cwd=None):
    """跑一个子脚本，返回 (returncode, stdout, stderr)。"""
    p = subprocess.run([PY, str(HERE / script)] + args,
                       capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def read_doc(path):
    p = Path(path)
    if p.suffix.lower() == ".docx":
        try:
            from docx import Document
        except ImportError:
            return ""
        return "\n".join(x.text for x in Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")


BOILERPLATE = ("权利要求书", "说明书摘要", "说明书", "摘要", "技术领域", "背景技术",
               "发明内容", "附图说明", "具体实施方式", "实施例")


def guess_topic(text):
    """优先取「一种……」这类方案名，其次取第一个非样板标题。"""
    m = re.search(r"一种[^，。；\n]{4,40}", text)
    if m:
        return m.group(0).strip()
    for line in text.splitlines():
        s2 = line.strip().lstrip("#").strip()
        if not s2 or len(s2) > 60:
            continue
        if any(s2.startswith(b) for b in BOILERPLATE):
            continue
        return re.sub(r"^[【\[]|[】\]]$", "", s2)
    return "未命名技术方案"


def guess_keywords(text, topic):
    """从文档里挑出现频次高的技术名词，避免瞎编。"""
    if not text:
        return ""
    cands = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text)          # 英文术语
    cn = re.findall(r"(?:(?![的之了与和及对])[一-龥]){2,6}(?:模块|单元|装置|方法|算法|信号|阈值|链路|平台)", text)
    STOP_PREFIX = ("所述", "对所述", "与", "和", "及", "当", "若", "在", "的", "该")
    freq = {}
    for w in cands + cn:
        w = w.strip()
        for pfx in STOP_PREFIX:
            if w.startswith(pfx):
                w = w[len(pfx):]
        if len(w) < 3 or w in topic or "所述" in w:
            continue
        freq[w] = freq.get(w, 0) + 1

    # 去掉被更长词包含的碎片（如「温度」被「温度信号」吃掉）
    keys = sorted(freq, key=lambda x: -len(x))
    kept = [k for k in keys if not any(k != o and k in o for o in keys)]

    # 只留复现 ≥2 次的术语，并剔除动作/修饰词混入的短语——宁可少给，不给噪声
    NOISE = ("超过", "预设", "再次", "一种", "包括", "执行", "实现", "所述")
    clean = [(k, freq[k]) for k in kept
             if freq[k] >= 2 and not any(n in k for n in NOISE)]
    clean.sort(key=lambda kv: -kv[1])
    if not clean:
        clean = [(k, freq[k]) for k in kept
                 if not any(n in k for n in NOISE)][:3]
    return ",".join(w for w, _ in clean[:5])


def extract_score(stdout):
    m = re.search(r"评分\s*(\d+)", stdout)
    return int(m.group(1)) if m else None


def extract_counts(stdout):
    m = re.search(r"PASS\s*(\d+)\s*/\s*WARN\s*(\d+)\s*/\s*FAIL\s*(\d+)", stdout)
    return tuple(int(x) for x in m.groups()) if m else (None, None, None)


def parse_failures(stdout):
    """把 ❌/⚠️ 行抓出来，用于汇总里的「待办」。"""
    out = []
    for line in stdout.splitlines():
        if line.startswith(("❌", "⚠️")):
            out.append(line.strip())
    return out


def main():
    ap = argparse.ArgumentParser(description="专利申请助手 · 全流程流水线")
    ap.add_argument("--doc", required=True, help="交底书或申请文件（md/docx）")
    ap.add_argument("--out", default="./pipeline-out", help="运行目录")
    ap.add_argument("--keywords", default="", help="检索关键词；留空则自动从文档提取")
    ap.add_argument("--ipc", default="", help="IPC/CPC 主分类，如 H01M10")
    ap.add_argument("--country", default="CN")
    ap.add_argument("--year-from", type=int, default=None)
    ap.add_argument("--fig", default="", help="附图规格 JSON；有才画图")
    ap.add_argument("--map", default="", help="比对映射 JSON；有才做比对")
    ap.add_argument("--skip", default="", help="跳过某些步骤，逗号分隔：search,figure,chart")
    args = ap.parse_args()

    doc = Path(args.doc)
    if not doc.exists():
        print(f"[FAIL] 文件不存在：{doc}")
        return 2

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}

    text = read_doc(doc)
    topic = guess_topic(text)
    keywords = args.keywords or guess_keywords(text, topic)
    has_claims = bool(re.search(r"权利要求书|权利要求\s*1|^1\s*[.、]", text, re.M))

    print(f"文档：{doc}")
    print(f"主题：{topic}")
    auto_kw = not args.keywords
    print(f"关键词：{keywords or '（未提取到，查新将只给通用式）'}"
          + ("  ← 自动提取，建议用 --keywords 补全中英文同义词" if auto_kw and keywords else ""))
    print(f"运行目录：{outdir}")
    print("=" * 62)

    steps = []   # (步骤名, 状态, 摘要, 产物, 待办)

    # ---------- 1. 机检 ----------
    if "check" not in skip:
        print("\n[1/6] 交付物机检")
        rc, so, se = run("check_deliverable.py", [str(doc)])
        print(so.strip() or se.strip())
        p_, w_, f_ = extract_counts(so)
        steps.append(("机检", "FAIL" if f_ else ("WARN" if w_ else "PASS"),
                      f"PASS {p_} / WARN {w_} / FAIL {f_}，评分 {extract_score(so)}",
                      "（输出见上）", parse_failures(so)))

    # ---------- 2. 查新 ----------
    if "search" not in skip:
        print("\n[2/6] 查新检索计划")
        sdir = outdir / "search"
        a = ["--topic", topic, "--keywords", keywords, "--out", str(sdir),
             "--country", args.country]
        if args.ipc:
            a += ["--ipc", args.ipc]
        if args.year_from:
            a += ["--year-from", str(args.year_from)]
        rc, so, se = run("prior_art_search.py", a)
        print("\n".join(so.strip().splitlines()[-4:]) or se.strip())
        degraded = "降级" in so
        steps.append(("查新", "WARN" if degraded else "PASS",
                      "已降级为检索计划模式（无 API 凭据）" if degraded
                      else "已生成检索式与直链",
                      "search/search-plan.md", [] if not degraded else
                      ["在浏览器执行检索式并回填命中数"]))

    # ---------- 3. 权项 ----------
    if "claims" not in skip:
        if has_claims:
            print("\n[3/6] 权利要求形式检查")
            rc, so, se = run("claim_check.py", [str(doc), "--json", str(outdir / "claims.json")])
            print(so.strip() or se.strip())
            p_, w_, f_ = extract_counts(so)
            steps.append(("权项", "FAIL" if f_ else ("WARN" if w_ else "PASS"),
                          f"PASS {p_} / WARN {w_} / FAIL {f_}", "claims.json", parse_failures(so)))
        else:
            print("\n[3/6] 权项检查 —— 跳过（文档中未发现权利要求）")
            steps.append(("权项", "SKIP", "文档中未发现权利要求", "", []))

    # ---------- 4. 附图 ----------
    if "figure" not in skip and args.fig:
        print("\n[4/6] 说明书附图")
        rc, so, se = run("figure_gen.py", ["--spec", args.fig, "--out", str(outdir / "figure.png")])
        print(so.strip() or se.strip())
        steps.append(("附图", "PASS" if rc == 0 else "FAIL",
                      "已生成黑白附图" if rc == 0 else "生成失败", "figure.png", []))
    elif "figure" not in skip:
        print("\n[4/6] 附图 —— 跳过（未提供 --fig 规格）")
        steps.append(("附图", "SKIP", "未提供附图规格", "", ["需要附图时传 --fig fig.json"]))

    # ---------- 5. 比对 ----------
    if "chart" not in skip and args.map:
        print("\n[5/6] 侵权比对表")
        if not has_claims:
            print("跳过：无权利要求可比对")
            steps.append(("比对", "SKIP", "无权利要求", "", []))
        else:
            rc, so, se = run("claim_chart.py", ["--claims", str(doc), "--map", args.map,
                                                "--out", str(outdir / "claim-chart.md")])
            print("\n".join(so.strip().splitlines()[-3:]) or se.strip())
            steps.append(("比对", "PASS" if rc == 0 else "FAIL",
                          "已生成比对表", "claim-chart.md", []))
    elif "chart" not in skip:
        print("\n[5/6] 比对 —— 跳过（未提供 --map 映射）")
        steps.append(("比对", "SKIP", "未提供比对映射", "", ["需要 FTO 时传 --map map.json"]))

    # ---------- 6. 汇总 ----------
    print("\n[6/6] 生成汇总报告")
    report = [f"# 流水线运行报告", "",
              f"- 文档：`{doc}`",
              f"- 主题：{topic}",
              f"- 关键词：{keywords or '（未提取）'}",
              f"- 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
              f"- 运行目录：`{outdir}`", "",
              "## 各步结果", "",
              "| 步骤 | 状态 | 摘要 | 产物 |", "|---|---|---|---|"]
    for name, st, summary, art, _ in steps:
        mark = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "SKIP": "—"}[st]
        report.append(f"| {name} | {mark} {st} | {summary} | {art} |")

    todos = []
    for name, st, _, _, t in steps:
        for item in t:
            todos.append(f"- **{name}**：{item}")
    report += ["", "## 还需要人做的", ""]
    report += todos if todos else ["- 无。形式项已全部通过。"]

    fails = [s for s in steps if s[1] == "FAIL"]
    warns = [s for s in steps if s[1] == "WARN"]
    report += ["", "## 结论", "",
               f"{'❌ 存在硬伤，须先修正' if fails else ('⚠️ 形式项通过，但有需确认项' if warns else '✅ 形式项全部通过')}", "",
               "> 机检与脚本只覆盖形式项与结构项；客体适格性、创造性、支持性等实质审查，"
               "须按 `references/review-checklist.md` 人工逐项过。", ""]

    rp = outdir / "00-运行报告.md"
    rp.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"\n报告已写入 {rp}")

    if fails:
        print("\n下一步：修正上面的 ❌ 项后重跑本命令。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

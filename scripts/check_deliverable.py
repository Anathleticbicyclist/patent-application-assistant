#!/usr/bin/env python3
"""专利申请助手 · 交付物机检脚本

用法：
    python3 scripts/check_deliverable.py <交付文件.md> [--type disclosure|application]

只做结构与形式层面的确定性检查（章节齐全、权项编号、多项引多项、引用基础、
实施例数量、摘要字数、疑似编造引用）。不替代人工实质审查。
"""
import argparse
import re
import sys
from pathlib import Path

DISCLOSURE_SECTIONS = [
    ("发明名称", r"发明名称|发明创造名称"),
    ("技术领域", r"技术领域"),
    ("背景技术", r"背景技术|现有技术"),
    ("发明目的", r"发明目的|发明所要解决"),
    ("技术方案", r"技术方案"),
    ("有益效果", r"有益效果|技术效果"),
    ("实施例", r"实施例"),
    ("附图说明", r"附图说明|附图清单"),
    ("保护点", r"保护点|创新点|关键点"),
    ("替代方案", r"替代方案|变形方案"),
    ("公开情况", r"公开情况|保密"),
    ("术语表", r"术语表|术语定义"),
]

SPEC_SECTIONS = [
    ("权利要求书", r"权利要求书|权利要求"),
    ("技术领域", r"技术领域"),
    ("背景技术", r"背景技术"),
    ("发明内容", r"发明内容"),
    ("附图说明", r"附图说明"),
    ("具体实施方式", r"具体实施方式|实施方式"),
    ("摘要", r"摘要"),
]


def load(path):
    p = Path(path)
    if p.suffix.lower() == ".docx":
        try:
            from docx import Document
        except ImportError:
            raise SystemExit("读取 docx 需要 python-docx：pip install python-docx")
        return "\n".join(par.text for par in Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")


def split_claims(text):
    """截取权利要求书段落，返回 [(编号, 正文)]。"""
    start = None
    for m in re.finditer(r"(权利要求书|权 利 要 求 书)", text):
        start = m.end()
        break
    if start is None:
        return []
    end = len(text)
    for kw in ("说明书", "技术领域", "说明书摘要"):
        m = re.search(kw, text[start:])
        if m:
            end = min(end, start + m.start())
    seg = text[start:end]
    claims = []
    current = None
    for line in seg.splitlines():
        m = re.match(r"\s*(\d{1,3})\s*[.、．]\s*(.*)", line)
        if m:
            if current:
                claims.append(current)
            current = [int(m.group(1)), m.group(2).strip()]
        elif current and line.strip():
            current[1] += line.strip()
    if current:
        claims.append(current)
    return [(n, c) for n, c in claims]


def check_disclosure(text):
    results = []
    for name, pat in DISCLOSURE_SECTIONS:
        ok = re.search(pat, text) is not None
        results.append(("PASS" if ok else "FAIL", f"交底书章节：{name}", "" if ok else "缺少该章节"))
    # 实施例数量
    nums = set(re.findall(r"实施例\s*([0-9一二三四五六七八九十]+)", text))
    count = len(nums)
    results.append(
        ("PASS" if count >= 3 else "WARN", f"实施例数量：{count}",
         "" if count >= 3 else "少于 3 个，或编号重复；需覆盖不同数据流/架构/场景")
    )
    # 术语漂移粗检：常见同义混用
    pairs = [("模块", "单元"), ("阈值", "门限"), ("判定", "判断")]
    for a, b in pairs:
        if a in text and b in text:
            results.append(("WARN", f"术语可能混用：{a} / {b}", "统一为一个名称并写入术语表"))
    return results


def check_application(text):
    results = []
    for name, pat in SPEC_SECTIONS:
        ok = re.search(pat, text) is not None
        results.append(("PASS" if ok else "FAIL", f"申请文件章节：{name}", "" if ok else "缺少该章节"))

    claims = split_claims(text)
    if not claims:
        results.append(("FAIL", "权利要求解析", "未找到编号权利要求，检查「1. 」格式"))
        return results

    results.append(("PASS", f"权利要求条数：{len(claims)}", ""))

    # 编号连续性
    expected = list(range(1, len(claims) + 1))
    actual = [n for n, _ in claims]
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        dup = [n for n in actual if actual.count(n) > 1]
        results.append(("FAIL", "权项编号连续性", f"缺号 {missing or '无'}；重号 {sorted(set(dup)) or '无'}"))
    else:
        results.append(("PASS", "权项编号连续性", ""))

    # 独立权利要求
    indep = [n for n, c in claims if "根据权利要求" not in c and "根据上述" not in c]
    results.append(("PASS" if indep else "FAIL", f"独立权利要求：{indep or '无'}",
                    "" if indep else "至少需要 1 项独立权利要求"))

    # 多项引多项
    multi = []
    for n, c in claims:
        if re.search(r"根据权利要求\s*\d+\s*(至|到|~|－|-|—|或)\s*\d+", c):
            multi.append(n)
    results.append(("FAIL" if multi else "PASS", "多项引用多项",
                    f"权项 {multi} 存在多项引多项（中国不允许）" if multi else ""))

    # 引用基础（粗检：所述 X 是否在前项或本项前文出现）
    for n, c in claims:
        if n == 1:
            continue
        prior = "".join(x for k, x in claims if k < n)
        own = c.replace("所述", "")
        for term in re.findall(r"所述([^\s，。；、的为是在由与和及所述]{2,6})", c):
            if not term:
                continue
            if term in prior or term in own:
                continue
            results.append(("WARN", f"权项 {n} 引用基础：所述{term}",
                            "该术语在前项与本项前文均未出现，可能缺乏引用基础"))
            break

    # 摘要字数
    m = re.search(r"摘要\s*\n+(.+?)(?=\n#|\Z)", text, re.S)
    if m:
        abstract = re.sub(r"\s", "", m.group(1))
        n = len(abstract)
        results.append(("PASS" if n <= 300 else "FAIL", f"摘要字数：{n}",
                        "" if n <= 300 else "超过 300 字"))
    return results


def check_citations(text):
    """疑似引用核查：列出所有专利号，提示逐条人工核对。"""
    results = []
    ids = re.findall(r"(CN|US|EP|JP|KR|WO)\s?[0-9]{6,13}[A-Z]?\d?", text)
    if ids:
        results.append(("WARN", f"文中出现 {len(ids)} 处专利号",
                        "逐条核对公开号是否真实存在（本脚本无法验证真伪）"))
    if re.search(r"（待补充|TODO|XXX|示例公开号）", text):
        results.append(("WARN", "存在占位符", "交付前清除 TODO/占位内容"))
    if "不构成法律意见" not in text and "需代理师" not in text:
        results.append(("WARN", "免责声明", "缺少「不构成法律意见 / 需代理师审核」声明"))
    return results


def check_paragraph_numbering(text):
    """段落编号连续性：存在编号时须从 [0001] 起连续、无重号缺号；完全无编号时仅 WARN。"""
    nums = [int(m.group(1)) for m in re.finditer(r"^\[(\d{4})\]", text, re.M)]
    if not nums:
        return [("WARN", "段落编号", "未检测到段落编号 [0001]…；正式提交前建议按 [0001] 起连续编号")]
    problems = []
    if nums[0] != 1:
        problems.append(f"起始编号为 [{nums[0]:04d}]，应从 [0001] 起")
    if len(set(nums)) != len(nums):
        problems.append("存在重号")
    expected = list(range(nums[0], nums[0] + len(nums)))
    if nums != expected:
        problems.append("编号不连续或缺号")
    if problems:
        return [("FAIL", "段落编号连续性", "；".join(problems))]
    return [("PASS", "段落编号连续性", f"共 {len(nums)} 段，连续无重号")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--type", choices=["disclosure", "application"], default=None)
    args = ap.parse_args()

    if not Path(args.file).exists():
        print(f"[FAIL] 文件不存在：{args.file}")
        return 2
    text = load(args.file)

    kind = args.type
    if kind is None:
        kind = "application" if ("权利要求" in text and "具体实施方式" in text) else "disclosure"

    checks = check_disclosure(text) if kind == "disclosure" else check_application(text)
    checks += check_citations(text)
    checks += check_paragraph_numbering(text)

    fails = [c for c in checks if c[0] == "FAIL"]
    warns = [c for c in checks if c[0] == "WARN"]
    score = max(0, 100 - 12 * len(fails) - 4 * len(warns))

    print(f"文件：{args.file}")
    print(f"识别类型：{'技术交底书' if kind == 'disclosure' else '申请文件'}")
    print("-" * 62)
    for level, item, note in checks:
        mark = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[level]
        print(f"{mark} {item}" + (f" —— {note}" if note else ""))
    print("-" * 62)
    print(f"结论：PASS {len(checks)-len(fails)-len(warns)} / WARN {len(warns)} / FAIL {len(fails)}   评分 {score}")
    print("提示：机检只覆盖形式项；实质审查（客体、创造性、支持性）需人工逐项过 review-checklist.md。")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

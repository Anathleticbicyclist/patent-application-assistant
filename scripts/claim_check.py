#!/usr/bin/env python3
"""权利要求书结构化解析与形式检查。

比 check_deliverable.py 更细：把权项解析成「类型 / 引用 / 特征项」，做：
1. 多项引多项（中国不允许）——直接判 FAIL
2. 引用基础：从权中的「所述X」必须在被引用权项中已出现
3. 独权特征计数：提示独权是否过窄（特征过多）或过宽（特征过少）
4. 类别覆盖：方法/装置/系统/介质是否成组
5. 禁用语：约、等、适当、优选、最好、例如
6. 摘要字数、摘要附图指定

用法：
    python3 scripts/claim_check.py 权利要求书.md
    python3 scripts/claim_check.py 申请文件.docx --json out.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

# 只保留真正会被审查员挑的模糊用语；「高/低/厚/薄」单字误报率太高，改为词组判断
BANNED = ["大约", "约为", " Approximately", "适当", "优选", "最好", "例如", "诸如",
          "等", "等等", "尽可能", "差不多", "左右"]
# 需要结合语境才判定的模糊表述
BANNED_PHRASES = ["较大的", "较小的", "较高的", "较低的", "较厚", "较薄", "较强", "较弱",
                  "适当范围", "合适的", "根据需要"]
# 白名单：专有名词里合法出现的，不报
WHITELIST = ["高强度", "高精度", "高可靠", "低温", "高温", "高压", "低压", "薄壁", "厚壁",
             "高强度钢", "等号", "等级", "等高线", "等离子"]
CATEGORY_WORDS = {
    "方法": ["方法", "工艺", "流程"],
    "装置": ["装置", "设备", "机构", "器"],
    "系统": ["系统"],
    "介质": ["存储介质", "可读介质", "程序产品"],
}


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
    """定位权利要求书段落并切分。"""
    m = re.search(r"(权利要求书|权\s*利\s*要\s*求\s*书)", text)
    if not m:
        return []
    start = m.end()
    stop = len(text)
    for kw in ("说明书摘要", "说明书\n", "\n说明书", "技术领域"):
        mm = re.search(kw, text[start:])
        if mm:
            stop = min(stop, start + mm.start())
    seg = text[start:stop]

    claims, cur = [], None
    for line in seg.splitlines():
        s = line.strip()
        if not s:
            continue
        m2 = re.match(r"^(\d{1,3})\s*[.、．]\s*(.+)$", s)
        if m2:
            if cur:
                claims.append(cur)
            cur = {"no": int(m2.group(1)), "text": m2.group(2)}
        elif cur:
            cur["text"] += s
    if cur:
        claims.append(cur)

    for c in claims:
        t = c["text"]
        ref = re.search(r"根据权利要求\s*([\d\s至到~\-－—或、,，]+)\s*项?\s*(?:中)?\s*(?:任一项|任意一项)?", t)
        c["refs"] = [int(x) for x in re.findall(r"\d+", ref.group(1))] if ref else []
        c["multi_ref"] = bool(ref and re.search(r"(至|到|~|-|－|—|或|、)", ref.group(1)))
        c["is_dependent"] = "根据权利要求" in t or "根据上述" in t
        subject = t.split("，", 1)[0]          # 只看主题名称，避免从权/从属描述干扰
        c["category"] = next((k for k in ("介质", "系统", "装置", "方法")
                              if any(w in subject for w in CATEGORY_WORDS[k])), "未知")
        c["features"] = split_features(t)
        txt = t
        for wl in WHITELIST:
            txt = txt.replace(wl, "")
        c["banned"] = [w for w in BANNED if w in txt] + \
                      [w for w in BANNED_PHRASES if w in txt]
    return claims


def split_features(text):
    """按「；」与 S1/S2 编号切分技术特征。"""
    body = text.split("其特征在于", 1)[-1]
    parts = re.split(r"[；;]|\bS\d+[、.]|（\d+）|\(\d+\)", body)
    return [p.strip(" ，,。") for p in parts if len(p.strip(" ，,。")) >= 4]


def check(claims, text):
    out = []
    add = out.append

    if not claims:
        add(("FAIL", "未解析到权利要求", "检查「1. 」起始格式"))
        return out

    nums = [c["no"] for c in claims]
    if nums != list(range(1, len(nums) + 1)):
        add(("FAIL", "编号连续性", f"实际 {nums}"))
    else:
        add(("PASS", f"权项数 {len(nums)}，编号连续", ""))

    indep = [c for c in claims if not c["is_dependent"]]
    add(("PASS" if indep else "FAIL", f"独立权利要求 {[c['no'] for c in indep]}",
         "" if indep else "至少需要 1 项独权"))

    # 多项引多项
    bad = [c["no"] for c in claims if c["multi_ref"]]
    add(("FAIL" if bad else "PASS", "多项引多项",
         f"权项 {bad} 引用了多项（中国不允许，须改为单项引用）" if bad else ""))

    # 引用基础
    warn = []
    for c in claims:
        if not c["refs"]:
            continue
        prior = " ".join(x["text"] for x in claims if x["no"] in c["refs"])
        own = c["text"].replace("所述", "")
        for term in re.findall(r"所述([^\s，。；、的为是在由与和及所述]{2,6})", c["text"]):
            if term and term not in prior and term not in own:
                warn.append(f"权项{c['no']}：所述{term}")
        # 「该X」「上述X」「前述X」同样需要引用基础，漏检是常见形式缺陷
        for term in re.findall(r"(?:该|上述|前述)([^\s，。；、的为是在由与和及]{2,8})", c["text"]):
            if term and term not in prior:
                warn.append(f"权项{c['no']}：{term}（该/上述/前述需有引用基础）")
    add(("WARN" if warn else "PASS", "引用基础", "；".join(warn[:6]) if warn else ""))

    # 引用方向（不得引用在后权项）
    forward = [c["no"] for c in claims if any(r >= c["no"] for r in c["refs"])]
    add(("FAIL" if forward else "PASS", "引用方向",
         f"权项 {forward} 引用了自身或在后权项" if forward else ""))

    # 「其特征在于」：独权应有前序部分+特征部分；缺了通常是撰写不规范
    for c in indep:
        if "其特征在于" not in c["text"]:
            add(("WARN", f"独权 {c['no']} 缺「其特征在于」",
                 "建议按「前序部分+其特征在于+特征部分」撰写，便于界定与现有技术的区别"))
    dup = [c["no"] for c in claims if c["text"].count("其特征在于") > 1]
    if dup:
        add(("WARN", "「其特征在于」重复", f"权项 {dup} 出现多次，通常只需一次"))

    # 从权主题名称必须与所引独权一致（否则类型错乱，如方法权项引用装置权项）
    mismatch = []
    for c in claims:
        if not c["refs"]:
            continue
        parent = next((x for x in claims if x["no"] == min(c["refs"]))
                      if c["refs"] else None, None)
        if parent and c["category"] != "未知" and parent["category"] != "未知" \
                and c["category"] != parent["category"]:
            mismatch.append(f"权项{c['no']}({c['category']}) 引用权项{parent['no']}({parent['category']})")
    add(("WARN" if mismatch else "PASS", "从权主题一致性",
         "；".join(mismatch) if mismatch else ""))

    # 独权特征数
    for c in indep:
        n = len(c["features"])
        if n > 8:
            add(("WARN", f"独权 {c['no']} 特征数 {n}", "偏多，可能含非必要特征，保护范围被压缩"))
        elif n < 2 and c["category"] == "方法":
            add(("WARN", f"独权 {c['no']} 特征数 {n}", "方法独权特征偏少，可能过于上位，易被现有技术覆盖"))
        elif n < 2:
            add(("PASS", f"独权 {c['no']} 特征数 {n}", "装置/介质类以整机或处理器+存储器表述，属正常"))
        else:
            add(("PASS", f"独权 {c['no']} 特征数 {n}", ""))

    # 类别覆盖
    cats = {c["category"] for c in indep}
    missing = [k for k in ("方法", "装置") if k not in cats]
    add(("WARN" if missing else "PASS", "类别覆盖",
         f"独权类别 {sorted(cats)}，建议补充：{missing}" if missing else f"独权类别 {sorted(cats)}"))

    # 禁用语（已过白名单）
    hits = [(c["no"], c["banned"]) for c in claims if c["banned"]]
    add(("WARN" if hits else "PASS", "禁用语/不确定用语",
         "；".join(f"权项{n}:{'、'.join(w)}" for n, w in hits) if hits else ""))

    # 说明书支持（第 26 条第 4 款粗筛）：权项里的技术术语在说明书里找不到，就可能缺支持
    m_spec = re.search(r"具体实施方式|实施例", text)
    spec = text[m_spec.start():] if m_spec else text
    claim_terms = set()
    for c in claims:
        # 先按标点切段，避免「温度信号与电压信号」这类跨段拼接成假术语
        for seg in re.split(r"[，。；：、（）()]", c["text"]):
            seg = seg.replace("所述", "").replace("上述", "").replace("前述", "").replace("该", "")
            seg = re.sub(r"^[与和及将基于采用通过再次采集大于小于等于包括其中当若在是有]+", "", seg.strip())
            for term in re.findall(
                    r"(?:(?![的之了与和及对])[一-龥]){2,6}(?:模块|单元|装置|参数|阈值|信号|数据|模型|网络|接口|矩阵|向量)", seg):
                # 去掉匹配结果前残留的动词/连词，避免产出「再次采集温度信号」这类假术语
                term = re.sub(r"^[的与和及且并在将对把由向以按从再次采集大于小等包括其中当若是内有外后前上下率仍还又均全且]+", "", term)
                if len(term) >= 3:
                    claim_terms.add(term)
        for term in re.findall(r"\b[A-Z]{2,6}\b", c["text"]):
            claim_terms.add(term)
    # 只保留长度合理、且不是通用词的术语
    GENERIC = {"装置", "方法", "系统", "介质", "模块", "单元", "信号", "数据"}
    claim_terms = {t for t in claim_terms if len(t) >= 3 and t not in GENERIC}
    unsupported = sorted(t for t in claim_terms if t not in spec)
    if claim_terms:
        ratio = 1 - len(unsupported) / len(claim_terms)
        note = ""
        if unsupported:
            note = f"未在说明书中出现：{'、'.join(unsupported[:6])}"
        add(("WARN" if unsupported else "PASS",
             f"说明书支持度 {ratio:.0%}（{len(claim_terms)-len(unsupported)}/{len(claim_terms)} 个术语可溯源）", note))

    # 摘要附图
    if "摘要附图" not in text:
        add(("WARN", "未指定摘要附图", "有附图时须指定其中一幅为摘要附图"))

    # 摘要
    m = re.search(r"摘要\s*\n+(.+?)(?=\n#|\Z)", text, re.S)
    if m:
        n = len(re.sub(r"\s", "", m.group(1)))
        add(("PASS" if n <= 300 else "FAIL", f"摘要字数 {n}", "" if n <= 300 else "超过 300 字"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    text = read_text(args.file)
    claims = extract_claims(text)
    results = check(claims, text)

    fails = [r for r in results if r[0] == "FAIL"]
    warns = [r for r in results if r[0] == "WARN"]
    score = max(0, 100 - 15 * len(fails) - 5 * len(warns))

    print(f"文件：{args.file}")
    print("-" * 64)
    for level, item, note in results:
        mark = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[level]
        print(f"{mark} {item}" + (f" —— {note}" if note else ""))
    print("-" * 64)
    print(f"PASS {len(results)-len(fails)-len(warns)} / WARN {len(warns)} / FAIL {len(fails)}   评分 {score}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"claims": claims, "results": results, "score": score},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"明细已写入 {args.json}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

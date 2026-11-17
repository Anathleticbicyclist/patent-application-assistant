#!/usr/bin/env python3
"""P0.5 合规闸门：把五项先决条件问完并生成闸门卡。

不判断对错，只负责「问全」和「拦住」——任一必答项为空就返回 1。
用法：
    python3 scripts/compliance_check.py --interactive
    python3 scripts/compliance_check.py --answers answers.json --out gate.md
answers.json 示例：
    {"owner": "职务发明（单位）", "owner_basis": "劳动合同第7条",
     "public": "已公开", "public_date": "2026-03-01", "public_way": "产品上线",
     "in_art24": "否", "abroad": "是", "data_out": "否", "unity": "单一方案", "deadline": "无"}
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

QUESTIONS = [
    ("owner", "权属", ["职务发明（单位）", "个人", "合作共有", "委托（受托方）"], "谁有权申请？"),
    ("owner_basis", "权属依据", None, "依据是什么？（劳动合同/开发协议/无约定）"),
    ("public", "公开状态", ["未公开", "已公开"], "方案是否已对外公开？"),
    ("public_date", "公开日期", None, "若已公开，首次公开日期（YYYY-MM-DD）？"),
    ("public_way", "公开方式", ["论文", "展会", "学术会议", "发布会/上线", "客户交付", "开源", "他人泄露", "其他"],
     "以什么方式公开？"),
    ("in_art24", "是否属第24条情形", ["是", "否", "不确定"], "是否属于专利法第24条的四类情形？"),
    ("abroad", "是否境外申请", ["否", "是", "未定"], "是否计划向外国申请专利？"),
    ("filed_in_cn", "是否已先在中国提交", ["是", "否", "未定"], "是否已先在中国提交申请？"),
    ("data_out", "数据是否外发", ["否（仅本地处理）", "是（已脱敏）", "是（未脱敏）"],
     "技术方案是否会发给境外 API / 外部服务？"),
    ("unity", "单一性", ["单一方案", "多发明点（需分案）"], "是一个发明点还是多个？"),
    ("deadline", "硬期限", None, "有无不可错过的期限？（优先权12个月/PCT30个月/答复期限）"),
]

REQUIRED = {"owner", "owner_basis", "public", "abroad", "filed_in_cn", "data_out", "unity", "deadline"}


def evaluate(a):
    """根据答案给出风险提示——只做规则推导，不做法律结论。"""
    risks = []

    basis = str(a.get("owner_basis") or "")
    # 「无协议」「没有约定」「未签」都表示缺依据——不能只判有无「协议」二字
    no_agreement = any(k in basis for k in ("无", "没有", "未签", "未约定", "口头"))
    if a.get("owner") in ("合作共有", "委托（受托方）") and (not basis or no_agreement):
        risks.append(("高", "权属", "共有/委托情形下若无书面约定，权属极易争议；申请前必须补齐协议或取得书面同意。"))

    if a.get("public") == "已公开":
        date = str(a.get("public_date") or "")
        way = a.get("public_way", "")
        in24 = a.get("in_art24", "")
        if in24 == "否":
            risks.append(("高", "新颖性", f"已以「{way}」方式公开且不属第24条情形——新颖性已丧失，"
                                       "建议改以改进点申请，或评估是否有未公开的后续改进。"))
        elif in24 == "不确定":
            risks.append(("高", "新颖性", "公开方式是否落入第24条需逐条核对；不确定时按「已丧失新颖性」处理。"))
        if date:
            try:
                d = datetime.strptime(date, "%Y-%m-%d")
                days = (datetime.now() - d).days
                risks.append(("中", "宽限期", f"距首次公开 {days} 天，是否仍在法定宽限期内、能否享受宽限期保护，"
                                           "须由代理师核对公开日期、场合与证明材料后确认（以通知书指定期限为准）。"))
            except ValueError:
                risks.append(("中", "日期格式", f"公开日期「{date}」无法解析，请用 YYYY-MM-DD。"))

    if a.get("abroad") in ("是", "未定"):
        risks.append(("高", "保密审查", "在中国完成的发明向外国申请前，必须先请求保密审查（专利法第19条）；"
                                      "未办的后果是：该技术方案在中国申请专利时不予授权。"))

    if a.get("data_out") == "是（未脱敏）":
        risks.append(("高", "数据出境", "未脱敏外发等于技术秘密外泄，且可能触及数据出境合规。"
                                     "须先脱敏（去配方/参数/客户标识）再外发。"))

    if a.get("unity") == "多发明点（需分案）":
        risks.append(("中", "单一性", "多个发明点合案申请会被要求分案；建议在 P2 就拆分为多件，"
                                    "或明确主案 + 分案的布局。"))

    return risks


def render(a, risks):
    lines = ["# P0.5 合规闸门卡", "",
             f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
             "| 项 | 答案 |", "|---|---|"]
    for key, label, _, _ in QUESTIONS:
        lines.append(f"| {label} | {a.get(key, '（未填）')} |")

    lines += ["", "## 风险提示", ""]
    if not risks:
        lines.append("未发现高风险项。仍需代理师确认法条适用。")
    else:
        for level, cat, msg in risks:
            mark = {"高": "🔴", "中": "🟡", "低": "🟢"}[level]
            lines.append(f"- {mark} **{level}｜{cat}**：{msg}")

    missing = [label for key, label, _, _ in QUESTIONS if key in REQUIRED and not a.get(key)]
    lines += ["", "## 结论", ""]
    if missing:
        lines.append(f"❌ **不得进入 P6 撰写**——以下必答项未填：{'、'.join(missing)}")
    elif any(r[0] == "高" for r in risks):
        lines.append("⚠️ 存在高风险项，须先解决或由代理师书面确认后才能继续撰写。")
    else:
        lines.append("✅ 闸门通过，可进入 P1/P6。")

    lines += ["", "> 本卡由脚本按规则推导，不构成法律意见。法条适用与权属认定须由代理师/律师确认。", ""]
    return "\n".join(lines), missing


def ask_interactive():
    a = {}
    for key, label, choices, q in QUESTIONS:
        print(f"\n【{label}】{q}")
        if choices:
            for i, c in enumerate(choices, 1):
                print(f"  {i}. {c}")
            while True:
                v = input("选择编号（回车跳过）：").strip()
                if not v:
                    break
                if v.isdigit() and 1 <= int(v) <= len(choices):
                    a[key] = choices[int(v) - 1]
                    break
                print("  请输入有效编号")
        else:
            a[key] = input("> ").strip()
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", help="答案 JSON")
    ap.add_argument("--out", default="out/compliance-gate-card.md")
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--print-only", action="store_true", help="只打印不写文件")
    args = ap.parse_args()

    if args.interactive:
        a = ask_interactive()
    elif args.answers:
        try:
            a = json.loads(Path(args.answers).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print(f"[FAIL] 答案文件不存在或无法解析：{args.answers}")
            a = {}
    else:
        print("需要 --interactive 或 --answers。用 --print-only 可只看模板。")
        a = {}

    risks = evaluate(a)
    card, missing = render(a, risks)
    print(card)
    if not args.print_only:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(card, encoding="utf-8")
        print(f"已写入 {args.out}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

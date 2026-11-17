#!/usr/bin/env python3
"""查新检索编排：从技术描述生成可复现的检索式、可点击的检索链接、检索记录骨架。

设计原则：
1. 没有 API 凭据时**不假装检索**——输出检索式与链接，命中数留空待人工填写。
2. 有凭据时调用真实 API，命中结果原样落盘，不做任何推测性补全。
3. 每条检索式都同时给出「查全/查准/定向」三档，避免单一检索式得出「无现有技术」的错误结论。

用法：
    python3 scripts/prior_art_search.py --topic "电池热失控预警" \
        --keywords "热失控,热失控预警,thermal runaway,thermal propagation" \
        --ipc "H01M10,G01R31" --country CN --year-from 2015 --out ./search

    # 可选：真实调用（需环境变量）
    python3 scripts/prior_art_search.py ... --provider pqai
环境变量：
    PQAI_TOKEN       PQAI API token（https://api.projectpq.ai）
    EPO_OPS_KEY / EPO_OPS_SECRET    EPO OPS 凭据
    USPTO_API_KEY    USPTO Open Data Portal 的 X-API-KEY
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path


# ---------- 检索式构造 ----------

def norm_terms(raw):
    """把逗号/顿号/分号分隔的词表切成去重列表。"""
    parts = re.split(r"[,，;；、\n]+", raw or "")
    return [p.strip() for p in parts if p.strip()]


def build_queries(topic, keywords, ipc, country, year_from):
    """生成三档检索式（中文库 / 英文库各一套）。"""
    kw = keywords
    cn_terms = [k for k in kw if re.search(r"[\u4e00-\u9fff]", k)]
    en_terms = [k for k in kw if not re.search(r"[\u4e00-\u9fff]", k)]
    ipc_expr = " OR ".join(ipc) if ipc else ""

    cn_or = " OR ".join(cn_terms) if cn_terms else topic
    en_or = " OR ".join(f'"{t}"' for t in en_terms) if en_terms else f'"{topic}"'

    q = []
    q.append({
        "id": "S1-CN", "档位": "查全", "库": "CNIPA / Google Patents(中文)",
        "检索式": f"TI=({cn_or}) OR AB=({cn_or})",
        "说明": "只用品名与同义词，先看有没有人做过同类东西",
    })
    q.append({
        "id": "S2-CN", "档位": "查准", "库": "CNIPA",
        "检索式": f"(TI=({cn_or}) OR AB=({cn_or}))" + (f" AND IPC=({ipc_expr})" if ipc_expr else ""),
        "说明": "叠加分类号，压掉跨领域噪声",
    })
    q.append({
        "id": "S1-EN", "档位": "查全", "库": "Google Patents / Espacenet / PATENTSCOPE",
        "检索式": en_or,
        "说明": "英文表达覆盖度通常高于中文，必查",
    })
    q.append({
        "id": "S2-EN", "档位": "查准", "库": "Espacenet / USPTO",
        "检索式": f"({en_or})" + (f" AND CPC=({ipc_expr})" if ipc_expr else ""),
        "说明": "CPC 比 IPC 更细，适合软件/算法类",
    })
    q.append({
        "id": "S3-ASSIGNEE", "档位": "定向", "库": "CNIPA / Google Patents",
        "检索式": f"({cn_or}) AND (AN=(竞品公司名) OR AN=(重点对手名))",
        "说明": "追竞品与重点对手的在先布局，填上真实申请人后使用",
    })
    for item in q:
        item["时间限定"] = f"{year_from}-01-01 至今" if year_from else "不限"
        item["国别"] = country or "不限"
    return q


def build_links(query_text, year_from, country):
    """生成各库可直接点开的检索链接（能带 query 参数的才带）。"""
    q = urllib.parse.quote(query_text)
    year = f"{year_from}-01-01" if year_from else ""
    links = {
        "Google Patents": f"https://patents.google.com/?q={q}"
                          + (f"&after=priority:{year.replace('-', '')}" if year_from else "")
                          + (f"&country={country}" if country else ""),
        "Espacenet": f"https://worldwide.espacenet.com/patent/search?q={q}",
        "WIPO PATENTSCOPE": f"https://patentscope.wipo.int/search/en/result.jsf?query={q}",
        "CNIPA 专利检索及分析": "https://pss-system.cponline.cnipa.gov.cn/",
        "USPTO Patent Public Search": "https://ppubs.uspto.gov/pubwebapp/",
    }
    return links


# ---------- 真实检索（可选） ----------

def fetch_pqai(query, limit=10):
    token = os.getenv("PQAI_TOKEN")
    if not token:
        return None, "未配置 PQAI_TOKEN，跳过在线检索"
    try:
        import requests
    except ImportError:
        return None, "缺少 requests"
    try:
        r = requests.get(f"https://api.projectpq.ai/search/{limit}",
                         params={"q": query, "token": token}, timeout=30)
        if r.status_code != 200:
            return None, f"PQAI HTTP {r.status_code}: {r.text[:120]}"
        data = r.json()
        return [{"id": x.get("id"), "title": x.get("title"),
                 "abstract": (x.get("abstract") or "")[:300]} for x in data.get("results", [])], None
    except Exception as exc:
        return None, f"PQAI 调用失败: {exc}"


def fetch_epo(query, limit=10):
    key, secret = os.getenv("EPO_OPS_KEY"), os.getenv("EPO_OPS_SECRET")
    if not (key and secret):
        return None, "未配置 EPO_OPS_KEY/SECRET，跳过在线检索"
    try:
        import requests
        tok = requests.post("https://ops.epo.org/3.2/auth/accesstoken",
                            data={"grant_type": "client_credentials"},
                            auth=(key, secret), timeout=30)
        access = tok.json().get("access_token")
        r = requests.get("https://ops.epo.org/3.2/rest-services/published-data/search",
                         params={"q": query, "Range": f"1-{limit}"},
                         headers={"Authorization": f"Bearer {access}",
                                  "Accept": "application/json"}, timeout=30)
        return [{"raw": r.text[:2000]}], None
    except Exception as exc:
        return None, f"EPO OPS 调用失败: {exc}"


def fetch_uspto(query, limit=10):
    key = os.getenv("USPTO_API_KEY")
    if not key:
        return None, "未配置 USPTO_API_KEY，跳过在线检索"
    try:
        import requests
        r = requests.get("https://api.uspto.gov/api/v1/patent/applications/search",
                         params={"q": query, "limit": limit},
                         headers={"X-API-KEY": key}, timeout=30)
        if r.status_code != 200:
            return None, f"USPTO HTTP {r.status_code}: {r.text[:120]}"
        return r.json().get("results", []), None
    except Exception as exc:
        return None, f"USPTO 调用失败: {exc}"


PROVIDERS = {"pqai": fetch_pqai, "epo": fetch_epo, "uspto": fetch_uspto}

# 凭据 → provider 的探测顺序，auto 模式按此顺序找第一个可用的
CREDENTIALS = {
    "pqai": ("PQAI_TOKEN",),
    "epo": ("EPO_OPS_KEY", "EPO_OPS_SECRET"),
    "uspto": ("USPTO_API_KEY",),
}


def available_providers():
    """返回当前环境里凭据齐全的 provider（顺序即优先级）。"""
    return [name for name, keys in CREDENTIALS.items()
            if all(os.getenv(k) for k in keys)]


def degrade_note():
    """没有任何凭据时的降级说明——不是错误，是明示边界。"""
    missing = ", ".join(k for keys in CREDENTIALS.values() for k in keys)
    return (f"未检测到可用的检索 API 凭据（{missing} 均未设置），"
            "已降级为**检索计划模式**：检索式与直链可直接在浏览器执行，命中数请回填。")


# ---------- 输出 ----------

def render_plan(topic, queries, links, provider_note, hits):
    lines = [f"# 查新检索计划：{topic}", "",
             f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
             "> 命中数一栏**留空由检索人填写**。未实际执行的数据不得填入。", "",
             "## 一、检索式", "",
             "| # | 档位 | 数据源 | 检索式 | 时间/国别 | 命中数 |",
             "|---|---|---|---|---|---|"]
    for q in queries:
        lines.append(f"| {q['id']} | {q['档位']} | {q['库']} | `{q['检索式']}` | "
                     f"{q['时间限定']} / {q['国别']} |  |")
    lines += ["", "## 二、可直接打开的检索链接", ""]
    for name, url in links.items():
        lines.append(f"- [{name}]({url})")
    lines += ["", "## 三、在线检索结果", ""]
    if provider_note:
        lines.append(f"- {provider_note}")
    if hits:
        for h in hits:
            lines.append(f"- `{h.get('id')}` {h.get('title', '')}")
    if not hits:
        lines.append("- 本次未取得在线结果；链接与检索式已就绪，可在浏览器中逐条执行并回填命中数。")
    lines += ["", "## 四、必填的检索局限说明", "",
              "> 例：仅检索中英文库，未覆盖日韩原文；未检索非专利文献中的企业内部标准。",
              "> 检索不可能是穷尽的，写明边界比假装穷尽更专业。", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="生成可复现的查新检索计划")
    ap.add_argument("--topic", required=True, help="技术主题（一句话）")
    ap.add_argument("--keywords", default="", help="关键词，逗号分隔，中英文都要给")
    ap.add_argument("--ipc", default="", help="IPC/CPC 主分类，逗号分隔，如 H01M10,G06F16")
    ap.add_argument("--country", default="", help="国别限定，如 CN/US/EP")
    ap.add_argument("--year-from", type=int, default=None, help="起始年份")
    ap.add_argument("--out", default=".", help="输出目录")
    ap.add_argument("--provider", choices=list(PROVIDERS) + ["auto", ""], default="auto",
                    help="auto=有凭据就调、没凭据静默降级；也可指定 pqai/epo/uspto；留空=只出计划")
    ap.add_argument("--confirm-egress", action="store_true",
                    help="已核对外发合规后方可调用外部检索接口；未确认时只生成检索计划，不发请求")
    args = ap.parse_args()

    kw = norm_terms(args.keywords) or [args.topic]
    ipc = norm_terms(args.ipc)
    queries = build_queries(args.topic, kw, ipc, args.country, args.year_from)

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    # 链接：以最宽的那条英文式为准
    links = build_links(queries[2]["检索式"], args.year_from, args.country)

    note, hits = None, None
    provider = args.provider
    if provider == "auto":
        usable = available_providers()
        provider = usable[0] if usable else ""
        if not provider:
            note = degrade_note()
        else:
            print(f"[auto] 检测到凭据，使用 provider: {provider}")
    if provider and not args.confirm_egress:
        # 外发确认闸门：检测到可用凭据但未确认外发合规时，不发起任何请求，仅出检索计划
        note = "已检测到检索凭据，但未确认外发合规（--confirm-egress），本次仅生成检索计划。"
        hits = None
    elif provider:
        hits, note = PROVIDERS[provider](queries[2]["检索式"], 10)

    plan = render_plan(args.topic, queries, links, note, hits)
    (outdir / "search-plan.md").write_text(plan, encoding="utf-8")
    (outdir / "queries.json").write_text(
        json.dumps({"topic": args.topic, "queries": queries, "links": links},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print(plan)
    print(f"\n已写出：{outdir/'search-plan.md'}、{outdir/'queries.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

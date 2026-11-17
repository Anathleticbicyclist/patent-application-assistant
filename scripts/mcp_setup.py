#!/usr/bin/env python3
"""把高频专利 MCP 接入 Agent 的配置生成器。

覆盖三个最常用、且能覆盖不同数据面的 MCP：
1. patsnap/patent-literature-search-mcp —— 六大局（WIPO/EPO/USPTO/CNIPA/JPO/KIPO）+ 文献
2. riemannzeta/patent_mcp_server —— USPTO 深水区（审查档案 / PTAB / 诉讼 / 转让）
3. KunihiroS/google-patents-mcp —— Google Patents 自然语言检索

只生成配置文件，不执行安装、不写入任何密钥明文（用 ${ENV} 占位）。

用法：
    python3 scripts/mcp_setup.py --target claude     # 打印并写 .mcp.json
    python3 scripts/mcp_setup.py --target codex      # 打印 TOML 片段
    python3 scripts/mcp_setup.py --target print
    python3 scripts/mcp_setup.py --target claude --pillars search   # 只接检索类
"""
import argparse
import json
import sys
from pathlib import Path

SERVERS = {
    "patsnap": {
        "command": "npx",
        "args": ["-y", "@patsnap/patent-literature-search-mcp"],
        "env": {"PATSNAP_API_KEY": "${PATSNAP_API_KEY}"},
        "说明": "六大局专利 + 科学文献统一检索；有免费额度，需在智慧芽开放平台申请 Key",
        "pillar": "search",
    },
    "uspto-deep": {
        "command": "uvx",
        "args": ["patent-mcp-server"],
        "env": {"USPTO_API_KEY": "${USPTO_API_KEY}"},
        "说明": "USPTO 审查档案、PTAB 程序、诉讼、转让；需要 USPTO Open Data Portal 的 API Key",
        "pillar": "search",
    },
    "google-patents": {
        "command": "npx",
        "args": ["-y", "google-patents-mcp"],
        "env": {},
        "说明": "Google Patents 自然语言/全文检索，无需 Key（受反爬与速率限制）",
        "pillar": "search",
    },
}

PILLARS = {
    "search": ["patsnap", "uspto-deep", "google-patents"],
    "draft": [],
    "review": [],
}


def build(selected):
    out = {}
    for name in selected:
        cfg = SERVERS[name]
        entry = {"command": cfg["command"], "args": cfg["args"]}
        if cfg["env"]:
            entry["env"] = cfg["env"]
        out[name] = entry
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["claude", "codex", "print", "cursor"], default="print")
    ap.add_argument("--pillars", default="search", help="要接入的能力组，逗号分隔（search）")
    ap.add_argument("--out", default="", help="输出路径（默认按 target 决定）")
    args = ap.parse_args()

    picked = []
    for p in [x.strip() for x in args.pillars.split(",") if x.strip()]:
        picked += [n for n in PILLARS.get(p, []) if n not in picked]
    if not picked:
        print("没有可接入的条目（当前仅 search 组有可用 MCP）。")
        return 1

    servers = build(picked)

    if args.target in ("claude", "cursor", "print"):
        payload = {"mcpServers": servers}
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        path = args.out or (".mcp.json" if args.target == "claude" else "")
    else:
        lines = []
        for name, cfg in servers.items():
            lines.append(f"[mcp_servers.{name}]")
            lines.append(f'command = "{cfg["command"]}"')
            lines.append("args = [" + ", ".join(f'"{a}"' for a in cfg["args"]) + "]")
            for k, v in cfg.get("env", {}).items():
                lines.append(f'env = {{ {k} = "{v}" }}')
            lines.append("")
        text = "\n".join(lines)
        path = args.out or ""

    print(text)
    print("\n--- 接入说明 ---")
    for name in picked:
        print(f"- {name}: {SERVERS[name]['说明']}")
    print("\n环境变量（真实值请自行 export，勿提交到仓库）：")
    for name in picked:
        for k in SERVERS[name]["env"]:
            print(f"  export {k}=<your-key>")
    if path:
        Path(path).write_text(text, encoding="utf-8")
        print(f"\n已写入 {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

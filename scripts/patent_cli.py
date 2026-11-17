#!/usr/bin/env python3
"""专利申请助手 · 统一命令行入口。

    python3 scripts/patent_cli.py search  --topic "..." --keywords "..." --ipc H01M10 --out ./out
    python3 scripts/patent_cli.py figure  --spec fig.json --out fig2.png
    python3 scripts/patent_cli.py claims  application.md
    python3 scripts/patent_cli.py chart   --claims application.md --map map.json --out chart.md
    python3 scripts/patent_cli.py check   交底书.md
    python3 scripts/patent_cli.py mcp     --target claude

每个子命令都是对独立脚本的薄封装，便于单独调用也便于串成流水线。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

COMMANDS = {
    "pipeline": ("pipeline.py", "一条命令跑完：机检→查新→权项→附图→比对→汇总"),
    "search": ("prior_art_search.py", "生成查新检索计划（检索式 + 链接 + 记录表）"),
    "figure": ("figure_gen.py", "生成国知局格式的黑白说明书附图"),
    "claims": ("claim_check.py", "权利要求形式检查（引用基础/多项引多项/禁用语）"),
    "chart": ("claim_chart.py", "侵权比对表（逐要素判定 + 全覆盖结论）"),
    "check": ("check_deliverable.py", "交付物机检（章节/编号/摘要/占位符）"),
    "mcp": ("mcp_setup.py", "生成高频专利 MCP 的接入配置"),
}


def usage():
    print("用法：python3 scripts/patent_cli.py <子命令> [参数...]\n")
    print("子命令：")
    for k, (_, desc) in COMMANDS.items():
        print(f"  {k:<8} {desc}")
    print("\n示例：")
    print('  python3 scripts/patent_cli.py pipeline --doc 交底书.md --ipc H01M10 --out ./run1')
    print('  python3 scripts/patent_cli.py search --topic "电池热失控预警" '
          '--keywords "热失控,thermal runaway" --ipc H01M10 --out ./search')
    print("  python3 scripts/patent_cli.py claims 申请文件.md")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        usage()
        return 0
    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"未知子命令：{cmd}\n")
        usage()
        return 2
    script, _ = COMMANDS[cmd]
    target = HERE / script
    if not target.exists():
        print(f"缺少脚本：{target}")
        return 2
    return subprocess.call([sys.executable, str(target)] + sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())

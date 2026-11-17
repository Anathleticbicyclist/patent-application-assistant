#!/usr/bin/env python3
"""最小回归测试：不依赖 pytest，直接 python3 tests/test_checks.py 运行。

覆盖三件事：
1. 合格样例必须全绿（PASS 12 / FAIL 0）——防止检查器误报
2. 缺陷样例必须被抓出（多项引多项 FAIL、支持度不足 WARN）——防止检查器漏报
3. 附图必须真的产出纯黑白图片——防止依赖变更后静默失真
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples" / "battery-case"
PY = sys.executable


def run(script, *args):
    p = subprocess.run([PY, str(ROOT / "scripts" / script)] + list(args),
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


failures = []


def expect(name, cond, detail=""):
    if cond:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name} {detail}")
        failures.append(name)


print("1. 合格样例")
rc, out = run("claim_check.py", str(EX / "application.md"))
expect("退出码 0", rc == 0, f"实际 {rc}")
expect("无 FAIL", "FAIL 0" in out)
expect("支持度 100%", "支持度 100%" in out)

print("2. 缺陷样例")
rc, out = run("claim_check.py", str(EX / "application-defective.md"))
expect("退出码 1", rc == 1, f"实际 {rc}")
expect("检出多项引多项", "多项引多项" in out and "❌" in out)
expect("检出支持度不足", "支持度 0%" in out)
expect("检出缺摘要附图", "未指定摘要附图" in out)

print("3. 附图二值化")
tmp = Path("/tmp/_patent_fig_test.png")
rc, out = run("figure_gen.py", "--spec", str(EX / "fig.json"), "--out", str(tmp))
expect("生成成功", rc == 0 and tmp.exists())
try:
    from PIL import Image
    im = Image.open(tmp).convert("L")
    levels = {v for _, v in im.getcolors(maxcolors=100000)}
    expect("纯黑白（仅 2 个灰度级）", len(levels) == 2, f"实际 {sorted(levels)[:5]}")
except ImportError:
    print("  ⚠️ 未安装 Pillow，跳过二值化校验")

print("4. 检索计划（无凭据降级）")
rc, out = run("prior_art_search.py", "--topic", "测试", "--keywords", "a,b",
              "--out", "/tmp/_patent_search_test")
expect("退出码 0", rc == 0, f"实际 {rc}")
expect("明确标注降级，不编造命中数", "降级" in out)

print("5. 合规闸门")
rc, out = run("compliance_check.py", "--answers", str(Path("/tmp/pt/ans.json"))
              if Path("/tmp/pt/ans.json").exists() else "--print-only")
expect("能输出闸门卡", "合规闸门卡" in out)

print()
if failures:
    print(f"❌ {len(failures)} 项未通过：{failures}")
    sys.exit(1)
print("✅ 全部通过")

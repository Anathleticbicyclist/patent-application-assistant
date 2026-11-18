#!/usr/bin/env python3
"""最小回归测试：不依赖 pytest，直接 python3 tests/test_checks.py 运行。

覆盖三件事：
1. 合格样例必须全绿（PASS 12 / FAIL 0）——防止检查器误报
2. 缺陷样例必须被抓出（多项引多项 FAIL、支持度不足 WARN）——防止检查器漏报
3. 附图必须真的产出纯黑白图片——防止依赖变更后静默失真
"""
import json
import subprocess
import sys
import tempfile
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
gate_dir = Path(tempfile.mkdtemp(prefix="patent_gate_"))
gate_answers = {
    "owner": "职务发明（单位）",
    "owner_basis": "劳动合同第7条",
    "public": "未公开",
    "abroad": "否",
    "filed_in_cn": "是",
    "data_out": "否（仅本地处理）",
    "unity": "单一方案",
    "deadline": "无",
}
ans_file = gate_dir / "answers.json"
ans_file.write_text(json.dumps(gate_answers, ensure_ascii=False), encoding="utf-8")
rc, out = run("compliance_check.py", "--answers", str(ans_file), "--print-only")
expect("能输出闸门卡", "合规闸门卡" in out)
expect("答案齐全时闸门通过（退出码 0）", rc == 0, f"实际 {rc}")

# 删掉一个必答项 → 退出码 1
missing_answers = dict(gate_answers)
del missing_answers["owner"]
miss_file = gate_dir / "answers-missing.json"
miss_file.write_text(json.dumps(missing_answers, ensure_ascii=False), encoding="utf-8")
rc, out = run("compliance_check.py", "--answers", str(miss_file), "--print-only")
expect("必答项缺失时退出码 1", rc == 1, f"实际 {rc}")

print("6. 其余脚本回归（此前零用例）")
# check_deliverable：合格样例无 FAIL，退出码 0
rc, out = run("check_deliverable.py", str(EX / "application.md"))
expect("check_deliverable 合格样例退出码 0", rc == 0, f"实际 {rc}")

# claim_chart：基于合格样例与比对映射生成比对表文件
chart_dir = Path(tempfile.mkdtemp(prefix="patent_chart_"))
chart_out = chart_dir / "chart.md"
rc, out = run("claim_chart.py", "--claims", str(EX / "application.md"),
              "--map", str(EX / "claim-map.json"), "--out", str(chart_out))
expect("claim_chart 生成比对表", rc == 0 and chart_out.exists(), f"实际 {rc}")

# mcp_setup：--help 可用；生成的配置含 mcpServers 段
rc, out = run("mcp_setup.py", "--help")
expect("mcp_setup --help 退出码 0", rc == 0, f"实际 {rc}")
rc, out = run("mcp_setup.py", "--target", "print")
expect("mcp_setup 生成配置含 mcpServers", "mcpServers" in out)

# patent_cli：--help 可用
rc, out = run("patent_cli.py", "--help")
expect("patent_cli --help 退出码 0", rc == 0, f"实际 {rc}")

# pipeline：合格样例跑全流程到临时目录
pipe_dir = Path(tempfile.mkdtemp(prefix="patent_pipe_"))
rc, out = run("pipeline.py", "--doc", str(EX / "application.md"), "--out", str(pipe_dir))
expect("pipeline 合格样例退出码 0", rc == 0, f"实际 {rc}")

print("7. 洗涤电器领域专项检查（合成文本，不依赖 examples/laundry-case）")
laundry_dir = Path(tempfile.mkdtemp(prefix="patent_laundry_"))

# 文本 A：多筒指代不清 + 装置独权缺连接关系 + 实施例缺六类字段
text_a = """# 技术领域
本方案涉及一种双筒洗衣机，含内筒与外桶。

## 权利要求书
1. 一种双筒洗衣机装置，其特征在于，包括大筒、小筒和分水阀，大筒用于洗涤外衣，小筒用于洗涤内衣，分水阀向大筒和小筒供水，另一筒配置独立悬挂结构。

## 具体实施方式
实施例：本方案洗涤效果好，用户体验佳。
"""
file_a = laundry_dir / "laundry-a.md"
file_a.write_text(text_a, encoding="utf-8")
rc, out_a = run("claim_check.py", str(file_a))
expect("文本 A 退出码 0（领域检查只出 WARN）", rc == 0, f"实际 {rc}")
expect("文本 A 检出多筒指代不清", "多筒指代不清" in out_a)
expect("文本 A 检出实施例缺字段", "实施例缺字段" in out_a)
expect("文本 A 检出装置独权缺连接关系", "未写出连接关系或位置关系" in out_a)
expect("文本 A 无 FAIL", "FAIL 0" in out_a)

# 文本 B：指代唯一、写明连接关系、实施例六类字段齐全 → 不应出现领域 WARN
text_b = """# 技术领域
本方案涉及一种双筒洗衣机，含内筒与外桶。

## 权利要求书
1. 一种双筒洗衣机装置，其特征在于，包括机箱、大筒、小筒和分水阀，大筒固定于机箱一侧，小筒固定于机箱另一侧，分水阀与分排水管路连通，大筒用于洗涤外衣，小筒用于洗涤内衣。

## 具体实施方式
实施例：水位 25L、温度 40℃、转速 1200rpm、错峰时间窗 30s、大筒衣物 5kg，对照位移量 2mm（示例值）。
"""
file_b = laundry_dir / "laundry-b.md"
file_b.write_text(text_b, encoding="utf-8")
rc, out_b = run("claim_check.py", str(file_b))
expect("文本 B 退出码 0", rc == 0, f"实际 {rc}")
expect("文本 B 无多筒指代不清", "多筒指代不清" not in out_b)
expect("文本 B 无实施例缺字段", "实施例缺字段" not in out_b)
expect("文本 B 无装置独权缺连接关系", "未写出连接关系或位置关系" not in out_b)

print()
if failures:
    print(f"❌ {len(failures)} 项未通过：{failures}")
    sys.exit(1)
print("✅ 全部通过")

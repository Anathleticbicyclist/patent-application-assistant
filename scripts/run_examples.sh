#!/usr/bin/env bash
# 用 examples/battery-case 跑通全部脚本，验证可执行层没坏。
set -e
cd "$(dirname "$0")/.."
OUT=${1:-/tmp/patent-examples}
mkdir -p "$OUT"

echo "== 1/5 查新检索计划 =="
python3 scripts/prior_art_search.py --topic "电池热失控预警" \
  --keywords "热失控,热失控预警,thermal runaway,thermal propagation" \
  --ipc H01M10,G01R31 --country CN --year-from 2015 --out "$OUT/search" | head -6

echo "== 2/5 说明书附图 =="
python3 scripts/figure_gen.py --spec examples/battery-case/fig.json --out "$OUT/fig2.png"

echo "== 3/5 权利要求形式检查 =="
python3 scripts/claim_check.py examples/battery-case/application.md || true

echo "== 4/5 侵权比对表 =="
python3 scripts/claim_chart.py --claims examples/battery-case/application.md \
  --map examples/battery-case/claim-map.json --out "$OUT/chart.md" | tail -4

echo "== 5/5 交付物机检 =="
python3 scripts/check_deliverable.py examples/battery-case/application.md || true

echo
echo "全部脚本执行完成，产物在 $OUT"

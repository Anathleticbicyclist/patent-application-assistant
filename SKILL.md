---
name: patent-application-assistant
display_name: "专利申请助手"
description: 面向中国发明专利/实用新型/外观设计的全流程专利实务助手，把「技术交底书撰写、专利保护点挖掘、查新检索、权利要求与说明书起草、侵权比对与规避设计、改进/审查意见」串成一条可执行流水线。当用户需要写技术交底书、梳理发明点、做查新/现有技术检索、评估新颖性创造性、起草或改写权利要求书与说明书、做 FTO 或侵权比对、给规避设计方案、做专利申请前质检或审查意见答复时使用；也覆盖申请前的合规判断：职务发明与权属归属、是否已公开及新颖性宽限期、向外国申请前的保密审查、单一性与分案、以及软件/算法、机械结构、电子通信、医药生物、化学材料等不同行业的客体适格性与撰写差异。（用户说「帮我写交底书」「这个功能能不能申请专利」「帮我查新」「有没有侵权风险」「怎么规避这个专利」「权利要求怎么写」「这是职务发明吗」「已经上线了还能申请吗」「要去美国申请要办什么」「技术方案发给外部 API 安全吗」等都属于本技能范围。）
---

# 专利申请助手

把分散的专利开源工具与大模型能力，组织成一条从「一段技术描述」到「可交付申请文件」的标准流水线。核心不是生成漂亮文字，而是**每一步都有判据、有证据、有质检门槛**。

## 三条底线（任何阶段都不得突破）

1. **不编造证据**：检索到的对比文件必须来自真实检索结果，专利号、公开号、申请人、日期逐项可核。没有检索到就写「未检索到高度相关文献」，并说明检索范围与局限，绝不虚构对比文件。
2. **不虚构法理**：涉及法条只引用确实存在于《专利法》《专利法实施细则》《专利审查指南》中的表述；不确定就写「需代理师确认」，不要自造条款号。
3. **区分事实与判断**：检索结果=事实；新颖性/创造性/侵权=**初步判断**。所有结论必须带一句「本结论为技术层面初判，不构成法律意见，最终以代理师/律师意见为准」。
4. **不做非正常申请**：不伪造实验数据与实施例、不拼凑无研发支撑的方案、不为规避审查而拆分改写（专利法第 20 条诚信原则）。用户要求「编点数据显得效果好」时必须拒绝并说明后果；可直接照用的拒绝口径见 `references/compliance-gate.md` 第六节。

另外两条实务纪律：

- **公开换保护**：交底书允许写「商业秘密保留」的部分，但必须显式标注；不要把不该公开的核心参数写进去。
- **术语单一化**：同一部件/步骤全文只用一个名称，交底书、权利要求、说明书三处必须一致（这是形式审查和后续无效程序的高频雷区）。

## 主流水线（按需进入，不必每次跑全）

| 阶段 | 目标 | 关键动作 | 详细指引 |
|---|---|---|---|
| P0 意图路由 | 判断用户要哪几段 | 从一句话里抽出：技术对象、交付物类型、是否已公开、目标（申请/防守/规避） | 本页「输入分流」 |
| **P0.5 合规闸门** | **先决条件：谁能申请、能不能公开、能不能出国、数据能不能外发** | 五项必问：权属、公开状态与宽限期、保密审查、数据出境、单一性/分案；出「闸门卡」 | `references/compliance-gate.md` |
| P1 技术结构化 | 把口语变成可专利的技术方案 | 问题—方案—效果三段式；画「要素树 FEAT」；列出替代路径；**按行业确认客体适格性** | `references/workflow.md`、`references/subject-matter.md` |
| P2 保护点挖掘 | 决定「申请几个、每个保护什么」 | 六个挖掘视角 + 权项类别规划 + 核心/支撑分层 | `references/workflow.md` |
| P3 查新检索 | 回答「有没有人做过」 | 构造中英文检索式 + IPC/CPC + 语义检索；出对比文件表 | `references/search-queries.md` |
| P4 可专利性初判 | 新颖性 / 创造性 / 实用性 | 三步法：最接近现有技术→区别特征→技术效果→是否显而易见 | `references/workflow.md` |
| P5 交底书撰写 | 给代理师一份能直接用的输入 | 12 节结构 + ≥3 个实施例 + 术语表 + 附图清单 | `references/disclosure-template.md`、`assets/disclosure-template.md` |
| P6 权利要求与说明书 | 定保护范围 | 独权最小必要特征集、从权梯度、多类别权项、说明书四段式 | `references/claims-drafting.md` |
| P7 规避设计 / FTO | 回答「我会不会侵权、怎么绕」 | 逐权项要素比对表 → 删减/替代/参数/架构/用途五类规避 | `references/design-around.md` |
| P8 质检与改进意见 | 提交前把雷排掉 | 66 项清单（40 基础 + 26 专项）+ 自动校验脚本 | `references/review-checklist.md`、`scripts/check_deliverable.py` |

## 输入分流

- **只有一句想法/一段需求** → P1 起跑，P5 收口（先产交底书，不急着写权项）。
- **已有交底书/文档/代码** → P1 直接做结构化抽取，跳到 P3 查新 + P6 起草。
- **只想确认能不能申请** → P3 + P4，出一页《可专利性初判》。
- **已有他人专利号，怕侵权** → P7（侵权比对 + 规避），必要时回 P3 找无效证据。
- **已收到审查意见** → P8，逐条对 OA 拆解 + 答复要点。
- **问「能不能申请 / 已经公开了怎么办 / 要不要去国外申请 / 这是谁的」** → 先走 P0.5 合规闸门，别直接开始写。

不确定时先问三个问题：**技术对象是什么（方法/装置/系统/介质/外观）？是否已经公开（发表、演示、上线、销售）？这次要的是申请文件、查新结论，还是规避方案？** 只问这三项，不要一次抛十个问题。

## 可执行层（本技能自带脚本，不需要额外装项目）

先看 `scripts/` 再考虑外部工具——下面这些是**离线可跑、结果确定**的：

| 子命令 | 作用 | 什么时候用 |
|---|---|---|
| `patent_cli.py pipeline` | **一条命令跑完机检→查新→权项→附图→比对→汇总，自动产出报告** | **默认入口：拿到交底书/申请文件先跑它** |
| `patent_cli.py gate` | **P0.5 合规闸门**：逐项问权属/公开/保密审查/数据出境/单一性，出「闸门卡」并按规则标风险 | **开工第一步；任一项未填就拦在撰写之前** |
| `patent_cli.py search` | 生成三档检索式 + 五库直链 + 记录表 | 每单查新开工第一步，先出检索计划再去浏览器执行 |
| `patent_cli.py figure <spec.json>` | 生成国知局格式黑白附图（纯黑白二值、只含标记、300DPI） | 交底书/说明书需要附图，且没有 STEP 模型时 |
| `patent_cli.py claims <文件>` | 权项细检：多项引多项、引用基础（含该/上述/前述）、引用方向、从权主题一致性、「其特征在于」位置、说明书支持度、摘要字数与摘要附图 | 每次写完/改完权利要求 |
| `patent_cli.py chart --claims --map` | 生成侵权比对表，按全覆盖原则自动出「落入/不落入」结论 | FTO 与规避设计 |
| `patent_cli.py check <文件>` | 交付物机检（章节、编号、摘要、占位符、免责声明） | 交付前最后一步 |
| `patent_cli.py mcp --target claude` | 生成三个高频专利 MCP 的接入配置（不写密钥明文） | 需要在线检索 USPTO/EPO/六大局时 |

统一入口：`python3 scripts/patent_cli.py --help`。端到端自检：`bash scripts/run_examples.sh`。

**没有凭据时怎么办**：`search` 默认 `--provider auto`，无凭据时静默降级为检索计划模式（只出检索式与链接，命中栏留空待回填），有凭据则自动调 PQAI/EPO/USPTO；`mcp` 只生成 `${ENV}` 占位并标注每个服务「可用/待配置」。这是刻意设计——宁可少给结论，也不给假数据。

**用 pipeline 的纪律**：它的报告只覆盖形式项，`00-运行报告.md` 里的「还需要人做的」必须逐条处理完，才能进入实质审查（`references/review-checklist.md`）。

## 开源工具编排（本技能不内置代码，按步骤调用现成项目）

完整映射见 `references/open-source-map.md`（精选，去重后 44 个最常用），**全量 187 个的逐项索引**见 `references/open-source-index.md`；全部致谢见 `README.md`。常用组合：

- **查新检索**：`patsnap/patent-literature-search-mcp`（六大局覆盖）、`riemannzeta/patent_mcp_server`（USPTO 最全）、`pqaidevteam/pqai`（语义现有技术检索）、`KunihiroS/google-patents-mcp`。中文场景优先 CNIPA 官方检索 + Google Patents 中文库交叉验证。
- **交底书/申请文件生成**：`handsomestWei/patent-disclosure-skill`（结构与话术参考）、`wanshuiyin/Auto-claude-code-research-in-sleep` 的 `patent-pipeline`（阶段化推进范例）、`QiYao-Wang/AutoPatent`（多 Agent 撰写框架）。
- **CNIPA 形式合规**：`handsomeZR-netizen/cn-patent-drafter`（规范同步）、`PisenAILab/china-patent-figure-skill`（说明书附图）、`CNIPA-AI/patent-xml-generator`（报送 XML）。
- **侵权/规避**：`yuc16/PatentRadar`、`mjtiv/patent-claim-mapper`、`Sean-yh/claim-chart`、`dungnotnull/freedom-to-operate-analysis-agent-skill`。
- **数据底座**：`ip-tools/python-epo-ops-client`、`ip-tools/uspto-opendata-python`、`google/patents-public-data`、`Patent2net/P2N-v3`。

调用外部工具时遵守其 API 条款与速率限制；没有凭据就走公开网页检索，不要声称拿到了未获取的数据。

## 交付物（按需求给，不要每次都出全套）

1. **《技术交底书》**（Markdown 或 docx）：12 节齐全，含实施例、术语表、附图清单、公开风险提示。
2. **《查新报告》**：检索式与检索范围、对比文件表（公开号/申请人/日期/相关段落）、逐篇相关性打分、结论。
3. **《权利要求书 + 说明书》**：独权 1 项起、从权成梯度、类别覆盖；说明书背景/发明内容/附图说明/具体实施方式完整。
4. **《FTO / 侵权比对表》**：权项要素 × 被控方案 的逐格比对，附规避建议分级。
5. **《申请前质检报告》**：清单项 + 不合格项 + 修改建议。

## 收口自检（交付前必须做）

1. 运行 `python3 scripts/patent_cli.py check <交付文件>`（申请文件另加 `claims` 细检），对结构、权项编号、术语、实施例数量做机检。
2. 人工过一遍 `references/review-checklist.md` 的必查项（尤其：独权是否含非必要技术特征、从权是否全部有引用基础、说明书是否支持每个权项）。
3. 结尾附免责声明，并列出「仍需人工确认」的开放问题。

## 参考文件导航

- `references/workflow.md` — P1–P4 的详细步骤、判据与结构化方法（要素树、六视角挖掘、三步法）
- `references/search-queries.md` — 数据源、检索式构造、分类号、检索记录表
- `references/disclosure-template.md` — 交底书 12 节逐一写法与退回原因
- `references/claims-drafting.md` — 权利要求与说明书起草规则、正反例
- `references/design-around.md` — 侵权比对表与五类规避路径、风险分级
- `references/review-checklist.md` — 66 项质检清单（A–H 8 类 40 项基础 + I–L 4 类 26 项专项）、审查意见答复思路
- `references/compliance-gate.md` — **P0.5 合规闸门**：权属、公开宽限期、保密审查、数据出境、单一性/分案、时限
- `references/subject-matter.md` — **分领域撰写**：软件算法、商业方法/UI、机械结构、电子通信、医药生物、化学材料
- `references/open-source-map.md` — 开源项目 ↔ 流程步骤映射（精选，去重后最常用的 44 个；已接成脚本的在表内标 ✅）
- `scripts/` — 可执行层（pipeline 全流程、检索计划、附图、权项检查、比对表、MCP 配置、交付物机检）
- `references/open-source-index.md` — **全量索引**（187 个，逐项标注可用阶段，选型/反查用）
- `assets/disclosure-template.md` — 可直接填写的交底书空模板
- `examples/battery-case/`、`examples/algorithm-case/` — 合格稿 + 缺陷稿成对样例（`tests/` 的回归基线由此驱动；先看合格稿知道该写成什么样，再看缺陷稿知道机检会抓什么）

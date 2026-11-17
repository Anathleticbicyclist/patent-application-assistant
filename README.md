# 专利申请助手（Patent Application Assistant）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/type-AI%20Agent%20Skill-blue)](SKILL.md)
[![Scripts](https://img.shields.io/badge/scripts-6%20runnable-success)](scripts/)

一个把「专利交底书撰写、保护点挖掘、查新检索、权利要求与说明书起草、侵权比对与规避设计、申请前质检」串成一条流水线的 **AI Agent Skill**。

两件事它都做：

1. **编排**——把 187 个开源专利项目的能力，编进一套**有判据、有证据、有质检门槛**的实务流程，每一步告诉你调哪个工具、产出什么、怎么判断合格；
2. **可执行**——高频的六件事（检索计划、黑白附图、权项细检、侵权比对、交付物机检、MCP 接入）已经写成本仓库自带的 Python 脚本，离线可跑、结果确定，不依赖任何外部项目安装。

> 本仓库只做编排与本地实现，**不内嵌**被致谢项目的代码（避免 GPL/AGPL 传染，也避免把上下文撑爆）；需要时按 `references/open-source-index.md` 指的位置现装现用。

> 适用于中国发明专利 / 实用新型 / 外观设计的申请准备；也可用于 FTO 初筛与规避设计讨论。
> 输出的所有结论均为**技术层面初判**，不构成法律意见。

---

## 它解决什么问题

工程师写交底书常犯的错，不是不会写，而是：

- 只写需求，不写方案（代理师看完还得追问三轮）
- 三个实施例只换了阈值，实质是一个方案
- 有益效果和特征没有因果关系，写「提升用户体验」
- 权项里塞满非必要特征，把保护范围白送出去
- 查新只查关键词，漏掉非专利文献和英文表达
- 看到别人的专利就慌，不看法律状态、不做逐特征比对

这个 Skill 把这些坑做成**结构化的检查项**，并在每一步给出可交付的文件形态。

---

## 流水线

```
P0 意图路由 ──┬─ 只有想法 ──────→ P1 结构化 → P5 交底书
              ├─ 已有交底书 ────→ P1 → P3 查新 → P6 权项+说明书
              ├─ 只想确认能不能申 → P3 → P4 可专利性初判
              ├─ 怕侵权 ────────→ P7 比对 + 规避
              └─ 收到审查意见 ──→ P8 质检 + 答复要点
```

| 阶段 | 产出 | 核心方法 |
|---|---|---|
| P1 技术结构化 | FEAT 要素树 + 问题/方案/效果三段式 | 特征拆到「必要性 / 替代方案」可判 |
| P2 保护点挖掘 | 保护点清单表 | 流程·部件·边界·数据·交互·延展 六视角 |
| P3 查新检索 | 检索记录表 + 对比文件表 | 四步检索式构造 + 分类号 + 相关性 A/B/C/D 分级 |
| P4 可专利性 | 一页纸初判 | 新颖性单篇比对 + 创造性三步法 |
| P5 交底书 | 12 节完整文档 | ≥3 个实质不同的实施例 |
| P6 权项与说明书 | 独权 + 从权梯度 + 四段式说明书 | 最小必要特征集，独权不写效果 |
| P7 侵权/规避 | 逐特征比对表 + 五类规避方案 | 全覆盖原则（All Elements Rule） |
| P8 质检 | 8 类 40 项清单 + 机检报告 | 形式项机检，实质项人工 |

---

## 目录结构

```
patent-application-assistant/
├── SKILL.md                        # 主流程与纪律（Agent 入口）
├── README.md                       # 本文件
├── agents/
│   ├── doubao.yaml                 # 豆包技能面板元数据
│   └── openai.yaml                 # 同构配置（兼容）
├── references/
│   ├── workflow.md                 # P1–P4 详细方法（要素树 / 六视角 / 三步法）
│   ├── search-queries.md           # 数据源、检索式、IPC/CPC、记录表
│   ├── disclosure-template.md      # 交底书 12 节写法与退回原因
│   ├── claims-drafting.md          # 权项与说明书规则 + 正反例
│   ├── design-around.md            # FTO 比对与五类规避路径
│   ├── review-checklist.md         # 8 类 40 项质检 + OA 应对
│   ├── open-source-map.md          # 开源项目 ↔ 流程步骤映射（精选 49 个）
│   └── open-source-index.md        # 全量索引（186 个，逐项标注可用阶段）
├── assets/
│   └── disclosure-template.md      # 可直接填写的交底书空模板
├── scripts/
│   ├── patent_cli.py               # 统一入口（pipeline/search/figure/claims/chart/check/mcp）
│   ├── pipeline.py                 # 全流程编排：一条命令跑完并出报告
│   ├── prior_art_search.py         # 三档检索式 + 五库直链 + 检索记录表
│   ├── figure_gen.py               # 国知局格式黑白附图（纯二值、只含标记、300DPI）
│   ├── claim_check.py              # 权项细检：多项引多项/引用基础/引用方向/禁用语
│   ├── claim_chart.py              # 侵权比对表（全覆盖原则自动出结论）
│   ├── check_deliverable.py        # 交付物机检（章节/编号/摘要/占位符）
│   ├── mcp_setup.py                # 高频专利 MCP 配置生成（不写密钥明文）
│   └── run_examples.sh             # 端到端自检
├── examples/
│   └── battery-case/               # 电池热失控预警的完整示例（申请文件+比对映射+附图规格）
└── requirements.txt
```

---

## 如何调用这个 Skill

它是一个**纯 Markdown + Python 脚本目录**，没有服务、没有 API Key 也能用。放进任何支持 Skill 的 Agent 的技能目录即可。

### 1. 装到技能目录

```bash
git clone https://github.com/Anathleticbicyclist/patent-application-assistant.git

# Claude Code
mkdir -p ~/.claude/skills && cp -r patent-application-assistant ~/.claude/skills/

# 豆包 / 通用 Agent
cp -r patent-application-assistant ~/.doubao/agent_mode/workspace/.user_skills/

# Codex / Cursor 等支持 skill 目录的工具：放进其 skills 目录，或直接把本目录挂进上下文
```

关键约束：目录名必须是 `patent-application-assistant`，与 `SKILL.md` 里 frontmatter 的 `name` 一致，否则不会被识别。

### 2. 触发方式

**隐式触发**（推荐）——直接说人话，Agent 读 `description` 自行匹配：

| 你想做的事 | 这样说 |
|---|---|
| 交底书 | 「把这个电池预警方案整理成专利交底书」 |
| 查新 | 「帮我查一下这个交互方案有没有人做过」 |
| 保护点挖掘 | 「这个方案能拆成几个权利要求？哪些是必守的」 |
| 规避 | 「竞品专利 CN112345678A，我们会不会侵权，怎么绕」 |
| 权项打磨 | 「权利要求帮我看看，有没有多余的必要技术特征」 |
| 改进意见 | 「审查员大概率会拿哪篇来驳我，怎么补」 |

**显式调用**——点名技能，适合需要确定性时：

```
使用 $patent-application-assistant 帮我把这份技术方案写成交底书
```

### 3. 直接调脚本（不经过 Agent）

```bash
pip install -r requirements.txt
python3 scripts/patent_cli.py --help
bash scripts/run_examples.sh          # 端到端自检，先确认环境是通的
```

### 4. 典型工作流

```
交底书 → §3 查新(patent_cli.py search) → §4 保护点挖掘 → §5 权项(patent_cli.py claims)
      → 客户反馈 → 规避比对(patent_cli.py chart) → 申请文件(patent_cli.py check) → 交付
```

每一棒的输入输出格式都写在 `references/workflow.md`；每步要做完才能进下一步，别跳。

---

## 可执行层（真正能跑的部分）

不是「告诉你该去用哪个工具」，而是自带脚本、离线可跑、结果确定：

```bash
python3 scripts/patent_cli.py --help

# 0. 全流程一条命令（推荐）
python3 scripts/patent_cli.py pipeline --doc 交底书.md \
  --ipc H01M10,G01R31 --fig fig.json --map map.json --out ./run1
# 自动产出：00-运行报告.md + search/ + claims.json + figure.png + claim-chart.md
# 中途某步失败不中断，最后统一告诉你「还差什么」；有硬伤时退出码为 1

# 1. 查新：先出检索计划（三档检索式 + CNIPA/Google/Espacenet/PATENTSCOPE/USPTO 直链）
python3 scripts/patent_cli.py search --topic "电池热失控预警" \
  --keywords "热失控,thermal runaway,false alarm" --ipc H01M10,G01R31 \
  --country CN --year-from 2015 --out ./search

# 2. 附图：结构化步骤 → 合规黑白线稿（纯黑白二值、图内只有编号、300 DPI）
python3 scripts/patent_cli.py figure --spec fig.json --out fig2.png

# 3. 权项细检：多项引多项 / 引用基础 / 引用方向 / 独权特征数 / 禁用语
python3 scripts/patent_cli.py claims 申请文件.md

# 4. 侵权比对：逐要素判定 → 按「全覆盖原则」自动出落入/不落入
python3 scripts/patent_cli.py chart --claims 申请文件.md --map map.json --out chart.md

# 5. 交付物机检
python3 scripts/patent_cli.py check 交底书.md

# 6. 把高频专利 MCP 接进 Agent（生成配置，密钥用 ${ENV} 占位）
python3 scripts/patent_cli.py mcp --target claude
```

端到端自检：

```bash
bash scripts/run_examples.sh      # 用 examples/battery-case 跑通全部脚本
```

**没有 API 凭据时的行为（自动降级，不用你先报错再改配置）**：

| 场景 | 脚本行为 |
|---|---|
| 无任何检索凭据 | `search` 默认 `--provider auto`，静默降级为「检索计划模式」：出检索式 + 直链，命中栏留空 |
| 有凭据 | `auto` 按 PQAI → EPO → USPTO 顺序挑第一个可用的，自动调真实接口 |
| `mcp` 无 key | 输出 `${ENV}` 占位 + 逐项标注「✅ 可用 / ⚠️ 待配置（缺哪个变量）」，不写入明文 |
| 文档里没有权项 | `pipeline` 自动跳过权项与比对步，不报错 |

刻意如此——宁可少给结论，也不给假数据。

## 交付物机检

```bash
python3 scripts/check_deliverable.py 交底书.md
python3 scripts/check_deliverable.py 申请文件.md --type application
```

自动检查：章节齐全度、权项编号连续性、多项引多项、引用基础、实施例数量、摘要字数、疑似引用与占位符、免责声明。
输出 PASS/WARN/FAIL 清单与评分。**机检通过 ≠ 合格**，实质项仍需人工过 `review-checklist.md`。

---

## 三条底线

1. **不编造证据** —— 专利号、对比文件、段落原文必须可核；没有就写「未检索到」并说明检索局限。
2. **不虚构法理** —— 只引用真实存在的法条，不确定就标「需代理师确认」。
3. **区分事实与判断** —— 检索结果是事实，新颖性/侵权是初判，必须附免责声明。

---

## 免责声明

本项目提供的是**技术文档整理与检索方法论**，不是法律意见。专利申请文件的最终定稿、侵权认定、无效宣告、许可谈判，均须由具备资质的专利代理师或律师完成。使用者应自行核验所有检索结果与专利法律状态。

---

# 致谢
本 Skill 的每一个环节，都建立在下面这些开源作者的工作之上。这份清单按用途分类，**逐项列出**——没有它们，这个流程只是空架子。

> 两级索引：本节回答「感谢了谁」；每个项目**能用在哪一步**，见 [`references/open-source-index.md`](references/open-source-index.md) 的 187 项全量对照表。

感谢方式说明：本仓库**不复制、不内嵌**这些项目的代码，只在流程里引用它们的方法与接口；每个项目的许可证、作者与仓库地址均以其原始仓库为准，使用时请遵守各自的许可条款。

特别感谢把「专利」这个高度封闭的领域开源出来的团队：PQAI 把语义检索做成了可自托管的服务栈，EPO/USPTO 的客户端让数据不再是黑箱，以及近两年涌现的一批中文 Agent Skill 作者，把交底书这类「师傅带徒弟」的经验写成了可复用的提示词与检查表。

### 一、总览型清单（先看这些）

1. **[mahesh-maan/awesome-patent-retrieval](https://github.com/mahesh-maan/awesome-patent-retrieval)** · ⭐ 104 — 专利数据处理与检索的资源合集，做选型的第一站
2. **[QiYao-Wang/Awesome-LLM4Patents](https://github.com/QiYao-Wang/Awesome-LLM4Patents)** · ⭐ 39 — 大模型 + 专利的论文/代码汇总（撰写、分类、检索、审查）
3. **[CNIPA/PatentDatabases](https://github.com/CNIPA/PatentDatabases)** · ⭐ 458 — 全球各专利局官方数据库入口汇总（含 CNIPA/USPTO/EPO/JPO/KIPO/WIPO）
4. **[google/patents-public-data](https://github.com/google/patents-public-data)** · ⭐ 694 — Google Patents 公共数据集（BigQuery）分析示例，做批量分析的地基
5. **[projectpq.ai（PQAI 组织）](https://projectpq.ai/)** — 开源专利检索 AI 生态，含检索引擎、编码器、重排、分类等一整套服务

### 二、专利撰写 / 交底书生成（AI Agent & Skill 类，中文为主）

6. **[handsomestWei/patent-disclosure-skill](https://github.com/handsomestWei/patent-disclosure-skill)** · ⭐ 13.5k — 国内最火的「中国专利.skill」：专利点挖掘 + 发明/实用/外观交底书编写 + 政策嗅探 + 审查答复辅助
7. **[7toCR/paper2patent](https://github.com/7toCR/paper2patent)** · ⭐ 739 — 论文转专利模板库，Flash/Pro Prompt + 专利附图生成 + Agent Skills，产出中国发明申请文本
8. **[ninehills/PatentWriterAgent](https://github.com/ninehills/PatentWriterAgent)** · ⭐ 581 — PatentWriterAgent 演示：端到端专利撰写 Agent
9. **[fuyuxiang/patent-disclosure-skill](https://github.com/fuyuxiang/patent-disclosure-skill)** · ⭐ 87 — 技术想法/文档/代码 → 专业技术交底书，含自适应信息采集、专利语言规范化、附图、Word 导出
10. **[PisenAILab/china-patent-figure-skill](https://github.com/PisenAILab/china-patent-figure-skill)** · ⭐ 97 — 中国专利附图专用：3D 装配体（STEP）→ 符合国知局形式要求的说明书附图，自动标号引线 + 13 项质检
11. **[handsomeZR-netizen/cn-patent-drafter](https://github.com/handsomeZR-netizen/cn-patent-drafter)** · ⭐ 65 — 对齐 CNIPA 2026 规范的中国发明专利 Claude Code Skill，一句话起草
12. **[lzlfwow/PatentClaw](https://github.com/lzlfwow/PatentClaw)** · ⭐ 58 — 论文 → 中国专利交底书的证据驱动多 Agent 生成，固定检查表审查 + 可追溯多轮改稿
13. **[abelxiaoxing/PatentAgent](https://github.com/abelxiaoxing/PatentAgent)** · ⭐ 46 — 专利构建助手
14. **[xiuneng0-collab/-skill--](https://github.com/xiuneng0-collab/-skill--)** · ⭐ 42 — 实用性发明专利 Skill
15. **[learnljs/paper-to-cn-patent](https://github.com/learnljs/paper-to-cn-patent)** · ⭐ 30 — 论文+附图+备注 → 中文发明申请草稿，遵循「先权利要求、后说明书」流程，强制人工复核
16. **[cycloneha/cn-patent-disclosure-writing-skill](https://github.com/cycloneha/cn-patent-disclosure-writing-skill)** · ⭐ 29 — 专利交底书撰写技巧 Skill
17. **[softctwo/patent-agents](https://github.com/softctwo/patent-agents)** · ⭐ 28 — 发明/实用/外观撰写 + 附图绘制 Agent（Gemini 2.0 Flash）
18. **[SALFM/cn-patent-first-draft](https://github.com/SALFM/cn-patent-first-draft)** · ⭐ 23 — 中文发明/实用新型初稿生成，含待确认事项、术语统一表、权利要求书、说明书、摘要
19. **[yizchu/patent-compose-skill](https://github.com/yizchu/patent-compose-skill)** · ⭐ 20 — 项目分析→市场分析→查新→专利组合→保护优化→交底书与附图→权利要求与完整申请文件
20. **[AqooDer/patent-mining-disclosure-skill](https://github.com/AqooDer/patent-mining-disclosure-skill)** · ⭐ 19 — 专利挖掘与交底书：专利点清单、相似专利查新、商业秘密取舍、流程图/架构图、Word/PDF 导出
21. **[Mrliubai/patent-assistant-skill-2026](https://github.com/Mrliubai/patent-assistant-skill-2026)** · ⭐ 15 — 查新→可专利性→申请文件→审查预测→答复，6 阶段全流程
22. **[TaohongMaxwell/PatentDigest](https://github.com/TaohongMaxwell/PatentDigest)** · ⭐ 13 — 专利文档智能解析 Skill
23. **[ProgrammerAnthony/PatentSkills](https://github.com/ProgrammerAnthony/PatentSkills)** · ⭐ 12 — 专利自动化创作工作流：创意、写作、评审
24. **[fnjialun/cnipa-patent-writer](https://github.com/fnjialun/cnipa-patent-writer)** · ⭐ 10 — 只借模板版式、内容自生成的中国发明专利撰写 Skill
25. **[MrEgg2021/patent-skills](https://github.com/MrEgg2021/patent-skills)** · ⭐ 10 — 6 个公开技能：Google Patents 检索、全球审查档案下载、发明点提取、权利要求拆解、交底书审核、形式审查
26. **[illusionaireal/oh-my-patent](https://github.com/illusionaireal/oh-my-patent)** · ⭐ 118 — 面向 AI 编码 Agent 的专利插件，技术想法 → 交底书（Claude Code / Codex / OpenCode）
27. **[Obviously-Not/patent-skills](https://github.com/Obviously-Not/patent-skills)** · ⭐ 19 — 从代码库发现可专利技术特征 + 战略布局的 Agent Skills
28. **[StellaQIU27/claude-skill-patent-writing-chinese](https://github.com/StellaQIU27/claude-skill-patent-writing-chinese)** · ⭐ 8 — 中文专利说明书生成，OMML 公式、仿宋字体等排版
29. **[Sphinxxx233/patent-disclosure-codex](https://github.com/Sphinxxx233/patent-disclosure-codex)** · ⭐ 8 — 面向 Codex 的中国专利挖掘/查新/交底书 Skill
30. **[wfukatsu/patent-draft](https://github.com/wfukatsu/patent-draft)** — 从设计文档找专利点并起草 JP/US/CN/KR/EP/PCT 申请（含附图）
31. **[mhurhangee/patrick](https://github.com/mhurhangee/patrick)** · ⭐ 24 — 代理师向：在自有 Word 文件里起草与红线修订的专利审查助手
32. **[PetePupalaikis/uspatent](https://github.com/PetePupalaikis/uspatent)** · ⭐ 7 — 用 LaTeX / LyX 起草美国专利申请的工具链
33. **[deftio/provisional-patent-template](https://github.com/deftio/provisional-patent-template)** · ⭐ 65 — 免费美国临时申请模板（已被大量授权专利/WIPO 申请使用）
34. **[allthemusicllc/atp-tools](https://github.com/allthemusicllc/atp-tools)** — AllThePatents：GPT2 级模型微调做「标题+摘要→权利要求」与反向生成
35. **[antiboredom/patent-generator](https://github.com/antiboredom/patent-generator)** · ⭐ 376 — 文学/哲学文本 → 专利申请书的生成器（概念实验）
36. **[nikmcfly/vibepatent](https://github.com/nikmcfly/vibepatent)** · ⭐ 12 — AI 专利申请生成器
37. **[Eriemon/patent-generator](https://github.com/Eriemon/patent-generator)** · ⭐ 3 — 中文专利生成
38. **[CNIPA-AI/patent-xml-generator](https://github.com/CNIPA-AI/patent-xml-generator)** · ⭐ 2 — 申请内容 → 符合 CNIPA DTD 标准的 XML（报送环节用）
39. **[LeonardHope/Claude-Skill-for-Patent-Filing-Quality-Control](https://github.com/LeonardHope/Claude-Skill-for-Patent-Filing-Quality-Control)** · ⭐ 12 — 申请文件质量管控 Skill
40. **[orionoxe/patent-agent-skills](https://github.com/orionoxe/patent-agent-skills)** · ⭐ 1 — 专利翻译质检 + 审查意见答复起草，可审计
41. **[sinonchum/PatentFlow](https://github.com/sinonchum/PatentFlow)** · ⭐ 4 — 面向欧洲代理师：EPO Office Action 解析 + 答复草稿（隐私优先 RAG）
42. **[talenlin/oa-response-drafter](https://github.com/talenlin/oa-response-drafter)** — 基于 NotebookLM 的 OA 答复起草助手
43. **[kgtceo/office-action](https://github.com/kgtceo/office-action)** — 确定性解析器判定被驳回的具体限定，再起草答复
44. **[Abhishek2005-Siva/patent-office-action-ai](https://github.com/Abhishek2005-Siva/patent-office-action-ai)** — OA 驳回打分 0-100 并起草 37 CFR 1.111 答复
45. **[MarkBerkovics/Response_to_OA_GUI](https://github.com/MarkBerkovics/Response_to_OA_GUI)** — 模拟专利律师答复 OA 的 AI Agent
46. **[Mohan-Selvan/patent_editor_ai](https://github.com/Mohan-Selvan/patent_editor_ai)** — 撰写副驾：找弱权利要求、改写建议、OA 风险打分
47. **[wukun2005-gif/patentExaminator](https://github.com/wukun2005-gif/patentExaminator)** · ⭐ 10 — AI 辅助实审：检索对比文件 + 撰写审查意见
48. **[shivram101/PinPoint](https://github.com/shivram101/PinPoint)** — 核查审查员引用是否与对比文件真正对应
49. **[AIforIP/PatRe](https://github.com/AIforIP/PatRe)** · ⭐ 5 — 审查意见与反驳生成的全流程基准（含 PatEx-Gym）
50. **[AIforIP/PatEx-Gym](https://github.com/AIforIP/PatEx-Gym)** · ⭐ 12 — Agentic 现有技术检索用于新颖性评估

### 三、专利撰写（学术框架 / 模型 / 基准）

51. **[QiYao-Wang/AutoPatent](https://github.com/QiYao-Wang/AutoPatent)** · ⭐ 219 — 多 Agent 自动专利生成（planner + 6 writer + examiner，PGTree/RRAG），JCIP 2026
52. **[yycyyv/M-Cube](https://github.com/yycyyv/M-Cube)** · ⭐ 203 — M³：多思考、多模态、多校验的专利撰写助手
53. **[RobThePCGuy/Claude-Patent-Creator](https://github.com/RobThePCGuy/Claude-Patent-Creator)** · ⭐ 211 — USPTO 专利创作系统：MCP + Claude Code 插件，MPEP/USC/CFR 混合 RAG + 7600 万专利
54. **[vl2g/PatentLMM](https://github.com/vl2g/PatentLMM)** · ⭐ 27 — AAAI 2025：多模态专利生成/撰写模型
55. **[IPBench/IPBench](https://github.com/IPBench/IPBench)** · ⭐ 25 — ACL 2026：知识产权领域 LLM 评测基准
56. **[AI4Patents/IMPACT](https://github.com/AI4Patents/IMPACT)** · ⭐ 18 — NeurIPS 2024：外观设计专利的多模态分析与创作数据集
57. **[shuxiachai/academic-commercialization-agent](https://github.com/shuxiachai/academic-commercialization-agent)** · ⭐ 813 — 论文 → TRL、专利态势、技术转移评估的多 Agent 工具
58. **[wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)** · ⭐ 19k — 含 `patent-pipeline` 技能：发明结构化 → 权利要求起草 → 说明书 → 审查官复审的流水线
59. **[FradSer/dotclaude](https://github.com/FradSer/dotclaude)** — 内含 `patent-architect` 技能：SerpAPI 查新 + 生成中国专利申请表
60. **[PatentTRIZbasedAI20260226110030/Patent-GPT](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT)** · ⭐ 5 — TRIZ + LLM 的发明副驾，生成专利创意并做相似性验证

### 四、专利检索 / 查新 / 语义检索（含 MCP 服务）

61. **[pqaidevteam/pqai](https://github.com/pqaidevteam/pqai)** · ⭐ 139 — PQAI 检索服务器：稠密神经检索做语义现有技术检索（生态还有 pqai-db / pqai-index / pqai-encoder / pqai-reranker / pqai-snippet / pqai-classifier / pqai-gateway）
62. **[ip-tools/patzilla](https://github.com/ip-tools/patzilla)** · ⭐ 126 — 模块化专利信息研究平台与数据集成工具箱（多数据源统一接入 + Web UI）
63. **[r14dd/patent](https://github.com/r14dd/patent)** · ⭐ 567 — 面向「代码/工具想法」的现有技术检索：这个 dev tool 是否已被做过
64. **[helmersl/patent_similarity_search](https://github.com/helmersl/patent_similarity_search)** · ⭐ 51 — 专利相似检索
65. **[us/patent-similarity-rag](https://github.com/us/patent-similarity-rag)** · ⭐ 48 — 基于 Google Patents 的 RAG 相似检索 + ChatGPT
66. **[hissain/llm_patent_search](https://github.com/hissain/llm_patent_search)** · ⭐ 4 — LLM 驱动的专利相似检索精简方案
67. **[KonstantinosPetrakis/PatentInspector](https://github.com/KonstantinosPetrakis/PatentInspector)** · ⭐ 24 — 开源专利分析 Web 应用，重可用性与 UX
68. **[keyang3/PatentSearch](https://github.com/keyang3/PatentSearch)** · ⭐ 6 — 加 BERT embedding 的专利文献检索
69. **[WladGrm/Patent-Search](https://github.com/WladGrm/Patent-Search)** · ⭐ 6 — T5/BERT 类模型的专利检索引擎（Flask Web App）
70. **[ajaykarpur/patent-retrieval](https://github.com/ajaykarpur/patent-retrieval)** · ⭐ 8 — 专利检索引擎
71. **[ASUCICREPO/Patent-Novelty-Assessment](https://github.com/ASUCICREPO/Patent-Novelty-Assessment)** · ⭐ 21 — AI Agent 检索专利与论文并做新颖性评估、出报告
72. **[TPRO-2021/DuckDuckPatent](https://github.com/TPRO-2021/DuckDuckPatent)** · ⭐ 9 — 直觉式现有专利检索工具
73. **[mrrishit909/patent-landscape-engine](https://github.com/mrrishit909/patent-landscape-engine)** · ⭐ 1 — 按权利要求要素做 BM25+LSA 检索与重排（电池包语料示例）
74. **[patsnap/patent-literature-search-mcp](https://github.com/patsnap/patent-literature-search-mcp)** · ⭐ 86 — 覆盖 WIPO/EPO/USPTO/CNIPA/JPO/KIPO 的专利+文献检索 MCP（智慧芽官方开源）
75. **[patsnap/mcp](https://github.com/patsnap/mcp)** · ⭐ 70 — 2 亿+专利、文献、化学药物记录的 MCP
76. **[riemannzeta/patent_mcp_server](https://github.com/riemannzeta/patent_mcp_server)** · ⭐ 85 — USPTO 数据最全的 MCP（Patent Public Search / ODP / PTAB / 诉讼）
77. **[chrisryugj/korean-patent-mcp](https://github.com/chrisryugj/korean-patent-mcp)** · ⭐ 63 — KIPRIS 韩国专利/实用/商标/外观 7 个工具
78. **[parkerhancock/patent-client-agents](https://github.com/parkerhancock/patent-client-agents)** · ⭐ 56 — 给 AI Agent 的 IP 数据工具箱（USPTO/EPO/JPO/Google/MPEP/CPC）
79. **[KunihiroS/google-patents-mcp](https://github.com/KunihiroS/google-patents-mcp)** · ⭐ 41 — Google Patents MCP
80. **[handaas/patent-mcp-server](https://github.com/handaas/patent-mcp-server)** · ⭐ 31 — 中文专利检索 + 统计分析 MCP，面向专利情报分析
81. **[navisbio/OPS-patent-search-mcp](https://github.com/navisbio/OPS-patent-search-mcp)** · ⭐ 22 — EPO OPS 检索 MCP，含分析师工作流技能与评测
82. **[nuri428/mcp_kipris](https://github.com/nuri428/mcp_kipris)** · ⭐ 17 — KIPRIS Plus 检索 MCP
83. **[LeonardHope/USPTO-ODP-Natural-Language-Search](https://github.com/LeonardHope/USPTO-ODP-Natural-Language-Search)** · ⭐ 9 — USPTO 全 API 的自然语言 Skill（含审查档案、转让、上诉）
84. **[LeonardHope/Google-Patents-Natural-Language-API-Search](https://github.com/LeonardHope/Google-Patents-Natural-Language-API-Search)** · ⭐ 8 — Google Patents 纯英文自然语言检索 Skill
85. **[tushariitr-19/patents-mcp](https://github.com/tushariitr-19/patents-mcp)** · ⭐ 6 — 基于 Google Patents 公共数据集的检索 MCP
86. **[chasewhughes/mcp-prior-art](https://github.com/chasewhughes/mcp-prior-art)** · ⭐ 2 — 现有技术检索 + 专利态势分析的 MCP
87. **[Augmented-Nature/SureChEMBL-MCP-Server](https://github.com/Augmented-Nature/SureChEMBL-MCP-Server)** · ⭐ 8 — SureChEMBL 化学专利库 MCP
88. **[cyy1018abc-kyy/patent-research-skill](https://github.com/cyy1018abc-kyy/patent-research-skill)** · ⭐ 6 — 现有技术检索 + 证据链 + 验收门槛 Skill
89. **[prashantshukla01/Patent-Gap-Finder_MCP](https://github.com/prashantshukla01/Patent-Gap-Finder_MCP)** · ⭐ 6 — 论文 → 专利空白点发现 MCP

### 五、专利分析 / 挖掘 / 态势可视化

90. **[Patent2net/P2N-v3](https://github.com/Patent2net/P2N-v3)** · ⭐ 17 — 老牌开源专利分析工具箱：从 EPO OPS 采集、清洗、指标与可视化（Patent2Net）
91. **[arminnorouzi/patentGPT](https://github.com/arminnorouzi/patentGPT)** · ⭐ 40 — 从专利中抽取具体技术测量值/参数的原型
92. **[ryanwhalen/patent_similarity_data](https://github.com/ryanwhalen/patent_similarity_data)** · ⭐ 32 — 美国实用专利相似度数据构建与分析工具
93. **[Fraunhofer-ITMP/Pharmaceutical-patent-landscaping](https://github.com/Fraunhofer-ITMP/Pharmaceutical-patent-landscaping)** · ⭐ 15 — 医药专利态势分析方法与代码（论文配套）
94. **[LeonardHope/Claude-Skill-for-Patent-Landscape-Analysis](https://github.com/LeonardHope/Claude-Skill-for-Patent-Landscape-Analysis)** · ⭐ 12 — 专利态势分析 Skill
95. **[mattshax/ipagent](https://github.com/mattshax/ipagent)** · ⭐ 10 — 专利态势分析 Chatbot
96. **[KAILAI-Y/PatentInsight](https://github.com/KAILAI-Y/PatentInsight)** · ⭐ 9 — 专利数据检索 + AI 洞察 + 交互式行业分析报告
97. **[PatentAnalysis/patent-analysis](https://github.com/PatentAnalysis/patent-analysis)** · ⭐ 8 — 专利文本大数据分析 + ML + 交互可视化
98. **[DeltaCharlieAlpha/PatentAnalysisNotebooks](https://github.com/DeltaCharlieAlpha/PatentAnalysisNotebooks)** · ⭐ 11 — Python 专利分析 Notebook 实例集
99. **[Xinger-123/patent-landscape-agent](https://github.com/Xinger-123/patent-landscape-agent)** · ⭐ 2 — CPC+关键词定义技术领域 → 态势报告（趋势、申请人排名、CR4、引用）
100. **[CosmoGSpacely/markery](https://github.com/CosmoGSpacely/markery)** · ⭐ 3 — USPTO/EPO 专利与商标态势分析
101. **[shao-shuai/birdview-patent-landscape](https://github.com/shao-shuai/birdview-patent-landscape)** · ⭐ 4 — 专利态势鸟瞰图
102. **[machin0r/patent-landscape](https://github.com/machin0r/patent-landscape)** · ⭐ 4 — 专利地图/态势
103. **[siknue/patent_map_generator](https://github.com/siknue/patent_map_generator)** · ⭐ 1 — 基于 J-PlatPat 抓取数据做专利地图
104. **[wipo-analytics/asean_marine](https://github.com/wipo-analytics/asean_marine)** · ⭐ 5 — WIPO Analytics 的科技+专利态势分析范式（可复用其方法）
105. **[byte-love/patent-quality-pipeline](https://github.com/byte-love/patent-quality-pipeline)** · ⭐ 1 — 专利质量指标计算流水线（千万行级 xlsx 流式解析 + 校验链）
106. **[rumorinfo/patentQuality](https://github.com/rumorinfo/patentQuality)** · ⭐ 1 — 专利质量评估
107. **[yelim-woo/patent-quality](https://github.com/yelim-woo/patent-quality)** · ⭐ 1 — 专利定性/质量分析 Skill（IP Landscape）

### 六、专利分类、嵌入与相似度（NLP 底层能力）

108. **[Kohulan/DECIMER-Image_Transformer](https://github.com/Kohulan/DECIMER-Image_Transformer)** · ⭐ 420 — 化学结构图自动识别（专利化学图像必备）
109. **[arktrail/Dorothy-Ymir](https://github.com/arktrail/Dorothy-Ymir)** · ⭐ 144 — 专利分类 AI 方案
110. **[AI-Growth-Lab/PatentSBERTa](https://github.com/AI-Growth-Lab/PatentSBERTa)** · ⭐ 124 — 增强 SBERT 的专利距离/分类混合模型
111. **[dan2097/patent-reaction-extraction](https://github.com/dan2097/patent-reaction-extraction)** · ⭐ 114 — 化学反应的文本挖掘
112. **[julian-risch/PatentMatch](https://github.com/julian-risch/PatentMatch)** · ⭐ 49 — 权利要求 ↔ 现有技术匹配数据集与模型
113. **[zenanz/ChemPatentEmbeddings](https://github.com/zenanz/ChemPatentEmbeddings)** · ⭐ 21 — 化学专利嵌入
114. **[iliass-y/patenteb](https://github.com/iliass-y/patenteb)** · ⭐ 13 — PatenTEB：15 个专利文本嵌入任务 + 12 个 patembed 模型
115. **[kipi-ai/korpatbert](https://github.com/kipi-ai/korpatbert)** · ⭐ 70 — 韩语专利专用 BERT
116. **[kipi-ai/korpatelectra](https://github.com/kipi-ai/korpatelectra)** · ⭐ 7 — 韩语专利专用 ELECTRA
117. **[AI-Growth-Lab/Patent_p2p_similarity_w2v](https://github.com/AI-Growth-Lab/Patent_p2p_similarity_w2v)** · ⭐ 36 — 专利短语对相似度（对应 Kaggle US Patent Phrase Matching）
118. **[NICTA/t3as-pat-clas](https://github.com/NICTA/t3as-pat-clas)** · ⭐ 15 — CPC/IPC/USPC 分类检索与查询服务
119. **[yakushechkin/patent-classification](https://github.com/yakushechkin/patent-classification)** · ⭐ 3 — WIPO-alpha 专利分类（GloVe/领域词向量/BERT）
120. **[TMSDMAP/PatentEmbedIR](https://github.com/TMSDMAP/PatentEmbedIR)** · ⭐ 2 — 多视角专利嵌入 + 大规模检索 + 企业级技术相似度
121. **[hhxc6439/patent-embedding](https://github.com/hhxc6439/patent-embedding)** · ⭐ 1 — 专利审查助手 embedding 微调（Qwen3-Embedding-0.6B）
122. **[sofean-mso/PatentPhraseEmbedding](https://github.com/sofean-mso/PatentPhraseEmbedding)** · ⭐ 3 — 专利领域词/短语向量
123. **[gingergenius/patent-embedding-visualization](https://github.com/gingergenius/patent-embedding-visualization)** · ⭐ 2 — 带多侧面元数据的语义探索可视化
124. **[takeyuyu/patent-embedding-map](https://github.com/takeyuyu/patent-embedding-map)** · ⭐ 1 — J-PlatPat 数据嵌入分类生成技术地图
125. **[elio-guadagnini/Patent-Classification-with-Word-Embedding-and-Machine-Learning](https://github.com/elio-guadagnini/Patent-Classification-with-Word-Embedding-and-Machine-Learning)** · ⭐ 1 — 词向量 + ML 专利分类
126. **[AbiramiSukumaran/alloydb-pgvector](https://github.com/AbiramiSukumaran/alloydb-pgvector)** · ⭐ 6 — 专利数据向量检索（AlloyDB pgvector）

### 七、侵权分析 / FTO / 权利要求比对 / 规避设计

127. **[yuc16/PatentRadar](https://github.com/yuc16/PatentRadar)** · ⭐ 71 — 专利侵权分析系统：输入公开号 → 竞品侵权分析报告；已打包为通用 Agent Skill
128. **[cat-xierluo/patent-analysis.skill](https://github.com/cat-xierluo/patent-analysis.skill)** · ⭐ 5 — 系统化专利分析 Skill：侵权评估、权利要求比对等 7 类场景
129. **[dungnotnull/freedom-to-operate-analysis-agent-skill](https://github.com/dungnotnull/freedom-to-operate-analysis-agent-skill)** · ⭐ 9 — 工程化 FTO 分析框架：技术特征 vs 有效权利要求逐项扫描
130. **[mjtiv/patent-claim-mapper](https://github.com/mjtiv/patent-claim-mapper)** · ⭐ 7 — 权利要求 ↔ 说明书结构化对应分析、claim chart 原型
131. **[Sean-yh/claim-chart](https://github.com/Sean-yh/claim-chart)** · ⭐ 1 — 生成专利 claim chart 文档的 Codex 技能
132. **[yejingchen123/claim-chart](https://github.com/yejingchen123/claim-chart)** · ⭐ 3 — 简易 claim chart 工具
133. **[smythmyke/PatentEvidenceSearch](https://github.com/smythmyke/PatentEvidenceSearch)** · ⭐ 1 — Evidence of Use 检索，自动生成带评分的 claim chart
134. **[j-hedtke/patentkit](https://github.com/j-hedtke/patentkit)** · ⭐ 1 — 模块化专利检索分析工具箱（连接器 + 统一数据模型 + Agentic 检索 + claim chart）
135. **[Yannet11/patent-analysis](https://github.com/Yannet11/patent-analysis)** · ⭐ 5 — 预测侵权赔偿金额 + 依产品特征与权利要求文本判断是否侵权
136. **[zesutton2619/PAT](https://github.com/zesutton2619/PAT)** · ⭐ 6 — 辅助律师识别专利相似性/侵权线索
137. **[djfksjd/patent-search-skill](https://github.com/djfksjd/patent-search-skill)** · ⭐ 22 — 韩语：可专利性检索与「预 FTO」分离的 Agent Skill
138. **[patsnap-skills / cross-border-patent-risk-screen（以 Skill 形式分发，无独立仓库）](https://github.com/patsnap-skills)** — 跨境电商 10 分钟侵权初筛 Skill：外观/发明/实用，图像+语义双检索 + 逐项比对 + 规避建议（以 Agent Skill 形式分发，检索 GitHub `patsnap-skills` 组织）
139. **[MarcAngelo16/pipeline_patent](https://github.com/MarcAngelo16/pipeline_patent)** · ⭐ 1 — 抓取 PubChem 化合物数据做潜在侵权分析（印度市场）
140. **[bsankaranand/LS_IP_Intelligence_Tool](https://github.com/bsankaranand/LS_IP_Intelligence_Tool)** · ⭐ 1 — 载体/细胞系表达的按元件 FTO 状态评估（生物领域）

### 八、数据源 / API 客户端 / 爬虫 / 数据集

141. **[ip-tools/python-epo-ops-client](https://github.com/ip-tools/python-epo-ops-client)** · ⭐ 196 — EPO OPS 官方 API 的 Python 客户端（欧洲专利数据首选）
142. **[iamlemec/fastpat](https://github.com/iamlemec/fastpat)** · ⭐ 141 — 解析与聚类 USPTO 数据（申请、授权、转让、维持费）
143. **[will4906/PatentCrawler](https://github.com/will4906/PatentCrawler)** · ⭐ 140 — scrapy 中文专利爬虫（已停维护，可作参考实现）
144. **[parkerhancock/patent_client](https://github.com/parkerhancock/patent_client)** · ⭐ 128 — ORM 风格的多局专利数据客户端
145. **[ip-tools/uspto-opendata-python](https://github.com/ip-tools/uspto-opendata-python)** · ⭐ 114 — USPTO Open Data API 客户端（授权/申请/转让/审查）
146. **[cverluise/PatCit](https://github.com/cverluise/PatCit)** · ⭐ 114 — 专利引用数据构建（论文级）
147. **[ryanlstevens/google_patent_scraper](https://github.com/ryanlstevens/google_patent_scraper)** · ⭐ 108 — 抓取 patents.google.com
148. **[suzgunmirac/hupd](https://github.com/suzgunmirac/hupd)** · ⭐ 89 — 哈佛 USPTO 专利数据集（HUPD）
149. **[wenyalintw/Google-Patents-Scraper](https://github.com/wenyalintw/Google-Patents-Scraper)** · ⭐ 77 — 批量下载检索结果 PDF 及其同族
150. **[TamerKhraisha/uspto-patent-data-parser](https://github.com/TamerKhraisha/uspto-patent-data-parser)** · ⭐ 61 — 读取/解析 USPTO 批量数据
151. **[smcronin/uspto-cli](https://github.com/smcronin/uspto-cli)** · ⭐ 42 — 面向 Agent 的 USPTO ODP CLI
152. **[ropensci/patentsview](https://github.com/ropensci/patentsview)** · ⭐ 39 — PatentsView API 的 R 客户端
153. **[mattwang44/USPTO-PatFT-Web-Crawler](https://github.com/mattwang44/USPTO-PatFT-Web-Crawler)** · ⭐ 30 — USPTO PatFT 抓取 + PDF 批量下载
154. **[patent-dev/bulk-file-loader](https://github.com/patent-dev/bulk-file-loader)** · ⭐ 17 — 多源专利批量数据文件统一下载管理（USPTO 等）
155. **[JYProjs/patentpy](https://github.com/JYProjs/patentpy)** · ⭐ 17 — USPTO 批量数据 → 规整 DataFrame
156. **[volfpeter/uspto-patent-citation-graph](https://github.com/volfpeter/uspto-patent-citation-graph)** · ⭐ 16 — 按需下载引用数据并本地建库的引用网络
157. **[patent-dev/uspto-odp](https://github.com/patent-dev/uspto-odp)** · ⭐ 17 — USPTO ODP 的 Go 客户端
158. **[patent-dev/epo-ops](https://github.com/patent-dev/epo-ops)** · ⭐ 10 — EPO OPS 的 Go 客户端
159. **[anvaari/patent-crawler](https://github.com/anvaari/patent-crawler)** · ⭐ 15 — 按关键词抓 Google Patent
160. **[linuskohl/googlepatentscraper](https://github.com/linuskohl/googlepatentscraper)** · ⭐ 13 — Google Patents 文档抓取
161. **[IYuviva/PatentCrawler](https://github.com/IYuviva/PatentCrawler)** · ⭐ 11 — 爬 CNIPA 专利信息写入 Excel
162. **[iproduct-database/vpm-filter-spark](https://github.com/iproduct-database/vpm-filter-spark)** · ⭐ 15 — 虚拟专利标记（Virtual Patent Marking）爬虫
163. **[liuquan-ustc-qmai/CN-US-EU-JP-Patent_2020-2025](https://github.com/liuquan-ustc-qmai/CN-US-EU-JP-Patent_2020-2025)** · ⭐ 9 — 中/美/欧/日 2020-2025 专利文本数据集
164. **[kayzhou/patent_crawlers](https://github.com/kayzhou/patent_crawlers)** · ⭐ 2 — CNIPA 专利 FTP 抓取 + Streamlit UI
165. **[openKG-field/PatentGLUE_MT](https://github.com/openKG-field/PatentGLUE_MT)** · ⭐ 1 — 专利语言理解评测基准（机器翻译任务）
166. **[fros1y/epo-download](https://github.com/fros1y/epo-download)** · ⭐ 10 — EPO OPS 数据下载 API/工具
167. **[jsfiddler/Espacenet](https://github.com/jsfiddler/Espacenet)** · ⭐ 7 — 增强 Espacenet 检索的脚本集
168. **[sonesuke/google-patent-cli](https://github.com/sonesuke/google-patent-cli)** · ⭐ 7 — 面向人与 AI 的 Google Patents 检索/抓取 CLI
169. **[YobieBen/uspto-crawler-mcp](https://github.com/YobieBen/uspto-crawler-mcp)** · ⭐ 4 — Crawl4AI + MCP 的 USPTO 抓取
170. **[prrzetacznik/patent-parsing-tools](https://github.com/prrzetacznik/patent-parsing-tools)** · ⭐ 6 — USPTO 数据集生成/解析

### 九、专利翻译 / 垂直领域

171. **[edgetalker/Patent-translation](https://github.com/edgetalker/Patent-translation)** · ⭐ 4 — LLM 专利翻译系统：术语库管理 + 向量检索加速
172. **[shiki65536/patent-ai](https://github.com/shiki65536/patent-ai)** · ⭐ 1 — Gemini RAG 专利翻译
173. **[janguck/TEAMLAB_Patent_Translation](https://github.com/janguck/TEAMLAB_Patent_Translation)** — 专利翻译（TEAMLAB）
174. **[Anlan-Chan/patent-translation](https://github.com/Anlan-Chan/patent-translation)** — 专利翻译
175. **[indolering/patents](https://github.com/indolering/patents)** · ⭐ 1 — 实验性专利翻译 UI
176. **[crispy-su/patent-to-zemax](https://github.com/crispy-su/patent-to-zemax)** · ⭐ 9 — 光学专利 → 可校验的 Zemax 模型（Codex 技能）
177. **[wangxiaoou2013/Chinese-Optical-Lens-Patent-Generator](https://github.com/wangxiaoou2013/Chinese-Optical-Lens-Patent-Generator)** · ⭐ 1 — 透镜组设计的中国专利生成器
178. **[Renuk9390/Patent_Sentiment_Analysis](https://github.com/Renuk9390/Patent_Sentiment_Analysis)** · ⭐ 17 — 标注专利段落（优势/问题/中性）辅助审查
179. **[shashank524/patent_analysis](https://github.com/shashank524/patent_analysis)** · ⭐ 7 — 从专利中识别化合物结构与实体（Streamlit）
180. **[FeLusiani/PatentsTextAnalysis](https://github.com/FeLusiani/PatentsTextAnalysis)** · ⭐ 7 — Google Patents 抓取 + 文本挖掘
181. **[laluni/software-ai-patent-auditor](https://github.com/laluni/software-ai-patent-auditor)** · ⭐ 4 — 软件/AI 专利审计的端到端 RAG 应用
182. **[jrq3rq/IPGuardian-AI](https://github.com/jrq3rq/IPGuardian-AI)** · ⭐ 2 — 面向创始人的 IP 全生命周期助手（创意捕获、查新、FTO）
183. **[jaccen/AI-Copyright-Skill](https://github.com/jaccen/AI-Copyright-Skill)** · ⭐ 20 — 面向 AI 领域的知识产权技能（含软著等）

### 十、专利/知识产权管理系统（台账、年费、期限）

184. **[jjdejong/phpip](https://github.com/jjdejong/phpip)** · ⭐ 55 — 专利等 IP 权利组合管理 + 期限（docketing）系统 v2
185. **[chenshiming0802/thinkphp_fastadmin_ipr](https://github.com/chenshiming0802/thinkphp_fastadmin_ipr)** · ⭐ 20 — 开源知识产权管理系统：商标/专利/著作权台账（PHP + FastAdmin，MIT）
186. **[kiworkshop/Pascal](https://github.com/kiworkshop/Pascal)** · ⭐ 10 — 韩语专利报价计算器
187. **[AERussell/IPR-Timing-Estimator](https://github.com/AERussell/IPR-Timing-Estimator)** · ⭐ 1 — IPR 程序各节点时间估算表

---

## 许可

本仓库的文档与脚本采用 MIT License。**所列开源项目各自遵循其原始许可证**（部分为 GPL/AGPL，商用前请逐一核验），本项目不内嵌、不分发它们的代码，仅作流程引用与方法借鉴。

## 参与

欢迎提交 PR 补充：新的检索数据源、更细的质检项、你踩过的驳回坑。致谢清单同样接受补充——如果你知道本清单遗漏的专利开源项目，请直接加在对应分类下。

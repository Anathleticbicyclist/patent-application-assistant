# 开源项目 ↔ 流程步骤映射（精选）

只列最直接可用的一层，完整 187 项见 `open-source-index.md`。
标 ✅ 的表示本技能已自带可离线运行的实现（`scripts/` 下），不依赖外部安装；其余为「按需调用」。

| 已接线的能力 | 对应开源项目 | 本地实现 |
|---|---|---|
| ✅ 查新检索计划与多源链接 | `pqaidevteam/pqai`、`patsnap/patent-literature-search-mcp`、`riemannzeta/patent_mcp_server`、`KunihiroS/google-patents-mcp` | `prior_art_search.py` + `mcp_setup.py` |
| ✅ 说明书附图 | `PisenAILab/china-patent-figure-skill`（方法参照） | `figure_gen.py` |
| ✅ 权利要求形式检查 | `Sean-yh/claim-chart`、`CNIPA-AI/patent-xml-generator`（规范参照） | `claim_check.py` |
| ✅ 侵权比对表 | `mjtiv/patent-claim-mapper`、`smythmyke/PatentEvidenceSearch` | `claim_chart.py` |
| ✅ 交付物机检 | `LeonardHope/Claude-Skill-for-Patent-Filing-Quality-Control`（清单参照） | `check_deliverable.py` |

| 流程步骤 | 首选 | 备选 | 说明 |
|---|---|---|---|
| P1 技术结构化 | 本技能 `references/workflow.md` | `wanshuiyin/Auto-claude-code-research-in-sleep` 的 `patent-pipeline` | 后者提供「发明结构化」技能的完整阶段模板 |
| P2 保护点挖掘 | 本技能六视角 | `Obviously-Not/patent-skills`、`AqooDer/patent-mining-disclosure-skill` | 后者偏「从代码/项目里挖点」 |
| P3 查新检索（中国） | CNIPA 官方检索 + `patsnap/patent-literature-search-mcp` | `will4906/PatentCrawler`、`kayzhou/patent_crawlers` | 官方库权威，MCP 便于批量与结构化 |
| P3 查新检索（美国） | `riemannzeta/patent_mcp_server` | `ip-tools/uspto-opendata-python`、`smcronin/uspto-cli` | 含审查档案、PTAB、转让 |
| P3 语义检索 | `pqaidevteam/pqai` | `helmersl/patent_similarity_search`、`us/patent-similarity-rag` | PQAI 是稠密检索，适合「描述一段话找相似专利」 |
| P3 欧洲 | `navisbio/OPS-patent-search-mcp` | `ip-tools/python-epo-ops-client` | INPADOC 同族最全 |
| P4 可专利性 | 本技能三步法 | `ASUCICREPO/Patent-Novelty-Assessment`、`AIforIP/PatEx-Gym` | 后两者做自动化新颖性评估 |
| P5 交底书 | 本技能模板 | `handsomestWei/patent-disclosure-skill`、`fuyuxiang/patent-disclosure-skill` | 结构与话术可直接借鉴 |
| P5 附图 | `PisenAILab/china-patent-figure-skill` | 手绘 + 编号规范 | STEP→国知局格式，自动标号引线 |
| P6 权利要求/说明书 | 本技能 `claims-drafting.md` | `handsomeZR-netizen/cn-patent-drafter`、`QiYao-Wang/AutoPatent` | 后者是多 Agent 长文本生成 |
| P6 形式校验 | `CNIPA-AI/patent-xml-generator` | `StellaQIU27/claude-skill-patent-writing-chinese` | XML 报送前必过 |
| P7 侵权比对 | `mjtiv/patent-claim-mapper` | `Sean-yh/claim-chart`、`smythmyke/PatentEvidenceSearch` | 轴是「权项要素 × 被控方案」 |
| P7 竞品报告 | `yuc16/PatentRadar` | `patsnap-skills` cross-border 技能 | 输入公开号出报告 |
| P7 FTO 工程化 | `dungnotnull/freedom-to-operate-analysis-agent-skill` | `cat-xierluo/patent-analysis.skill` | 特征扫描 + 风险分级 |
| P8 审查意见答复 | 本技能 `review-checklist.md` | `sinonchum/PatentFlow`、`kgtceo/office-action`、`talenlin/oa-response-drafter` | 后者按 OA 逐条起草 |
| 数据落地 | `iamlemec/fastpat`、`TamerKhraisha/uspto-patent-data-parser` | `google/patents-public-data` | 批量解析与引用网络 |
| 态势分析 | `Patent2net/P2N-v3` | `Xinger-123/patent-landscape-agent` | 趋势、申请人、CR4、引证 |
| 专利翻译 | `edgetalker/Patent-translation` | `shiki65536/patent-ai` | 术语库 + 向量检索 |
| 台账管理 | `jjdejong/phpip` | `chenshiming0802/thinkphp_fastadmin_ipr` | 期限、年费、组合管理 |

## 使用注意

- 这些项目**不随本技能分发**，按各自 LICENSE 使用；商用前逐一核验授权（部分为 GPL/AGPL）。
- MCP 类项目需自备 API Key/配额，遵守各局条款（EPO OPS 有日配额，USPTO 有速率限制）。
- 抓取类项目（Google Patents 爬虫等）存在反爬与条款风险，优先用官方 API。
- 任何工具的输出都要人工复核，尤其是它「引用」的专利号与段落。

<div align="center">

# OpenPE — 从原理到终局

**基于大语言模型的第一性原理因果分析框架**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-orange.svg)](https://claude.ai/claude-code)

[English](README.md) · [中文](README_zh.md) · [한국어](README_ko.md)

</div>

---

每件事的发生都有原因。每个原因背后还有原因。这构成了一个网络——不是一条线，而是一张网。每个节点都是其自身因果网络的中心。

但这张网不会无限延展。离起点越远，解释力就越弱——不是线性衰减，而是乘法衰减。到某个点，线索就断了。这个边界不是缺陷，而是从一个起点出发所能理解的自然视野。

OpenPE 在这个视野范围内工作。它从第一性原理构建因果图，对每条因果链进行反驳检验，只在证据能支撑的范围内做出预测——从**原理**到**终局**。

---

## 快速开始

### 方式一：手动配置

```bash
git clone https://github.com/xinzhuwang-wxz/OpenPE.git
cd OpenPE

# 安装 pixi（如果尚未安装）
curl -fsSL https://pixi.sh/install.sh | bash

# 创建分析项目
python src/scaffold_analysis.py analyses/my_analysis
cd analyses/my_analysis

# 配置
# 编辑 analysis_config.yaml → 设置 question 和 domain
pixi install
claude   # 启动 orchestrator agent
```

### 方式二：Claude Code 一键执行

将以下内容直接粘贴到 [Claude Code](https://claude.ai/claude-code)：

```
Clone https://github.com/xinzhuwang-wxz/OpenPE and use OpenPE's scaffolding + orchestrator flow to complete this analysis: <你的问题>
```

Claude Code 将自动创建分析目录、安装依赖、运行全部七个阶段——产出包含因果 DAG、反驳检验、情景预测和审计链的完整报告。

---

## 工作原理

```
问题 ─→ 阶段 0：发现 ─→ 阶段 1：策略 ─→ 阶段 2：探索
           │              │              │
       因果 DAG       方法选择        EDA + 图表
       数据采集       EP 评估        分布检查
       质量门控       链规划
           │              │              │
           ▼              ▼              ▼
       阶段 3：分析 ─→ 阶段 4：预测 ─→ 阶段 5：验证
           │              │              │
       因果检验       蒙特卡洛模拟    独立复现
       三重反驳       敏感度分析      EP 传播审计
       EP 传播       终局分类        因果标签审计
           │              │              │
           ▼              ▼              ▼
                  阶段 6：文档
                      │
                  分析报告 (MD + PDF)
                  审计链 (声明 + 数据源 + 逻辑)
                  EP 衰减可视化
```

每个阶段遵循相同的循环：

1. **执行** — 子 agent 生成产物（以规划模式开始）
2. **审查** — 独立审查员将问题分为 A（阻塞）/ B（必须修复）/ C（建议）
3. **检查** — 仲裁者决定通过/迭代/回退
4. **提交** — 状态记录在 STATE.md 中
5. **人工门控** — 阶段 5 之后，人工审批后才进入最终报告

---

## 三大核心创新

### 1. 解释力 (EP) — 量化不确定性下的推理

多数分析框架将置信度视为二元的："我们相信"或"我们不信"。OpenPE 引入了**解释力 (Explanatory Power)** ——一种连续的、乘法衰减的度量，追踪因果链上解释价值的存留程度。

```
EP = truth × relevance

truth:     我们对这条因果关系的真实性有多确信？(0–1)
relevance: 这条因果关系解释了结果方差的多大比例？(0–1)
```

沿因果链 A → B → C → D，**联合 EP 乘法衰减**：

```
Joint_EP = EP(A→B) × EP(B→C) × EP(C→D)
```

这带来一个深刻的结论：长因果链会自然失去解释力。一条 5 环链，每条边 EP=0.7，联合 EP 仅为 0.17——刚过软截断阈值。框架强制执行明确的停止规则：

| 阈值 | 联合 EP | 动作 |
|------|---------|------|
| **硬截断** | < 0.05 | 停止探索。此链已超出分析视野。 |
| **软截断** | < 0.15 | 仅轻量评估。不展开子链。 |
| **子链展开** | > 0.30 | 值得深入研究。创建子分析。 |

EP 值在分析生命周期中演变。分析前标签（`LITERATURE_SUPPORTED` → truth=0.70、`THEORIZED` → 0.40、`SPECULATIVE` → 0.15）通过阶段 3 反驳检验更新为分析后分类（`DATA_SUPPORTED` → 0.85、`CORRELATION` → 0.50、`HYPOTHESIZED` → 0.15、`DISPUTED` → 0.30）。

**为什么重要：** EP 使分析置信度的衰减变得可见和可量化。每条因果论证都携带一个数字，读者可以追溯和挑战，而不是在行文中隐藏不确定性。

### 2. 安慰剂锚定的矛盾检测 (DISPUTED 分类)

标准因果推断将反驳结果当作计分卡：通过的测试越多 → 证据越强。OpenPE 增加了一个语义层，检测证据模式中的**逻辑矛盾**。

每条因果边经历三项反驳检验：
- **安慰剂检验** — 用随机变量替换处理变量；效应应消失
- **随机混杂检验** — 添加随机混杂因子；估计应保持稳定
- **数据子集检验** — 在随机 80% 子集上估计；应保持一致

分类以**安慰剂为因果锚点**：

- 如果安慰剂**通过**（效应是处理特异的/"真实的"），那么子集和混杂检验的失败就是矛盾的——真实效应应该是稳定和稳健的
- 如果安慰剂**未通过**（效应不是处理特异的），那么子集通过就是矛盾的——非真实的效应不可能完美稳定

当检测到这些矛盾时，边被分类为 `DISPUTED`——既不是 DATA_SUPPORTED，也不是 CORRELATION，而是标记为需要人工审查。框架拒绝对矛盾证据进行自动分类。

```python
# 矛盾检测逻辑 (方案 C)
if placebo_passed and (not subset_passed or not cc_passed):
    return "DISPUTED"   # 真实但不稳定/受混杂 — 矛盾
if not placebo_passed and subset_passed:
    return "DISPUTED"   # 不真实但完美稳定 — 矛盾
```

**为什么重要：** 多数框架即使在证据自相矛盾时也强制分类。DISPUTED 承认有些模式没有干净的答案——将其路由到人工判断，而非算法猜测。

### 3. 跨分析记忆系统与证据驱动的层级转换

OpenPE 的分析不从零开始。分层记忆系统在分析间积累领域知识，通过置信度驱动的生命周期管理：

| 层级 | 范围 | 加载时机 | 内容 |
|------|------|---------|------|
| **L0** | 通用 | 始终加载 | 经 ≥3 次分析验证的跨领域原则 |
| **L1** | 领域 | 匹配领域时加载 | 领域特定经验（方法、数据源、失败教训）|
| **L2** | 详情 | 按需加载 | 完整分析摘要（自动生成）|

记忆不是静态的，它们会演化：

```
创建 (L1, 置信度=0.50)
  → 被第 2 次分析佐证 (+0.15 → 0.65)
  → 被第 3 次分析佐证 (+0.15 → 0.80) → 升级到 L0
  → 被第 4 次分析反驳 (-0.25 → 0.55)
  → 被第 5 次分析反驳 (-0.25 → 0.30) → 降回 L1
  → 随时间衰减 (每次分析 -0.01)
  → 最终：置信度 < 0.05 且 热度 < 0.01 → 遗忘（删除）
```

生命周期在 `commit_session()` 中完全自动化：
- **升级** (L1→L0)：≥2 次独立佐证
- **降级** (L0→L1)：置信度降至 0.30 以下
- **遗忘**：置信度 ≤ 0.05 且热度 < 0.01 → 文件删除
- **归档**：冷的 L2 条目（热度 < 0.1）移至 `_archive/`
- **幂等提交**：标记文件防止崩溃重启后重复衰减

全局记忆位于仓库根目录（`memory/`）。每次新分析通过脚手架继承快照，完成后将高置信度发现推送回全局。

**为什么重要：** 同一领域的第 3 次分析比第 1 次更好——不是因为代码改进了，而是因为记忆系统学会了什么有效、什么无效。

---

## 借鉴与适配

OpenPE 借鉴了三个优秀项目的思路，并适配到第一性原理分析场景中：

### ACG Protocol → 审计链 (IGM/SSR/VAR)

[ACG Protocol](https://github.com/Kos-M/acg_protocol) 引入了内联溯源标记和源验证注册表。OpenPE 将其适配为三层审计链：

- **IGM**（内联溯源标记）：`[C1:a1b2c3d4e5:phase3/data.csv:row42]` — 每条声明嵌入哈希链接到其来源
- **SSR**（结构化数据源注册表）：SHA-256 哈希、源类型、每个数据集的验证状态
- **VAR**（真实性审计注册表）：追踪推理逻辑链，通过 `verify_logic()` 自动一致性检查

### Graphiti → 时间因果知识图谱

[Graphiti](https://github.com/getzep/graphiti) 的时间 EntityEdge 模型启发了 OpenPE 因果知识图谱中的有效性窗口模式。关系携带 `valid_at`/`invalid_at`/`expired_at` 时间戳，使图谱能记录因果机制*何时*为真——而非仅仅*是否*为真。结合置信度驱动的复用策略（SKIP / LIGHTWEIGHT_VERIFY / MUST_RETEST），高置信度关系在未来分析中可跳过重测。

### OpenViking → 记忆热度评分

[OpenViking](https://github.com/volcengine/OpenViking) 的记忆生命周期系统提供了热度评分公式：`sigmoid(频率) × 指数衰减(时近度)`。OpenPE 用此区分活跃使用的记忆和陈旧的记忆，驱动归档和遗忘机制，保持记忆系统有界。

---

## 项目结构

```
OpenPE/
├── src/
│   ├── scaffold_analysis.py    # 创建分析目录
│   ├── templates/              # CLAUDE.md 模板 + 共享脚本
│   │   ├── scripts/            # EP 引擎、因果管道、记忆存储...
│   │   └── report_template/    # 专业 PDF 样式
│   ├── methodology/            # 规范文档 (01-09 + 附录)
│   ├── conventions/            # 领域知识（因果推断、时间序列、面板分析）
│   └── orchestration/          # 会话管理规范
├── .claude/
│   ├── agents/                 # Agent 配置文件 (15+ 个专业 agent)
│   ├── hooks/                  # 分析隔离沙箱
│   └── skills/                 # 分析管线技能
├── CLAUDE.md                   # 项目级说明
├── pyproject.toml              # 根 pixi 配置
└── LICENSE                     # GPL-3.0
```

脚手架创建的分析结构：

```
analyses/my_analysis/           # 独立 git 仓库
├── CLAUDE.md                   # Orchestrator 协议（自包含）
├── analysis_config.yaml        # 问题、领域、EP 阈值
├── STATE.md                    # 管线状态（阶段、迭代次数、阻塞项）
├── pixi.toml                   # 环境 + 任务图
├── scripts/                    # 共享模块（从模板复制）
├── memory/                     # L0/L1/L2/causal_graph
├── conventions/ → src/conventions  # 符号链接
├── methodology/ → src/methodology  # 符号链接
└── phase{0..6}_*/
    ├── CLAUDE.md               # 阶段特定说明
    ├── exec/                   # 产物 (DISCOVERY.md, ANALYSIS.md, ...)
    ├── scripts/                # 阶段特定代码
    ├── figures/                # PDF + PNG 图表
    └── review/                 # REVIEW_NOTES.md
```

---

## 输入模式

| 模式 | 场景 | 行为 |
|------|------|------|
| **A** — 仅问题 | 未提供数据 | 全自主：假设生成、数据采集、质量门控 |
| **B** — 问题 + 数据 | 用户提供数据集 | 用户数据通过与采集数据相同的质量门控 |
| **C** — 问题 + 假设 | 用户提供因果假设 | 用户假设成为候选 DAG 之一——无信任特权 |

---

## 环境要求

- **Python** ≥ 3.11
- **[pixi](https://pixi.sh)** — 依赖管理（自动安装所有其他依赖）
- **[Claude Code](https://claude.ai/claude-code)** — LLM orchestrator
- **pandoc** ≥ 3.0 + xelatex — PDF 生成（通过 pixi 安装）

---

## 致谢

OpenPE 源于 [slop-X](https://github.com/jfc-mit/slop-X)，并将其推广到任意领域。

我们还从以下开源项目中汲取灵感并适配模式：

| 项目 | 借鉴内容 | 许可证 |
|------|---------|--------|
| [ACG Protocol](https://github.com/Kos-M/acg_protocol) | UGVP 事实溯源 (IGM/SSR/VAR 审计结构) | — |
| [Graphiti](https://github.com/getzep/graphiti) | 知识图谱的时间 EntityEdge 有效性模型 | Apache-2.0 |
| [OpenViking](https://github.com/volcengine/OpenViking) | 记忆生命周期热度评分 (`sigmoid × recency`) | Apache-2.0 |
| [Causica](https://github.com/microsoft/causica) | 图评估指标模式 | MIT |
| [causal-learn](https://github.com/py-why/causal-learn) | PC 算法用于因果结构发现 | MIT |
| [DoWhy](https://github.com/py-why/dowhy) | 因果推断 + 反驳检验框架 | MIT |
| [DeerFlow](https://github.com/bytedance/deer-flow) | 多 agent 编排模式 | MIT |

开发工作流由 [Superpowers](https://github.com/cline/superpowers-marketplace) Claude Code 技能驱动——特别是 `writing-plans`、`subagent-driven-development`、`test-driven-development` 和 `code-reviewer`。

---

## 许可证

[GPL-3.0](LICENSE) — 可自由使用、修改和分发。衍生作品必须同样以 GPL-3.0 开源。

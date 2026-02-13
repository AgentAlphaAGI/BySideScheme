<div align="center">

# BySideScheme

### 来事儿 —— AI 驱动的职场局势感知与策略引擎

**让每一次汇报都有预案，让每一段关系都有图谱，让每一个决策都有记忆。**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Neo4j](https://img.shields.io/badge/Neo4j_5-4581C3?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![AutoGen](https://img.shields.io/badge/AutoGen-Multi_Agent-FF6F00?style=flat-square)](https://microsoft.github.io/autogen)

</div>

---

## 它解决什么问题

职场中真正决定成败的，往往不是技术能力，而是**信息差**、**关系网**和**时机判断**。

- 你知道隔壁组长上周跟 VP 的 1:1 聊了什么吗？
- 两个月前你在周报里埋的那句预警，关键时刻还能想起来吗？
- 明天的评审会上，谁会站你这边、谁会捅刀子，你有把握吗？

BySideScheme 不是一个聊天机器人。它是一个**持续运转的局势感知系统**——像一个永远在线的幕僚，帮你记住一切、看透关系、推演未来、生成话术。

---

## 核心能力

### 动态知识图谱 — 让关系网"活"起来

每一条你输入的事实，系统都会通过 LLM 自动抽取其中的人物、事件、项目、组织及它们之间的关系，写入 Neo4j 图数据库。

```
"Alex 上周在和 VP Chen 的 1:1 里，主动提到天网项目架构有隐患"
                    │
                    ▼  LLM 实体关系抽取
        ┌──────────────────────────────┐
        │  Alex ──LOBBIED──▶ VP Chen  │
        │         sentiment: -0.7      │
        │         evidence: "提议接手"  │
        └──────────────────────────────┘
```

- **增量合并**：同一个人物出现多次不会重复创建，而是更新权重、情感值和证据链
- **5 类实体**：Person / Event / Project / Resource / Organization
- **20+ 种关系**：REPORTS_TO / ALLIES_WITH / OPPOSES / LOBBIED / WARNED 等
- **中心性分析**：自动识别谁是关键人物、哪些关系存在风险
- **力导向可视化**：节点按类型着色，边按情感着色（绿色=正向，红色=负向），厚度反映权重

> 真实效果：连续输入 7 天事实后，图谱将呈现出一张包含 10+ 实体、20+ 关系的动态局势地图，每个节点都携带时间线和证据链。

---

### 三层叙事引擎 — 同一件事，三种说法

面对同一个职场事件，系统结合**局势配置 + 长期记忆 + 图谱上下文**，生成三个维度的输出：

| 层级 | 目的 | 示例 |
|------|------|------|
| **对上汇报** | 政治正确，管理预期 | "如两周前周报所述，我们已预判到该风险并部署了 Plan B，全程 2 分钟恢复" |
| **自我复盘** | 看穿本质，识别风险 | "Alex 的攻击不是技术关切，而是在用'架构隐患'包装抢功意图" |
| **下一步行动** | 具体可执行的策略 | "立刻写复盘报告，把'事故'重新定义为'成功的容灾演练'" |

背后是一个 **5 维决策引擎**（风险/收益/政治/时机/资源），确保建议不是泛泛而谈，而是基于你的真实处境量身定制。

---

### 多智能体模拟器 — 先在脑中打一仗

明天要跟强势的产品经理 + 和稀泥的老板 + 看热闹的竞争对手开会？

模拟器让你**提前排练**。每个角色由独立的 LLM 驱动，性格、说话风格、利益诉求各不相同：

```
你: "天网 AB 实验 CTR 提升了 12%，Alex 你说的隐患具体指哪个模块？"

Alex (GLM):  "数据是好的，但极端场景呢？第三方挂了怎么办？"
Jessica (DeepSeek): "12% 不错...但我想看留存数据。"
David (Qwen): "要不再观察一个版本？"

┌─ 实时洞察 ─────────────────────────────┐
│  Alex 必然攻击"容灾"——建议你主动亮出     │
│  Plan B，把他的攻击点变成你的加分项。    │
└──────────────────────────────────────┘
```

- 支持 DeepSeek / Qwen / GLM 等多模型混用，不同性格用不同模型
- SSE 流式输出，逐字看到 AI 角色的"思考过程"
- 人物画像随对话动态演进，支持版本回溯和一键回滚
- **严格数据隔离**：模拟推演只读图谱，不写入——你的真实局势数据不会被虚构内容污染

---

### 长期记忆系统 — 它不会忘记任何一个细节

基于 Mem0 + Qdrant 向量数据库，系统持续积累你输入的每一条事实和生成的每一条策略。

关键时刻，记忆会被**自动唤醒**：

```
Day 2  写入记忆: "已部署 Plan B 降级开关" + "周报邮件预警风险"
  ...
Day 7  RankAI 宕机，Alex 在 200 人群公开攻击
  │
  └──▶ 记忆检索命中: "你两周前就预警过，而且 Plan B 已就绪"
       │
       └──▶ 生成绝杀话术: "正如两周前周报所述..."
```

记忆还会自动整合提炼为高维度 **Insight**：

> *"在与风险厌恶型领导共事时，降级方案要'偷偷做好'而非'据理力争'。领导不想听坏消息，但需要你兜底。邮件比口头承诺重量级高出十倍。"*

---

## 系统架构

```
                          ┌──────────────┐
                          │   React 18   │
                          │  Cyberpunk UI│
                          │ Force Graph  │
                          └──────┬───────┘
                                 │ REST API
                                 ▼
┌────────────────────────────────────────────────────────┐
│                     FastAPI Backend                    │
│                                                        │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────┐   │
│  │  Advisor    │   │  Simulator   │   │  Graph API │   │
│  │  Service    │   │  (AutoGen)   │   │            │   │
│  │             │   │              │   │            │   │
│  │  Decision ──┤   │  Multi-Agent ┤   │  Extract   │   │
│  │  Engine     │   │  SSE Stream  │   │  Merge     │   │
│  │             │   │              │   │  Query     │   │
│  │  Narrative ─┤   │  Insights ───┤   │  Analyze   │   │
│  │  Generator  │   │  Engine      │   │            │   │
│  └──────┬──────┘   └──────┬───────┘   └─────┬──────┘   │
│         │ R/W             │ Read Only       │ R/W      │
│         ▼                 ▼                 ▼          │
│  ┌─────────────────────────────────────────────────┐   │
│  │          Memory Layer    │    Graph Layer       │   │
│  │  ┌───────────┐  ┌────┐   │  ┌──────────────────┐│   │
│  │  │ Mem0      │  │SQLite│ │  │ Neo4j 5          ││   │
│  │  │ + Qdrant  │  │    │   │  │ (Docker)         ││   │
│  │  │ Vectors   │  │Meta│   │  │ Entities+Rels    ││   │
│  │  └───────────┘  └────┘   │  └──────────────────┘│   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
                                 │
                                 ▼ OpenAI-Compatible API
                     ┌─────────────────────────┐
                     │  SiliconFlow / DeepSeek │
                     │  Qwen / GLM / ...       │
                     └─────────────────────────┘
```

**数据流原则**：Advisor 对记忆和图谱有完整的读写权限；Simulator 只能读取图谱和记忆作为推演上下文，但不向其中写入任何数据。这保证了真实局势数据的纯净性。

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 后端框架 | Python 3.10+ / FastAPI | 异步 API 服务 |
| 多智能体 | AutoGen 0.2 | 模拟器多角色对话编排 |
| 向量记忆 | Mem0 + Qdrant | 语义检索、记忆积累与洞察提炼 |
| 图数据库 | Neo4j 5 (Docker) | 实体关系存储、中心性分析、路径查询 |
| 关系型存储 | SQLite | 局势配置、画像版本、反馈记录 |
| LLM 引擎 | SiliconFlow / OpenAI 兼容 | 多模型混用 (DeepSeek, Qwen, GLM) |
| 前端框架 | React 18 / TypeScript / Vite | SPA 单页应用 |
| UI 风格 | Tailwind CSS | 赛博朋克主题 |
| 状态管理 | Zustand | 轻量状态管理 |
| 图谱可视化 | react-force-graph-2d | 力导向交互式关系图 |
| 包管理 | uv (后端) / pnpm (前端) | 极速依赖管理 |

---

## 适用场景

| 场景 | 系统如何帮你 |
|------|-------------|
| **晋升窗口期** | 记忆积累证据链，图谱追踪支持者/反对者，生成答辩材料 |
| **跨部门博弈** | 图谱可视化多方关系，模拟器预演会议走向，三层叙事应对不同听众 |
| **突发危机** | 自动唤醒历史预警记忆，生成"化事故为功劳"的重构话术 |
| **向上管理** | 识别领导风格和诉求，生成匹配其偏好的汇报口径 |
| **竞争对手应对** | 图谱追踪对手的拉拢路径和影响力变化，提前预判攻击方向 |
| **央企/国企环境** | 理解"政治站位"逻辑，给出符合体制生态的策略（文件留痕、红头文件、党委会叙事） |
| **互联网大厂** | 理解"数据说话"逻辑，生成 ROI 导向的汇报和技术复盘 |

---

## 快速开始

**前置要求**：Docker、Python 3.10+、Node.js 18+、pnpm

### 1. 启动图数据库

```bash
cd BySideScheme_backend
docker compose up -d    # 启动 Neo4j (端口 17474/17687)
```

### 2. 启动后端

```bash
cd BySideScheme_backend
cp .env.example .env    # 填写 LLM API Key 等配置
uv venv && uv pip install -r requirements.txt
uv run main.py          # 默认 http://localhost:8000
```

### 3. 启动前端

```bash
cd BySideScheme_web
pnpm install
pnpm dev                # 默认 http://localhost:5173
```

打开浏览器访问 `http://localhost:5173`，配置你的局势，开始输入第一条事实。

---

## 项目结构

```
BySideScheme/
│
├── BySideScheme_backend/          # 后端核心服务
│   ├── docker-compose.yml         # Neo4j 容器编排
│   ├── main.py                    # 程序入口
│   ├── requirements.txt           # Python 依赖
│   ├── .env                       # 环境变量 (API Key, DB 配置)
│   └── src/
│       ├── api/routers/           # advice / graph / simulator / feedback
│       ├── core/                  # llm_client / memory / neo4j_client / graph_engine
│       │                          # decision / generator / insights
│       ├── services/              # AdvisorService (核心编排)
│       ├── autogen_agents/        # AutoGen 多智能体定义
│       └── prompts/               # YAML Prompt 模板 (decision / narrative / graph)
│
├── BySideScheme_web/              # 前端用户界面
│   └── src/
│       ├── pages/                 # Dashboard / Advisor / Simulator / GraphView
│       │                          # Memory / Profile
│       ├── components/            # Layout / EntityDetailPanel / AnalysisPanel
│       └── services/              # API 客户端
│
├── API_REFERENCE.md               # 完整 API 接口文档
├── REQUIREMENTS.md                # 产品需求文档
├── WALKTHROUGH_SCRIPT.md          # 互联网大厂演练剧本
└── WALKTHROUGH_SOE_SCRIPT.md      # 央企环境演练剧本
```

---

## 演练剧本

我们提供了两套完整的端到端演练剧本，覆盖从局势配置到危机反转的全流程：

| 剧本 | 背景 | 核心冲突 | 天数 |
|------|------|---------|------|
| [互联网大厂版](./WALKTHROUGH_SCRIPT.md) | P6 冲刺 P7，手握核心项目 | 竞争对手三段式围剿 vs Plan B 伏笔引爆 | 9 天 |
| [央企版](./WALKTHROUGH_SOE_SCRIPT.md) | 科级冲处级，数字化转型项目 | 地头蛇三线攻势 vs 政治通路构建 | 12 天 |

每个剧本都标注了图谱变化、记忆读写、模拟器使用和三层叙事输出的预期效果，可直接作为系统演示脚本使用。

---

## 文档

- [后端详细文档](./BySideScheme_backend/README.md) — 环境配置、模型选择、目录说明
- [API 接口文档](./API_REFERENCE.md) — 全部 REST 端点、请求/响应示例
- [产品需求文档](./REQUIREMENTS.md) — 功能范围、设计约束、验收标准

---

<div align="center">

**BySideScheme** — 职场不是战场，但你需要一个军师。

</div>

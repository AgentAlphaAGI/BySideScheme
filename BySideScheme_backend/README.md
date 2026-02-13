# 来事儿 (BySideScheme) - 后端服务

**来事儿** 的核心后端服务，基于 **FastAPI** + **AutoGen** + **Mem0** + **Neo4j** 构建，提供具备长期记忆、知识图谱与政治智慧的职场辅助能力。

## 核心能力

- **RESTful API**: 提供标准的 HTTP 接口，供前端或其他客户端调用。
- **多模型支持**: 兼容 OpenAI 协议，支持 DeepSeek、Qwen、GLM 等主流大模型，可为不同模块指定不同模型。
- **本地记忆**: 集成 Mem0 + Qdrant，实现数据的本地向量化存储与检索，保障隐私。
- **知识图谱**: 集成 Neo4j，从用户输入的事实中自动抽取实体关系，构建动态职场局势图谱。
- **多智能体模拟**: 基于 AutoGen 的多角色对话模拟，支持会前预演与局势推演。
- **流式响应**: 支持 SSE (Server-Sent Events) 与 WebSocket，实现实时对话体验。
- **任务队列**: 异步处理长耗时推演任务，支持状态轮询与结果订阅。

## 技术栈

| 组件 | 技术 |
|------|------|
| Runtime | Python 3.10+ |
| Framework | FastAPI |
| Agent Framework | AutoGen 0.2.35 |
| Memory | Mem0 + Qdrant (本地向量存储) |
| Graph Database | Neo4j 5 (Docker) |
| Relational DB | SQLite |
| Package Manager | uv |

## 快速开始

### 1. 环境准备

```bash
# 安装 uv (如果尚未安装)
pip install uv
# 或 macOS: brew install uv
# 或 Linux/WSL: curl -LsSf https://astral.sh/uv/install.sh | sh

# 进入后端目录
cd BySideScheme_backend

# 创建虚拟环境
uv venv
```

### 2. 安装依赖

```bash
uv pip install -r requirements.txt
```

### 3. 启动 Neo4j (Docker)

```bash
docker compose up -d
```

这会启动一个 Neo4j 容器，数据持久化到 `data/neo4j/` 目录：
- **Bolt 端口**: 17687 (应用连接)
- **Browser 端口**: 17474 (浏览器访问 `http://localhost:17474`)
- **默认账号**: neo4j / bysidescheme

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填入必要的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# ==========================================
# 1. 基础安全配置 (可选)
# ==========================================
# 设置后前端请求 Header 必须携带 X-API-Key
# 留空则不开启鉴权（仅限本地开发）
BySideScheme_API_KEY=

# ==========================================
# 2. 模型引擎配置 (至少配置一组)
# ==========================================

# --- SiliconFlow (推荐，集成多家模型) ---
SILICONFLOW_API_KEY=sk-your-siliconflow-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3

# --- OpenAI (可选) ---
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o

# ==========================================
# 3. 模块引擎映射
# ==========================================
# 指定各模块使用哪个引擎 (填引擎前缀，大写)

DECISION_ENGINE=SILICONFLOW        # 决策引擎
NARRATIVE_ENGINE=SILICONFLOW       # 叙事引擎
SIMULATOR_INSIGHTS_ENGINE=SILICONFLOW  # 洞察引擎
GRAPH_ENGINE=SILICONFLOW           # 图谱引擎 (实体关系抽取)

# ==========================================
# 4. Neo4j 图数据库
# ==========================================
NEO4J_URI=bolt://localhost:17687
NEO4J_USER=neo4j
NEO4J_PASSWORD=bysidescheme
NEO4J_DATABASE=neo4j
```

### 5. 启动服务

```bash
uv run main.py
```

服务启动后：
- **API 服务**: `http://localhost:8001`
- **API 文档 (Swagger)**: `http://localhost:8001/docs`

## 目录结构

```
BySideScheme_backend/
├── docker-compose.yml  # Neo4j 容器编排
├── data/               # [自动生成] 本地数据存储
│   ├── app.db          # SQLite: 局势、画像版本等结构化数据
│   ├── history.db      # Mem0: 记忆操作日志
│   ├── qdrant/         # Qdrant: 向量数据库文件
│   └── neo4j/          # Neo4j: 图数据库文件 (Docker 挂载)
│       ├── data/
│       └── logs/
├── logs/               # [自动生成] 系统运行日志
├── src/
│   ├── api/
│   │   ├── main.py         # FastAPI 应用 & ServiceContainer
│   │   ├── schemas.py      # Pydantic 请求/响应模型
│   │   ├── security.py     # API Key 鉴权
│   │   └── routers/
│   │       ├── simulator.py    # 多智能体模拟 API
│   │       ├── feedback.py     # 用户反馈 API
│   │       └── graph.py        # 知识图谱 API
│   ├── core/
│   │   ├── llm_client.py       # LLM 客户端工厂 (多引擎)
│   │   ├── memory.py           # Mem0 记忆管理器
│   │   ├── database.py         # SQLite 数据库管理
│   │   ├── neo4j_client.py     # Neo4j 连接管理器
│   │   ├── graph_engine.py     # 图谱引擎 (抽取/合并/查询)
│   │   ├── decision.py         # 决策引擎 (5维判断)
│   │   ├── generator.py        # 叙事生成器 (三层输出)
│   │   ├── simulator_insights.py  # 模拟洞察分析
│   │   ├── situation.py        # 局势数据模型
│   │   ├── prompt_loader.py    # YAML Prompt 加载器
│   │   └── logger.py           # 日志配置
│   ├── services/
│   │   └── advisor.py          # 策略顾问服务 (编排核心)
│   ├── autogen_agents/
│   │   ├── factory.py          # AutoGen Agent 工厂
│   │   └── agents.py           # Agent 定义
│   └── prompts/                # YAML Prompt 模板
│       ├── decision.yaml       # 决策判断 Prompt
│       ├── narrative.yaml      # 叙事生成 Prompt
│       ├── simulator.yaml      # 模拟分析 Prompt
│       └── graph.yaml          # 实体关系抽取 Prompt
├── main.py             # 程序入口
├── requirements.txt    # 依赖列表
└── .env                # [必须] 环境变量配置文件
```

## 数据流

### 事实输入流 (写入图谱 + 记忆)

```
用户事实 → AdvisorService
  ├─ 读取: 记忆上下文 (Mem0) + 图谱上下文 (Neo4j) + 局势 (SQLite)
  ├─ 决策: DecisionEngine (5维判断)
  ├─ 生成: NarrativeGenerator (三层叙事)
  ├─ 写入记忆: Mem0 (叙事/政治/承诺记忆)
  └─ 写入图谱: GraphEngine → LLM抽取 → Neo4j MERGE
```

### 模拟器流 (只读图谱，不写入)

```
模拟请求 → AutoGen 多智能体对话
  ├─ 读取: 图谱上下文 (Neo4j, 只读)
  ├─ 执行: 多角色对话模拟
  ├─ 分析: SimulatorInsightsEngine
  └─ 输出: 局势洞察 + 风险评估 + 人设校准
```

## API 概览

| 模块 | 端点 | 说明 |
|------|------|------|
| 局势 | `POST /situation/update` | 更新用户局势模型 |
| 局势 | `GET /situation/{user_id}` | 获取当前局势 |
| 策略 | `POST /advice/generate` | 输入事实，生成策略建议 |
| 记忆 | `GET /memory/{user_id}/all` | 获取所有记忆 |
| 记忆 | `POST /memory/{user_id}/consolidate` | 记忆整理归纳 |
| 图谱 | `GET /graph/{user_id}` | 获取完整图谱数据 |
| 图谱 | `GET /graph/{user_id}/entity/{name}` | 实体邻域查询 |
| 图谱 | `POST /graph/{user_id}/extract` | 手动触发实体抽取 |
| 图谱 | `GET /graph/{user_id}/insights` | 图谱洞察分析 |
| 图谱 | `GET /graph/{user_id}/changes` | 近期变化检测 |
| 模拟 | `POST /simulator/start` | 初始化模拟会话 |
| 模拟 | `POST /simulator/chat` | 发送模拟消息 |
| 模拟 | `POST /simulator/jobs/run` | 异步场景推演 |
| 反馈 | `POST /feedback/submit` | 提交建议反馈 |

完整 API 文档参考：[API_REFERENCE.md](../API_REFERENCE.md) 或启动后访问 `/docs`。

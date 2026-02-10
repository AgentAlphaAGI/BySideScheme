# 来事儿 (Lai Shi Er) - 您的职场智能军师 🧠💼

> **"职场如战场，不仅要会做事，更要会‘来事儿’。"**

**来事儿** 是一个基于 AI 的职场辅助系统，旨在帮助用户在复杂的职场环境中进行**局势分析**、**策略制定**和**话术生成**。它不仅仅是一个简单的问答机器人，而是一个具备**长期记忆**、**局势感知**和**政治智慧**的智能 Agent。

## ✨ 核心功能

*   **🏢 局势建模 (Situation Modeling)**
    *   数字化用户的职场画像（职级、晋升窗口、当前阶段）。
    *   **[New] 多角色干系人分析 (Stakeholders)**：支持定义多个关键角色（如直属老板、Skip Manager、竞争对手），并配置其风格（如“风险厌恶型”）、关系状态（如“猜忌”）及影响力，AI 将综合考虑多方利益进行博弈分析。
    *   基于局势动态调整 AI 的决策逻辑（如：在“观察期”偏向保守，在“冲刺期”偏向激进）。

*   **🗣️ 策略与话术生成 (Strategy & Narrative)**
    *   输入今日事实（如：“项目延期了”），AI 自动生成三层输出：
        1.  **对上版本**：政治正确、情绪稳定、不仅是汇报更是管理老板预期。
        2.  **自我版本**：还原真相、记录风险、不仅是记录更是复盘。
        3.  **策略提示**：下一步行动建议。

*   **🧠 智能记忆系统 (Intelligent Memory)**
    *   **多维记忆**：自动分类存储“叙事记忆”、“政治记忆（关系/风险）”、“状态记忆”和“承诺记忆”。
    *   **长期洞察**：具备记忆整理功能，能从零散的日常记录中提炼出长期模式（如：“老板周一情绪通常不稳定”）。
    *   **本地持久化**：使用 `mem0` + `Qdrant` (向量) + `SQLite` (关系数据)，数据完全掌握在自己手中。

*   **🔒 隐私与本地优先**
    *   核心数据存储在本地 `data/` 目录。
    *   支持接入 OpenAI 兼容接口（如 SiliconFlow / DeepSeek），灵活切换模型。

## 🛠️ 技术栈

*   **Backend**: Python 3.10+, FastAPI
*   **LLM Integration**: OpenAI SDK (Compatible with SiliconFlow/DeepSeek/GLM)
*   **Memory**: [Mem0](https://github.com/mem0ai/mem0) (The Memory Layer for AI Apps)
*   **Vector Store**: Qdrant (Local Mode)
*   **Database**: SQLite
*   **Logging**: Python standard logging (RotatingFileHandler)

## 🚀 快速开始

### 1. 环境准备 (使用 uv)

本项目推荐使用 [uv](https://github.com/astral-sh/uv) 进行极速依赖管理和构建。

```bash
# 1. 安装 uv (如果尚未安装)
pip install uv
# 或 macOS: brew install uv
# 或 Linux/WSL: curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 进入项目目录
cd BySideScheme_backend

# 3. 创建虚拟环境 (速度极快)
uv venv
```

### 2. 安装依赖

```bash
# 激活虚拟环境
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 安装依赖
uv pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填入 API Key。

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# 推荐使用 SiliconFlow (硅基流动) 提供的模型服务
SILICONFLOW_API_KEY=sk-your-key-here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Pro/zai-org/GLM-4.7  # 或 Qwen/Qwen2.5-72B-Instruct

# 如果没有 SiliconFlow，也可以使用 OpenAI
# OPENAI_API_KEY=sk-xxx
```

### 4. 启动服务

```bash
# 方式一：在激活的虚拟环境中
python main.py

# 方式二：使用 uv 直接运行 (无需手动激活)
uv run main.py
```
服务默认运行在 `http://localhost:8001`。

## 🎮 试用指南 (Demo Scenarios)

### 方法一：一键体验脚本 (推荐)

我们提供了一个 Python 脚本，可以自动执行完整的演示流程。

```bash
# 确保服务已启动
python demo_script.py
```

脚本将自动模拟：
1.  设定一个“P6 冲 P7”的职场局势。
2.  **Day 1**: 汇报项目延期（埋下伏笔）。
3.  **Day 2**: 应对老板责难（触发记忆联动）。
4.  **复盘**: 自动提取长期洞察。

### 方法二：手动 API 调用

以下脚本可用于模拟一个真实的职场场景，体验系统的**记忆联动**和**局势感知**能力。

### 场景设定：晋升期的 P6 vs 风险厌恶型老板

**用户 ID**: `demo_user_001`

#### 1. 初始化局势 (Setup Situation)

首先告诉系统你的当前状态：处于晋升窗口期，老板不喜欢风险。

```bash
curl -X POST "http://localhost:8001/situation/update" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "situation": {
      "career_type": "互联网大厂",
      "current_level": "P6",
      "target_level": "P7",
      "promotion_window": true,
      "boss_style": "风险厌恶型",
      "current_phase": "冲刺期",
      "personal_goal": "建立靠谱人设，争取晋升",
      "recent_events": []
    }
  }'
```

#### 2. 第一天：建立防御基线 (Day 1)

**事件**：项目因为第三方原因延期了，你需要汇报，但不能背锅。

```bash
curl -X POST "http://localhost:8001/advice/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "fact": "项目A因为第三方API不稳定导致延期1天，但我上周五已经在周报里提示过这个风险了。"
  }'
```

> **预期效果**：系统会建议你强调“风险已预警”，并生成话术：“正如上周五周报所述...”。系统会自动记下这个策略。

#### 3. 第二天：遭遇责难 (Day 2)

**事件**：老板在会上发火了，觉得项目失控。

```bash
curl -X POST "http://localhost:8001/advice/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "fact": "今天早会老板因为项目A延期发火了，说进度不可控。"
  }'
```

> **预期效果**：系统会检索到昨天的记忆（你已经预警过），建议你**不要当众辩解**，而是会后私发证据（周报截图），话术会非常委婉地“提醒”老板。

#### 4. 触发记忆整理 (Consolidation)

一周结束后，让系统总结这周的经验。

```bash
curl -X POST "http://localhost:8001/memory/demo_user_001/consolidate"
```

> **预期效果**：系统会生成一条长期洞察，例如：*“老板对进度延期极度敏感，对于非自身原因的延期，必须在前一周五留下书面预警证据，且在事发后通过私下渠道同步，避免公开对抗。”*

#### 5. 查看所有记忆

```bash
curl "http://localhost:8001/memory/demo_user_001/all"
```

## 📖 API 概览

详细接口文档请参考 [API_REFERENCE.md](./API_REFERENCE.md)。

| 方法 | 路径 | 描述 |
| :--- | :--- | :--- |
| **POST** | `/situation/update` | 更新用户的职场局势（职级、老板风格等） |
| **GET** | `/situation/{user_id}` | 获取当前局势配置 |
| **POST** | `/advice/generate` | **核心接口**：输入今日事实，生成策略建议与话术 |
| **POST** | `/memory/query` | 检索相关记忆 |
| **POST** | `/memory/{user_id}/consolidate` | 触发长期记忆整理（提炼洞察） |
| **GET** | `/memory/{user_id}/all` | 查看所有记忆 |
| **DELETE** | `/memory/{user_id}/{id}` | 删除指定记忆 |

## 📂 目录结构

```
laishier-backend/
├── data/               # 本地数据存储 (自动生成)
│   ├── app.db          # SQLite 数据库: 存储用户局势 (Situation) 和结构化数据
│   ├── history.db      # Mem0 历史记录: 记录记忆操作的日志
│   └── qdrant/         # 向量数据库 (Vector Store): 存储记忆的语义向量 (Embeddings)
├── logs/               # 系统日志
├── src/
│   ├── api/            # FastAPI 路由与 Schema
│   ├── core/           # 核心逻辑 (Memory, Decision, Generator, Logger)
│   └── services/       # 业务逻辑编排
├── main.py             # 程序入口
├── requirements.txt    # 依赖列表
└── .env                # 配置文件
```

## 💾 数据存储详解 (Data Storage)

本项目坚持**隐私优先**，所有核心数据均存储在本地 `data/` 目录下，不依赖云端数据库。

1.  **`data/app.db` (SQLite)**
    *   **用途**：存储应用的业务数据，目前主要是用户的“局势模型” (Situation Model)。
    *   **内容**：包含用户的职级、老板风格、当前阶段等结构化 JSON 数据。这是 AI 进行决策的“前置上下文”。

2.  **`data/qdrant/` (Vector Store)**
    *   **用途**：向量数据库，是 AI 的“长期记忆体”。
    *   **内容**：当您输入事实或生成策略时，系统会将文本转化为高维向量 (Embeddings) 存入此处。
    *   **作用**：这使得系统能通过语义搜索（而非关键词匹配）找到相关的历史记忆。例如，搜索“老板发火”能关联到“上次项目延期”的记忆。

3.  **`data/history.db` (SQLite)**
    *   **用途**：Mem0 库的操作日志。
    *   **内容**：记录了每一条记忆的创建、修改和删除历史，用于追踪记忆的演变过程。

## 📝 开发日志

- [x] 搭建 FastAPI 框架
- [x] 集成 SiliconFlow LLM
- [x] 实现基于 Mem0 的本地记忆系统
- [x] 实现局势 (Situation) 持久化 (SQLite)
- [x] 实现记忆整理与洞察提取 (Consolidation)
- [x] 添加全链路日志监控

---
*Stay safe and prosper in your workplace.*

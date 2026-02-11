# 在旁术 (BySideScheme) - 后端服务

**在旁术** 的核心后端服务，基于 **FastAPI** + **AutoGen** + **Mem0** 构建，提供具备长期记忆与政治智慧的职场辅助能力。

## ✨ 核心能力

*   **RESTful API**: 提供标准的 HTTP 接口，供前端或其他客户端调用。
*   **多模型支持**: 兼容 OpenAI 协议，支持 DeepSeek (深度求索)、Qwen (通义千问)、GLM (智谱) 等主流大模型，可为不同角色指定不同模型。
*   **本地记忆**: 集成 `mem0` + `Qdrant`，实现数据的本地向量化存储与检索，保障隐私。
*   **流式响应**: 支持 SSE (Server-Sent Events) 与 WebSocket，实现打字机效果的实时对话体验。
*   **任务队列**: 异步处理长耗时推演任务，支持状态轮询与结果订阅。

## 🛠️ 技术栈

*   **Runtime**: Python 3.10+
*   **Framework**: FastAPI
*   **Agent Framework**: AutoGen
*   **Memory**: Mem0 (Local Vector Store with Qdrant)
*   **Database**: SQLite (Relational Data)
*   **Package Manager**: uv (Ultra-fast Python package installer)

## 🚀 快速开始

### 1. 环境准备 (使用 uv)

本项目推荐使用 [uv](https://github.com/astral-sh/uv) 进行极速依赖管理和构建。

```bash
# 1. 安装 uv (如果尚未安装)
pip install uv
# 或 macOS: brew install uv
# 或 Linux/WSL: curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 进入后端目录
cd BySideScheme_backend

# 3. 创建虚拟环境 (速度极快)
uv venv
```

### 2. 安装依赖

```bash
# 激活虚拟环境 (可选，uv run 可自动使用环境)
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate

# 安装依赖
uv pip install -r requirements.txt
```

### 3. 配置环境变量 (关键步骤)

复制 `.env.example` 为 `.env` 并填入必要的配置。**系统启动必须依赖此文件。**

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据你的需求配置模型服务：

```ini
# ==========================================
# 1. 基础安全配置 (可选)
# ==========================================
# API 访问密钥。设置后，前端请求 Header 必须携带 X-API-Key: your-secret-key
# 如果留空，则不开启鉴权（仅限本地开发使用）
LAISHIER_API_KEY=

# ==========================================
# 2. 模型引擎配置 (至少配置一组)
# ==========================================
# 支持配置多组引擎，前缀可自定义 (如 SILICONFLOW, DEEPSEEK, OPENAI)

# --- 引擎 A: SiliconFlow (推荐，集成 DeepSeek/Qwen 等) ---
SILICONFLOW_API_KEY=sk-your-siliconflow-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
# 推荐模型: deepseek-ai/DeepSeek-V3, Qwen/Qwen2.5-72B-Instruct
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3

# --- 引擎 B: OpenAI (可选) ---
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o

# ==========================================
# 3. 模块引擎映射
# ==========================================
# 指定系统的各个模块分别使用哪个引擎 (填上面的前缀，大写)

# 决策引擎 (Advisor): 用于生成策略、话术
DECISION_ENGINE=SILICONFLOW

# 叙事引擎 (Generator): 用于生成具体的回复文本
NARRATIVE_ENGINE=SILICONFLOW

# 洞察引擎 (Insights): 用于分析模拟器对话、提取风险
SIMULATOR_INSIGHTS_ENGINE=SILICONFLOW

# 默认引擎: 当未指定具体模型时使用
DEFAULT_LLM_ENGINE=SILICONFLOW
```

### 4. 启动服务

```bash
# 使用 uv 直接运行 (推荐)
uv run main.py

# 或手动激活环境后运行
# python main.py
```

服务启动后：
- **API 服务**: `http://localhost:8001`
- **API 文档 (Swagger)**: `http://localhost:8001/docs`

## 📂 目录结构

```
BySideScheme_backend/
├── data/               # [自动生成] 本地数据存储目录
│   ├── app.db          # SQLite: 存储用户局势、画像版本等结构化数据
│   ├── history.db      # Mem0: 记忆操作日志
│   └── qdrant/         # Qdrant: 向量数据库文件
├── logs/               # [自动生成] 系统运行日志
├── src/
│   ├── api/            # 路由定义 (Routes)
│   ├── core/           # 核心逻辑 (LLM Client, Memory Manager)
│   ├── services/       # 业务逻辑 (Simulator, Advisor)
│   └── models/         # Pydantic 数据模型
├── main.py             # 程序入口
├── requirements.txt    # 依赖列表
└── .env                # [必须] 环境变量配置文件
```

## 🧪 测试与验证

你可以使用提供的 Python 脚本进行全流程测试：

```bash
# 运行演示脚本
uv run demo_script.py
```

或者参考根目录下的 [API_REFERENCE.md](../API_REFERENCE.md) 使用 `curl` 或 Postman 进行手动测试。

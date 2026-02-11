# 在旁术 (BySideScheme) - 您的职场智能军师 🧠💼

> **"职场如战场，不仅要会做事，更要会‘在旁术’。"**

**BySideScheme** 是一个全栈 AI 职场辅助系统，旨在帮助用户在复杂的职场环境中进行**局势分析**、**策略制定**和**话术生成**。它不仅仅是一个简单的问答机器人，而是一个具备**长期记忆**、**局势感知**和**政治智慧**的智能 Agent。

## 🚀 核心特性

### 1. 🏢 全局势建模 (Situation Modeling)
数字化你的职场环境，支持**多维度角色 (Stakeholders)** 分析。不只是针对老板，还要看隔壁组长、大老板等复杂关系，综合博弈。
- 设定当前职级、晋升窗口期与核心目标。
- 定义关键干系人（Role/Style/Influence），AI 决策时会自动考量各方利益。

### 2. 🎭 沉浸式职场模拟器 (Simulator) [核心升级]
在真实汇报前，先在模拟器里演练一番。
- **多角色协同**: 支持同时配置多位领导 (Leaders) 和同事 (Colleagues)，每位角色可指定不同的模型引擎 (DeepSeek/Qwen/GLM 等) 以模拟不同性格与能力。
- **流式交互**: 采用 SSE 技术，实时看到 AI 扮演的“暴躁老板”或“甩锅同事”的思考过程与逐字回复。
- **实时洞察**: 侧边栏实时展示推演过程中的深层分析，包括风险评分、局势变化预警及画像校准建议。
- **版本回溯**: AI 人物的性格画像会随对话动态演进，支持查看演进历史并一键回滚。

### 3. 🗣️ 策略与话术生成 (Advisor)
针对同一事件，结合局势与记忆，生成三层输出：
- **对上汇报**: 政治正确，管理预期。
- **自我复盘**: 揭示真相，识别风险。
- **下一步策略**: 具体可执行的行动建议。

### 4. 🧠 智能长期记忆 (Long-term Memory)
记住你和老板的每一次互动，自动提炼长期洞察（Insights），越用越懂你。
- **自动记忆**: 决策过程中的关键信息自动存入向量库。
- **洞察提炼**: 定期将零散记忆整合成高维度的职场生存法则。

### 5. 🔒 隐私优先
核心数据（局势配置、记忆向量库、画像版本）完全本地化存储，拒绝云端泄露风险。

## 📂 项目结构

本项目包含前后端两个独立模块：

*   **[BySideScheme_backend](./BySideScheme_backend/)**: 
    *   后端核心服务。
    *   基于 **Python / FastAPI**，使用 **uv** 进行极速环境管理。
    *   核心引擎：**AutoGen** (多 Agent 协同) + **SiliconFlow/DeepSeek** (LLM)。
    *   包含 **Mem0 + Qdrant** 本地记忆系统、决策引擎。
    *   提供所有业务 API。

*   **[BySideScheme_web](./BySideScheme_web/)**: 
    *   前端用户界面。
    *   基于 **Vite + React + Tailwind CSS** 构建。
    *   提供直观的聊天交互、局势配置面板和记忆可视化。
    *   支持**赛博朋克风格**的沉浸式体验。

*   **[API_REFERENCE.md](./API_REFERENCE.md)**: 
    *   详细的后端 API 接口文档。

## 🛠️ 快速开始

请分别参考各子目录下的 README 文档进行安装和启动：

- **[后端启动指南](./BySideScheme_backend/README.md)** (推荐使用 `uv` 启动)
- **[前端启动指南](./BySideScheme_web/README.md)** (使用 `npm` 或 `pnpm`)

### 简易启动流程

**1. 启动后端**

```bash
cd BySideScheme_backend
# 确保已安装 uv
uv venv
# 首次运行需安装依赖
uv pip install -r requirements.txt
# 配置 .env (参考 .env.example)
# 启动服务
uv run main.py
```

**2. 启动前端**

```bash
cd BySideScheme_web
pnpm install
pnpm dev
```

访问 `http://localhost:5173` 即可开始体验。

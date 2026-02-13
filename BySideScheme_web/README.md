# 来事儿 (BySideScheme) - Web 前端

**来事儿** 职场策略助手的赛博朋克风格前端界面。基于 React + Vite + Tailwind CSS 构建，提供沉浸式的职场局势推演与策略辅助体验。

## ✨ 核心特性

### 🎭 职场模拟器 (Simulator) [核心升级]
基于多智能体 (Multi-Agent) 的沉浸式职场演练场。
- **多角色协同**: 支持同时配置多位领导 (Leaders) 和同事 (Colleagues)，每位角色可指定不同的模型引擎 (DeepSeek/Qwen/GLM 等) 以模拟不同性格与能力。
- **流式推演**: 采用 **SSE (Server-Sent Events)** 技术，实时展示 AI 角色的思考过程与逐字对话输出，体验更流畅。
- **实时洞察面板 (Analysis Panel)**: 侧边栏实时展示推演过程中的深层分析，包括：
    - 🛡️ **总体风险评分**: 动态仪表盘展示当前对话的风险等级。
    - 📈 **局势洞察**: 识别对话中隐含的局势变化。
    - ⚠️ **风险预警**: 实时捕捉潜在风险并提供缓解建议 (Mitigation)。
    - 🧠 **画像校准**: 自动检测人物行为偏差，实时更新人物画像。
- **画像演进与回溯**: 支持查看人物画像的演进历史记录，并可一键**回滚 (Rollback)** 到指定版本，方便探索不同可能。

### 🧠 策略顾问 (Advisor)
- 输入今日发生的职场事实，系统结合**当前局势 (Situation)** 和**长期记忆 (Memory)**，生成：
    - **决策判断**: 是否该说、时机选择、战略意图。
    - **三层话术**: “对上汇报版本”、“自我复盘版本”及“策略提示”。
    - **引用来源**: 展示决策背后引用的具体记忆与局势信息。

### 📝 记忆库 (Memory)
- 管理用户的长期职场记忆。
- 支持语义检索、删除。
- **智能整理 (Consolidation)**: 一键将近期的零散记忆提炼为高维度的洞察 (Insight) 并存入记忆库。

### 🏢 局势管理 (Situation)
- 结构化配置当前的职业环境、阶段、目标。
- **干系人管理 (Stakeholders)**: 详细定义关键人物的角色、行事风格、关系状态及影响力等级。

## 🛠 技术栈

- **框架**: React 18 + Vite
- **语言**: TypeScript
- **样式**: Tailwind CSS + 赛博朋克主题 (Neon UI)
- **图标**: Lucide React
- **动画**: Framer Motion
- **状态管理**: Zustand (带持久化)
- **API 通信**: Axios + EventSource (SSE)

## 🚀 快速开始

### 前置要求
- Node.js (v18+)
- pnpm (推荐) 或 npm
- [BySideScheme 后端服务](../BySideScheme_backend) (需运行在端口 8001)

### 安装

```bash
# 安装依赖
pnpm install
```

### 启动开发服务器

```bash
pnpm dev
```

应用将启动在 `http://localhost:5173`。

## 📂 项目结构

```
src/
├── components/           # 可复用 UI 组件
│   ├── AnalysisPanel.tsx      # [NEW] 模拟器实时洞察面板
│   ├── PersonaHistoryModal.tsx # [NEW] 画像历史回溯弹窗
│   ├── SituationForm.tsx      # 局势配置表单
│   └── Layout.tsx             # 全局布局
├── pages/                # 页面组件
│   ├── Simulator.tsx          # [UPDATED] 职场模拟器主页 (含 SSE 与多角色支持)
│   ├── Advisor.tsx            # 策略顾问页
│   ├── Memory.tsx             # 记忆库页
│   ├── Profile.tsx            # 个人中心页
│   └── Dashboard.tsx          # 首页仪表盘
├── services/             # API 客户端
│   └── api.ts                 # 后端接口封装 (含 Job 与 Stream 处理)
├── store/                # 全局状态 (Zustand)
├── types/                # TypeScript 类型定义
└── ...
```

## 🔌 后端集成

本项目预期 **来事儿后端 (BySideScheme Backend)** 运行在 `http://localhost:8001`。
请确保后端服务已启动，若开启了 API Key 鉴权，请在环境变量或配置中进行相应设置。

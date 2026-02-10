# 来事儿 (Lai Shi Er) - Web 前端

**来事儿** 职场策略助手的赛博朋克风格前端界面。

## 🛠 技术栈

- **框架**: React 18 + Vite
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **图标**: Lucide React
- **动画**: Framer Motion
- **状态管理**: Zustand (带持久化)
- **路由**: React Router DOM v6
- **HTTP 客户端**: Axios

## 🚀 快速开始

### 前置要求

- Node.js (v18+)
- pnpm (推荐) 或 npm

### 安装

```bash
# 安装依赖
pnpm install
```

### 启动开发服务器

```ba
```

应用将启动在 `http://localhost:5173`。

### 构建生产版本

```bash
pnpm build
```

## 📂 项目结构

```
src/
├── components/     # 可复用 UI 组件 (Layout 等)
├── pages/          # 页面组件 (Dashboard, Advisor, Memory, Profile)
├── services/       # API 客户端和服务函数
├── store/          # 全局状态管理 (Zustand)
├── types/          # TypeScript 类型定义
├── utils/          # 工具函数
├── App.tsx         # 主应用组件 (含路由)
├── main.tsx        # 入口文件
└── index.css       # 全局样式和 Tailwind 指令
```

## 🎨 UI/UX 特性

- **赛博朋克主题**: 默认暗色模式，搭配霓虹点缀。
- **玻璃拟态**: 半透明卡片和导航栏设计。
- **响应式设计**: 完美适配移动端和桌面端屏幕。
- **流畅动画**: 使用 Framer Motion 实现平滑的过渡和交互效果。

## 🔌 后端集成

本项目预期 **来事儿后端 (Lai Shi Er Backend)** 运行在 `http://localhost:8001`。
在使用本应用前，请确保已启动后端服务。

# 来事儿 (BySideScheme) 需求文档

## 1. 背景与目标

来事儿是一套"职场局势建模 + 知识图谱 + 长期记忆 + 策略/话术生成 + 多角色推演"的本地优先系统。用户在复杂职场环境中需要：
- 记录事实与上下文，形成可检索的长期记忆
- 从事实中自动抽取实体关系，构建动态职场局势图谱
- 在关键节点快速得到"对上话术/自我复盘/策略提示"
- 对多干系人（老板/总监/同事/竞争方等）进行推演与博弈分析
- 识别风险与局势变化，持续校准对关键人物的画像假设（并可回溯）

本需求文档以当前系统实现为基线，明确产品范围、核心能力、数据与接口、非功能要求与验收标准。

## 2. 产品范围

### 2.1 In Scope（当前范围）
- 局势建模：用户职级/晋升窗口/阶段/干系人（Stakeholders）管理
- 知识图谱：基于 Neo4j 的实体关系抽取与动态局势建模（仅用户事实写入，模拟器不写入）
- 核心建议：输入事实（fact），生成决策与三层话术（对上/对己/策略提示），同时更新图谱
- 长期记忆：多类别记忆写入、语义检索、全量查看、删除、整理提炼洞察
- 多角色模拟器：基于多智能体对话推演（支持动态人物加载，只读消费图谱上下文）
- 观察员洞察层：对推演对话进行结构化复盘（洞察/风险/画像偏差举证/下一步动作）
- 人物画像校准：在推演过程中根据行为偏差校准画像，支持持久化与版本回溯/回滚
- 任务化推演：支持 job_id/status/result
- 流式输出：SSE / WebSocket 订阅作业输出
- 图谱可视化：前端交互式力导向图，支持搜索/过滤/缩放/实体详情
- 安全：可选 API Key 鉴权（HTTP + WebSocket）
- 配置：通过环境变量选择不同引擎与模型

### 2.2 Out of Scope（暂不包含）
- 多实例分布式作业队列（Redis/Celery/RQ 等）与强一致 job 存储
- 完整 RBAC/多租户权限系统（当前为单一 API Key）
- 数据导入导出、审计报表、运营后台
- 图谱的时间线回放（历史快照对比）

## 3. 角色与使用场景

### 3.1 用户角色
- 普通用户：提交"今日事实"、维护局势、查看图谱、检索/整理记忆、运行推演、查看洞察
- 开发/自部署者：配置模型服务、部署 Neo4j、设置 API Key

### 3.2 典型场景
- 日报事实输入：项目延期、老板发火、资源争夺、跨团队冲突 → 自动构建局势图谱
- 图谱分析：查看关键人物关系网、识别风险关系、发现权力结构变化
- 晋升窗口策略：建立靠谱人设、风险预警证据链、关键干系人博弈
- 多领导会议推演：直属领导 vs 总监 vs 同事协作，基于图谱上下文模拟对话与反应
- 画像偏差校准：发现"老板行为与初始人格不一致"，系统举证并修正画像版本

## 4. 核心概念与数据模型

### 4.1 SituationModel（局势模型）
目的：为决策与生成提供结构化上下文。
字段：
- 职业环境、当前职级、目标职级
- 是否晋升窗口
- 当前阶段（观察/冲刺/平稳/动荡/攻坚等）
- 个人目标
- 干系人列表 Stakeholders：名称/角色/风格/关系状态/影响力等级

### 4.2 知识图谱（Neo4j）
目的：从用户输入的事实中自动抽取实体与关系，形成动态的职场局势地图。

**节点类型：**
- Person：人物（同事、上级、竞争对手等）
- Event：事件（会议、调整、冲突等）
- Project：项目/任务
- Resource：资源（预算、HC、设备等）
- Organization：组织单元（部门、团队、公司）

**关系类型：**
- Person ↔ Person：REPORTS_TO、ALLIES_WITH、COMPETES_WITH、TRUSTS、DISTRUSTS、INFLUENCES
- Person → Event：PARTICIPATED_IN、INITIATED、OPPOSED
- Person → Project：OWNS、WORKS_ON、SUPPORTS、BLOCKS
- Person → Resource：CONTROLS、COMPETES_FOR
- Person → Organization：BELONGS_TO、LEADS

**关系属性：**
- weight (float 0-1)：关系强度
- sentiment：positive / negative / neutral
- confidence (float 0-1)：判断信心度
- evidence：来源证据
- created_at / updated_at：时间戳

**数据流边界：**
- 写入：仅用户通过 `/advice/generate` 提交的事实触发 LLM 抽取并写入 Neo4j
- 模拟器不写入：多智能体模拟对话是"假设推演"，不进入图谱和记忆
- 模拟器只读：模拟器可读取图谱上下文作为背景信息

### 4.3 记忆模型（Mem0 + Qdrant + history.db）
目的：让系统具备长期一致性与可检索上下文。
类别：
- narrative：历史对上口径/叙事
- political：人际风险/偏好/政治判断
- career_state：阶段状态/加分项/扣分项
- commitment：承诺/待办/不确定表态
- insight：整理后的长期洞察

### 4.4 人物画像（Persona Version）
目的：对关键人物的"行为模型"进行版本化管理。
要求：
- 每次画像更新必须具备举证（对话证据）与"特质→行为"的论证链路
- 画像更新可持久化，后续会话可加载最新画像
- 支持版本列表与回滚（回滚写入新版本记录，保持可追溯）

### 4.5 作业（Job）
目的：把推演从同步阻塞改为后台执行，支持轮询/订阅/流式输出。
字段：
- job_id、status（pending/running/completed/failed）、error
- session_id（绑定推演会话）
- messages（增量累积）、analysis（完成时输出）

## 5. 功能需求（按模块）

### 5.1 局势管理
目标：用户可维护自己的局势配置，并被后续决策/推演/图谱复用。
需求：
- 更新局势（覆盖式写入）
- 获取局势（若不存在可返回默认 mock 以便快速试用）
- 删除/重置局势
验收：
- 写入后读取一致
- 未写入时返回可用的默认结构

### 5.2 核心建议（Advice）
目标：输入事实后输出"决策 + 三层话术 + 使用的上下文 + 图谱抽取结果"。
需求：
- 生成决策（是否该说、时机、对象、战略意图、影响等）
- 生成话术：
  - 对上版本（政治正确/管理预期）
  - 自我版本（真相/复盘/风险）
  - 策略提示（下一步动作）
- 注入图谱上下文：决策和生成均使用局势图谱中的人物关系、事件、项目等信息
- 自动记忆回写（当 should_say 为真时写入口径/策略摘要）
- 自动图谱更新：从事实中抽取实体关系，通过 MERGE 写入 Neo4j
验收：
- 返回结构稳定，包含 context_used（situation + memory + graph）
- 返回 graph_extracted（本次抽取的实体和关系）
- 记忆回写可在后续查询中检索到
- 图谱更新可在 `/graph/{user_id}` 中查看到

### 5.3 知识图谱
目标：构建并维护动态的职场局势图谱，支持可视化与分析。
需求：
- 获取完整图谱数据（节点 + 边，供前端可视化）
- 实体邻域查询（指定实体的 N 跳子图）
- 手动触发实体关系抽取（传入文本，写入图谱）
- 近期变化检测（新增实体/关系、权重变动）
- 图谱洞察分析（关键人物中心性、风险关系、近期变化）
- 清空图谱 / 删除指定实体
验收：
- 输入事实后，图谱节点和关系正确增长
- 重复输入同一实体时通过 MERGE 更新而非重复创建
- 图谱上下文在决策/生成 prompt 中被引用
- 前端可视化正确渲染节点和边

### 5.4 记忆管理
目标：支持长期记忆写入、语义检索与整理。
需求：
- 查询相关记忆（按类别返回）
- 获取所有记忆
- 删除单条/清空
- 记忆整理：将零散记忆提炼为 insight 并回写
验收：
- 查询结果随输入语义变化而变化（非关键词匹配）
- 整理输出写入 insight 类别且可回查

### 5.5 多角色模拟器（Simulator）
目标：用户可加载自定义人物，进行多角色对话推演（基于图谱上下文但不写回）。
需求：
- 会话创建、对话、重置
- 动态人物加载（people[] 推荐）
  - 支持 leader/colleague
  - 支持为人物指定 engine（deepseek/qwen3/glm 等），实现差异化与吞吐优化
- 支持传入 user_id/situation：用于把局势纳入分析与加载画像版本
- 读取图谱上下文作为模拟背景信息（只读，不写入）
验收：
- 不传 people 时兼容 leaders/colleagues/boss 旧字段
- people 可同时加载多类人物并参与对话
- 模拟器对话不产生记忆写入或图谱写入

### 5.6 观察员洞察层（Insights）
目标：对模拟对话进行结构化复盘，提升洞察力、风险判断、可解释性。
需求（analysis 输出）：
- situation_insights：局势变化与关键观察
- overall_risk_score：总体风险分（0-100）
- risks[]：风险条目（severity/trigger/impact/evidence/mitigation）
- persona_updates[]：
  - deviation_detected：是否偏差
  - observed_traits：观察到的特质
  - trait_behavior_chain：特质→行为论证链
  - evidence：证据（引用对话片段）
  - updated_persona + update_confidence：修正画像与置信度
- next_actions：下一步行动建议
- uncertainties：不确定点
验收：
- analysis 严格 JSON，可直接用于前端渲染与自动化后处理
- 风险条目包含可执行 mitigations

### 5.7 画像演进（持久化 + 回溯 + 回滚）
目标：让"人物画像修正"从 session 内行为升级为长期资产。
需求：
- 当偏差成立且置信度足够时：
  - 更新当前会话中该人物的 system_message
  - 写入 SQLite 版本表（user_id + person_name）
- 支持版本列表查询
- 支持回滚到指定版本（写入新版本记录，便于审计）
验收：
- 新会话启动时，若传 user_id，应加载 latest persona 覆盖初始 persona
- 回滚后最新 persona 变为指定版本内容

### 5.8 任务化推演与流式输出
目标：支撑长耗时推演与 UI 实时展示，不阻塞请求线程。
需求：
- Job 启动：chat job / run job
- Job 查询：status、result（累计 messages + 最终 analysis）
- SSE：事件类型 status/message/analysis/done
- WebSocket：事件类型 status/message/analysis/error/done
验收：
- 作业运行时 result.messages 会逐步增加
- SSE/WS 订阅能收到增量消息并最终收到 analysis

### 5.9 图谱可视化（前端）
目标：以交互式力导向图展示职场局势图谱。
需求：
- 使用 react-force-graph-2d 渲染力导向图
- 节点按类型着色（Person=青, Event=橙, Project=绿, Resource=紫, Organization=红）
- 边按 sentiment 着色（positive=绿, negative=红, neutral=灰），粗细反映 weight
- 点击节点弹出详情面板（属性、关系列表、证据引用）
- 搜索栏：按名称搜索实体
- 类型过滤器：按节点类型筛选显示
- 缩放控制：放大/缩小/适应窗口
- 图谱洞察面板：关键人物、风险关系、近期变化
- 赛博朋克视觉风格与现有 UI 一致
验收：
- 节点和边正确渲染，颜色与类型对应
- 点击节点展示详情并可跳转到关联实体
- 搜索和过滤功能正常工作

### 5.10 安全与隐私
目标：保证"默认本地优先"，并避免被外部滥用。
需求：
- 可选 API Key 鉴权（HTTP + WS）
- 不在日志中输出密钥
- 数据落盘位置明确（data/ + logs/），默认加入 gitignore
- Neo4j 数据持久化到 data/neo4j/（Docker 挂载）
验收：
- 错误码一致（401）
- WS 未携带 key 时拒绝连接

## 6. 技术架构

### 6.1 后端技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| Runtime | Python 3.10+ | 服务运行时 |
| Framework | FastAPI | REST API 框架 |
| Agent Framework | AutoGen 0.2.35 | 多智能体对话模拟 |
| Memory | Mem0 + Qdrant | 本地向量化记忆存储与检索 |
| Graph Database | Neo4j 5 (Docker) | 实体关系图谱存储与查询 |
| Relational DB | SQLite | 局势/画像版本/反馈等结构化数据 |
| Package Manager | uv | 依赖管理 |

### 6.2 前端技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| Framework | React 18 + TypeScript | UI 框架 |
| Build Tool | Vite | 构建工具 |
| Styling | Tailwind CSS | 赛博朋克主题样式 |
| State | Zustand | 状态管理 |
| Graph Viz | react-force-graph-2d | 力导向图可视化 |
| Animation | Framer Motion | 过渡动画 |
| HTTP Client | Axios | API 通信 |

### 6.3 模型服务配置
- 支持 SiliconFlow / OpenAI 兼容接口
- 支持 DeepSeek、Qwen、GLM 等多模型混用
- 支持为不同模块指定不同引擎：
  - DECISION_ENGINE：决策引擎
  - NARRATIVE_ENGINE：叙事生成引擎
  - SIMULATOR_INSIGHTS_ENGINE：模拟洞察引擎
  - GRAPH_ENGINE：图谱实体关系抽取引擎
- 支持为不同模拟角色指定不同 engine

### 6.4 环境变量

| 变量 | 说明 |
|------|------|
| BySideScheme_API_KEY | 可选 API 访问密钥 |
| DECISION_ENGINE | 决策层引擎前缀 |
| NARRATIVE_ENGINE | 叙事层引擎前缀 |
| SIMULATOR_INSIGHTS_ENGINE | 洞察层引擎前缀 |
| GRAPH_ENGINE | 图谱引擎前缀 |
| {ENGINE}_API_KEY | 引擎 API Key |
| {ENGINE}_BASE_URL | 引擎 Base URL |
| {ENGINE}_MODEL | 引擎模型名 |
| NEO4J_URI | Neo4j Bolt 连接地址 |
| NEO4J_USER | Neo4j 用户名 |
| NEO4J_PASSWORD | Neo4j 密码 |
| NEO4J_DATABASE | Neo4j 数据库名 |

## 7. 非功能需求

### 7.1 性能与并发
- 单次推演可能耗时较长，需支持后台作业与流式输出
- HTTP handler 不应长时间阻塞事件循环
- Neo4j 查询应有索引支撑（user_id 索引 + 复合唯一性约束）

### 7.2 可观测性
- 日志应包含 request/模块关键节点（启动、推演、图谱抽取、作业状态变更、错误）
- 不记录敏感信息

### 7.3 可维护性
- Prompt 以 YAML 形式管理（decision.yaml、narrative.yaml、simulator.yaml、graph.yaml）
- 数据模型与接口契约稳定（向后兼容）
- GraphEngine 优雅降级：Neo4j 未配置时系统仍正常运行（图谱功能跳过）

### 7.4 可扩展性
- 图谱节点类型和关系类型在代码中以常量定义，便于扩展
- 新增实体/关系类型只需更新常量集合和 Prompt 模板

## 8. 接口与契约

接口定义与请求/响应示例以 API 文档为准：
- [API_REFERENCE.md](./API_REFERENCE.md)

## 9. 验收标准

### 最小验收用例

1. 设置局势后，`/advice/generate` 输出包含 `context_used.situation`、`context_used.graph` 且合理引用
2. 输入事实后，`graph_extracted` 包含合理的实体和关系
3. `GET /graph/{user_id}` 返回的节点和关系数量随事实输入增长
4. 图谱中相同实体通过 MERGE 合并而非重复创建
5. 写入的自动记忆可被 `/memory/query` 检索到
6. 模拟器对话不产生图谱写入（验证：模拟前后图谱节点数不变）
7. `GET /graph/{user_id}/insights` 返回关键人物列表和风险关系
8. `GET /graph/{user_id}/changes` 返回近期图谱变化
9. 前端图谱页面正确渲染节点（按类型着色）和边（按情感着色）
10. 点击节点展示详情面板，搜索和过滤功能正常
11. `simulator/start` 传 people 可加载 leader+colleague 并产生对话
12. `simulator/chat` 返回 analysis（含 risks/persona_updates/next_actions）
13. `simulator/jobs/chat` 创建 job，status 从 pending→running→completed
14. SSE 订阅能收到 message 事件与最终 analysis
15. persona versions 可列出，rollback 后 latest persona 变为回滚内容
16. 配置 `BySideScheme_API_KEY` 后，未带 header 的请求被拒绝（401）
17. Neo4j 未启动时，系统仍能正常运行（图谱功能优雅降级）

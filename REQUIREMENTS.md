# 在旁术 (BySideScheme)需求文档（基于现有后端设计）

## 1. 背景与目标

在旁术是一套“职场局势建模 + 长期记忆 + 策略/话术生成 + 多角色推演”的本地优先系统。用户在复杂职场环境中需要：
- 记录事实与上下文，形成可检索的长期记忆
- 在关键节点快速得到“对上话术/自我复盘/策略提示”
- 对多干系人（老板/总监/同事/竞争方等）进行推演与博弈分析
- 识别风险与局势变化，持续校准对关键人物的画像假设（并可回溯）

本需求文档以当前后端实现为基线，明确产品范围、核心能力、数据与接口、非功能要求与验收标准。

## 2. 产品范围

### 2.1 In Scope（本期范围）
- 局势建模：用户职级/晋升窗口/阶段/干系人（Stakeholders）管理
- 核心建议：输入事实（fact），生成决策与三层话术（对上/对己/策略提示）
- 长期记忆：多类别记忆写入、语义检索、全量查看、删除、整理提炼洞察
- 多角色模拟器：基于多智能体对话推演（支持动态人物加载）
- 观察员洞察层：对推演对话进行结构化复盘（洞察/风险/画像偏差举证/下一步动作）
- 人物画像校准：在推演过程中根据行为偏差校准画像，支持持久化与版本回溯/回滚
- 任务化推演：支持 job_id/status/result
- 流式输出：SSE / WebSocket 订阅作业输出（单会话内）
- 安全：可选 API Key 鉴权（HTTP + WebSocket）
- 配置：通过环境变量选择不同引擎（SiliconFlow/OpenAI 兼容）与不同模型

### 2.2 Out of Scope（暂不包含）
- 多实例分布式作业队列（Redis/Celery/RQ 等）与强一致 job 存储
- Web 前端/移动端 UI 设计与实现细节（仅后端接口契约）
- 完整 RBAC/多租户权限系统（当前为单一 API Key）
- 数据导入导出、审计报表、运营后台

## 3. 角色与使用场景

### 3.1 用户角色
- 普通用户：提交“今日事实”、维护局势、检索/整理记忆、运行推演、查看洞察
- 开发/自部署者：配置模型服务、部署运行、设置 API Key、防止外部滥用

### 3.2 典型场景
- 日报事实输入：项目延期、老板发火、资源争夺、跨团队冲突
- 晋升窗口策略：建立靠谱人设、风险预警证据链、关键干系人博弈
- 多领导会议推演：直属领导 vs 总监 vs 同事协作，模拟对话与反应
- 画像偏差校准：发现“老板行为与初始人格不一致”，系统举证并修正画像版本

## 4. 核心概念与数据模型

### 4.1 SituationModel（局势模型）
目的：为决策与生成提供结构化上下文，避免“只看一句话就输出”。
字段（概念级）：
- 职业环境、当前职级、目标职级
- 是否晋升窗口
- 当前阶段（观察/冲刺/平稳/动荡等）
- 个人目标
- 干系人列表 Stakeholders：
  - 名称/角色/风格/关系状态/影响力等级

### 4.2 记忆模型（Mem0 + Qdrant + history.db）
目的：让系统具备长期一致性与可检索上下文。
类别（概念级）：
- narrative：历史对上口径/叙事
- political：人际风险/偏好/政治判断
- career_state：阶段状态/加分项/扣分项
- commitment：承诺/待办/不确定表态
- insight：整理后的长期洞察

### 4.3 人物画像（Persona Version）
目的：对关键人物的“行为模型”进行版本化管理。
要求：
- 每次画像更新必须具备举证（对话证据）与“特质→行为”的论证链路
- 画像更新可持久化，后续会话可加载最新画像
- 支持版本列表与回滚（回滚本质为写入新的版本记录，保持可追溯）

### 4.4 作业（Job）
目的：把推演从同步阻塞改为后台执行，支持轮询/订阅/流式输出。
字段（概念级）：
- job_id、status（pending/running/completed/failed）、error
- session_id（绑定推演会话）
- messages（增量累积）、analysis（完成时输出）

## 5. 功能需求（按模块）

### 5.1 局势管理
目标：用户可维护自己的局势配置，并被后续决策/推演复用。
需求：
- 更新局势（覆盖式写入）
- 获取局势（若不存在可返回默认 mock 以便快速试用）
- 删除/重置局势
验收：
- 写入后读取一致
- 未写入时返回可用的默认结构

### 5.2 核心建议（Advice）
目标：输入事实后输出“决策 + 三层话术 + 使用的上下文”。
需求：
- 生成决策（是否该说、时机、对象、战略意图、影响等）
- 生成话术：
  - 对上版本（政治正确/管理预期）
  - 自我版本（真相/复盘/风险）
  - 策略提示（下一步动作）
- 自动记忆回写（当 should_say 为真时写入口径/策略摘要）
验收：
- 返回结构稳定，且包含 context_used（便于解释型 UI）
- 记忆回写可在后续查询中检索到

### 5.3 记忆管理
目标：支持长期记忆写入、语义检索与整理。
需求：
- 查询相关记忆（按类别返回）
- 获取所有记忆
- 删除单条/清空
- 记忆整理：将零散记忆提炼为 insight 并回写
验收：
- 查询结果随输入语义变化而变化（非关键词匹配）
- 整理输出写入 insight 类别且可回查

### 5.4 多角色模拟器（Simulator）
目标：用户可加载自定义人物，进行多角色对话推演。
需求：
- 会话创建、对话、重置
- 动态人物加载（people[] 推荐）
  - 支持 leader/colleague
  - 支持为人物指定 engine（deepseek/qwen3/glm 等），实现差异化与吞吐优化
- 支持传入 user_id/situation：用于把局势纳入分析与加载画像版本
验收：
- 不传 people 时兼容 leaders/colleagues/boss 旧字段
- people 可同时加载多类人物并参与对话

### 5.5 观察员洞察层（Insights）
目标：对模拟对话进行结构化复盘，提升“洞察力、风险判断、可解释性”。
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
- uncertainties：不确定点（说明缺少哪些信息）
验收：
- analysis 严格 JSON，可直接用于前端渲染与自动化后处理
- 风险条目包含可执行 mitigations

### 5.6 画像演进（持久化 + 回溯 + 回滚）
目标：让“人物画像修正”从 session 内行为升级为长期资产。
需求：
- 当偏差成立且置信度足够时：
  - 更新当前会话中该人物的 system_message（使后续推演按新画像继续）
  - 写入 SQLite 版本表（user_id + person_name）
- 支持版本列表查询
- 支持回滚到指定版本（回滚写入新版本记录，便于审计）
验收：
- 新会话启动时，若传 user_id，应加载 latest persona 覆盖初始 persona
- 回滚后最新 persona 变为指定版本内容

### 5.7 任务化推演与流式输出
目标：支撑长耗时推演与 UI 实时展示，不阻塞请求线程。
需求：
- Job 启动：
  - chat job：把一次 /chat 变为作业
  - run job：把一次 /run 变为作业
- Job 查询：
  - status：状态与时间戳
  - result：累计 messages + 最终 analysis
- SSE：
  - 事件：status/message/analysis/done
  - 可用于浏览器 EventSource / curl -N
- WebSocket：
  - 事件：status/message/analysis/error/done
  - 适合前端复杂交互
验收：
- 作业运行时 result.messages 会逐步增加
- SSE/WS 订阅能收到增量消息并最终收到 analysis

### 5.8 安全与隐私
目标：保证“默认本地优先”，并避免被外部滥用。
需求：
- 可选 API Key 鉴权：
  - 未设置 LAISHIER_API_KEY：不校验
  - 设置后：HTTP 与 WS 均需要 X-API-Key
- 不在日志中输出密钥
- 数据落盘位置明确（data/ + logs/），并默认加入 gitignore
验收：
- 错误码一致（401）
- WS 未携带 key 时拒绝连接

## 6. 配置与运行要求

### 6.1 模型服务（OpenAI 兼容）
要求：
- 支持 SiliconFlow/OpenAI 兼容接口
- 支持 DeepSeek (深度求索)、Qwen (通义千问)、GLM (智谱) 等多模型混用
- 支持为不同角色指定不同 engine 前缀环境变量（如 DEEPSEEK_*、QWEN3_*、GLM_*）

### 6.2 环境变量（概念）
- LAISHIER_API_KEY：可选 API 访问密钥
- DECISION_ENGINE：指定决策层（Advisor）使用的引擎前缀（默认：SILICONFLOW/OPENAI）
- NARRATIVE_ENGINE：指定话术生成层（Generator）使用的引擎前缀（默认：SILICONFLOW/OPENAI）
- SIMULATOR_INSIGHTS_ENGINE：指定洞察层使用的引擎前缀（默认：SILICONFLOW/OPENAI）
- {ENGINE}_API_KEY/{ENGINE}_BASE_URL/{ENGINE}_MODEL：多引擎角色配置
  - 例如：DEEPSEEK_API_KEY, QWEN3_MODEL 等

## 7. 非功能需求

### 7.1 性能与并发
- 单次推演可能耗时较长，需支持后台作业与流式输出
- HTTP handler 不应长时间阻塞事件循环

### 7.2 可观测性
- 日志应包含 request/模块关键节点（启动、推演、作业状态变更、错误）
- 不记录敏感信息（密钥、隐私内容可选择脱敏策略）

### 7.3 可维护性
- Prompt 以 YAML 形式管理，支持迭代
- 数据模型与接口契约稳定（向后兼容）

## 8. 接口与契约

接口定义与请求/响应示例以 API 文档为准：
- [API_REFERENCE.md](./API_REFERENCE.md)

## 9. 验收标准（可执行）

最小验收用例：
1. 设置局势后，advice/generate 输出包含 context_used.situation 且合理引用
2. 写入的自动记忆可被 memory/query 检索到
3. simulator/start 传 people 可加载 leader+colleague 并产生对话
4. simulator/chat 返回 analysis（含 risks/persona_updates/next_actions）
5. simulator/jobs/chat 创建 job，status 从 pending→running→completed，result.messages 逐步累积
6. SSE 订阅能收到 message 事件与最终 analysis
7. persona versions 可列出，rollback 后 latest persona 变为回滚内容
8. 配置 LAISHIER_API_KEY 后，未带 header 的 HTTP/WS 请求被拒绝


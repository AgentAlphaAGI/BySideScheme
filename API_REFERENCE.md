# 来事儿 (BySideScheme) API 文档

本文档详细描述了后端服务提供的所有 API 接口、请求参数及响应示例。

## 基础信息

- **Base URL**: `http://localhost:8001`
- **Content-Type**: `application/json`

## 鉴权（可选）

本服务支持可选的 API Key 鉴权：
- 若服务端未设置 `BySideScheme_API_KEY`（或为空），接口默认不校验鉴权
- 若服务端设置了 `BySideScheme_API_KEY`，则所有 HTTP 请求需要携带请求头 `X-API-Key: <BySideScheme_API_KEY>`，否则返回 401

WebSocket 也同样：握手阶段需携带 `X-API-Key`（当服务端开启校验时）。

## 通用错误格式

FastAPI 默认错误格式示例：

```json
{ "detail": "..." }
```

---

## 局势管理 (Situation)

### 1. 更新局势
**POST** `/situation/update`

用于初始化或更新用户的职场状态模型。这是系统进行决策的基础上下文。

**请求体 (JSON):**

```json
{
  "user_id": "demo_user",
  "situation": {
    "career_type": "央国企",
    "current_level": "科级干部",
    "target_level": "处级",
    "promotion_window": true,
    "stakeholders": [
      {
        "name": "王局建",
        "role": "部门总监",
        "style": "守成型",
        "relationship": "信任但有限",
        "influence_level": "High"
      },
      {
        "name": "李工",
        "role": "资深工程师",
        "style": "老黄牛型",
        "relationship": "友好",
        "influence_level": "Medium"
      }
    ],
    "current_phase": "攻坚期",
    "personal_goal": "确保系统验收，不仅要做，还要亮",
    "recent_events": []
  }
}
```

**响应示例:**

```json
{
  "message": "Situation updated successfully",
  "situation": { ... }
}
```

### 2. 获取局势
**GET** `/situation/{user_id}`

获取指定用户的当前局势配置。如果未设置，将返回系统默认的 Mock 数据。

### 3. 重置局势
**DELETE** `/situation/{user_id}`

删除用户的局势配置，恢复到初始状态。

---

## 策略与决策 (Advice)

### 4. 生成建议 (核心接口)
**POST** `/advice/generate`

输入今日发生的职场事实，系统结合局势、历史记忆和**局势图谱**，生成策略建议与话术。同时自动从事实中抽取实体关系，更新知识图谱。

**请求体 (JSON):**

```json
{
  "user_id": "demo_user",
  "fact": "今天上午部门例会上，王局建当众表扬了项目进度，但话锋一转说验收标准要从严。会后李工告诉我，陈副总上周单独找过王局建，提了安全合规方面的疑虑。"
}
```

**响应示例:**

```json
{
  "decision": {
    "should_say": true,
    "timing_check": "合适",
    "target_audience": "王局建，避开陈副总",
    "strategic_intent": "铺路",
    "future_impact": "为验收建立安全叙事",
    "strategy_summary": "主动向王局建汇报安全措施，化解陈副总的疑虑"
  },
  "narrative": {
    "boss_version": "领导，关于验收从严的指示已收到...",
    "self_version": "陈副总在背后施压安全问题...",
    "strategy_hints": "下一步：主动约陈副总展示安全架构"
  },
  "context_used": {
    "situation": "当前局势：央国企...",
    "memory": "[记忆库提取]...",
    "graph": "[局势图谱]\n> 关键人物:..."
  },
  "graph_extracted": {
    "entities": [
      {"name": "王局建", "type": "Person", "properties": {"role": "部门总监"}},
      {"name": "陈副总", "type": "Person", "properties": {"role": "分管安全"}},
      {"name": "部门例会", "type": "Event", "properties": {"description": "王局建表扬项目进度"}}
    ],
    "relations": [
      {"source": "陈副总", "target": "王局建", "type": "INFLUENCES", "properties": {"weight": 0.7, "sentiment": "negative"}},
      {"source": "王局建", "target": "部门例会", "type": "PARTICIPATED_IN", "properties": {"weight": 0.9}}
    ]
  }
}
```

---

## 知识图谱 (Graph)

基于 Neo4j 的职场局势知识图谱。仅用户通过 `/advice/generate` 输入的事实会自动触发实体关系抽取并写入图谱。多智能体模拟器的对话**不写入**图谱。

### 节点类型

| 类型 | 说明 | 典型属性 |
|------|------|----------|
| Person | 人物 | role, department, style, influence_level |
| Event | 事件 | description, date, significance |
| Project | 项目 | status, priority |
| Resource | 资源 | type, status |
| Organization | 组织 | type, level |

### 关系类型

| 关系 | 方向 | 说明 |
|------|------|------|
| REPORTS_TO | Person → Person | 汇报关系 |
| ALLIES_WITH | Person → Person | 盟友/合作 |
| COMPETES_WITH | Person → Person | 竞争关系 |
| TRUSTS | Person → Person | 信任 |
| DISTRUSTS | Person → Person | 不信任/猜忌 |
| INFLUENCES | Person → Person | 影响/施压 |
| PARTICIPATED_IN | Person → Event | 参与事件 |
| INITIATED | Person → Event | 发起事件 |
| OPPOSED | Person → Event | 反对事件 |
| OWNS | Person → Project | 负责项目 |
| WORKS_ON | Person → Project | 参与项目 |
| SUPPORTS | Person → Project | 支持项目 |
| BLOCKS | Person → Project | 阻碍项目 |
| CONTROLS | Person → Resource | 控制资源 |
| COMPETES_FOR | Person → Resource | 争夺资源 |
| BELONGS_TO | Person → Organization | 属于组织 |
| LEADS | Person → Organization | 领导组织 |

### 关系属性

所有关系均带以下属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| weight | float (0-1) | 关系强度 |
| sentiment | string | positive / negative / neutral |
| confidence | float (0-1) | 判断信心度 |
| evidence | string[] | 来源证据 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### 5. 获取完整图谱
**GET** `/graph/{user_id}`

返回用户的完整图谱数据，供前端力导向图可视化。

**响应示例:**

```json
{
  "nodes": [
    {
      "id": "4:abc:0",
      "name": "王局建",
      "type": "Person",
      "properties": {
        "name": "王局建",
        "role": "部门总监",
        "influence_level": "High",
        "style": "守成型",
        "created_at": "2026-02-13T07:00:00+00:00",
        "updated_at": "2026-02-13T08:30:00+00:00"
      }
    },
    {
      "id": "4:abc:1",
      "name": "陈副总",
      "type": "Person",
      "properties": {
        "name": "陈副总",
        "role": "分管运维与安全",
        "style": "保守派"
      }
    }
  ],
  "edges": [
    {
      "source": "4:abc:1",
      "target": "4:abc:0",
      "type": "INFLUENCES",
      "weight": 0.7,
      "sentiment": "negative",
      "confidence": 0.8,
      "evidence": ["陈副总上周单独找过王局建，提了安全合规方面的疑虑"]
    }
  ]
}
```

### 6. 获取实体邻域
**GET** `/graph/{user_id}/entity/{entity_name}?depth=2`

返回指定实体的 N 跳邻域子图。

**参数:**
- `entity_name` (path): 实体名称
- `depth` (query, 可选): 跳数深度，默认 2

**响应格式:** 同 `GET /graph/{user_id}`

### 7. 手动触发实体抽取
**POST** `/graph/{user_id}/extract`

手动提交文本，触发 LLM 实体关系抽取并写入图谱。

**请求体 (JSON):**

```json
{
  "text": "张副总今天主动约我喝茶，说他想把系统作为央企数字化转型的标杆案例上报集团。",
  "situation_context": "央国企，科级干部，攻坚期"
}
```

**响应示例:**

```json
{
  "message": "抽取完成：3 个实体，2 条关系",
  "extracted": {
    "entities": [
      {"name": "张副总", "type": "Person", "properties": {"role": "分管市场的副总"}},
      {"name": "数字化转型标杆案例", "type": "Event", "properties": {"description": "将系统上报集团宣传部"}},
      {"name": "集团", "type": "Organization", "properties": {"type": "上级单位"}}
    ],
    "relations": [
      {"source": "张副总", "target": "数字化转型标杆案例", "type": "INITIATED", "properties": {"weight": 0.8, "sentiment": "positive", "confidence": 0.9, "evidence": "张副总主动约我喝茶，说他想把系统作为标杆"}},
      {"source": "张副总", "target": "集团", "type": "BELONGS_TO", "properties": {"weight": 0.5, "sentiment": "neutral", "confidence": 0.6, "evidence": "上报集团宣传部"}}
    ]
  }
}
```

### 8. 获取近期图谱变化
**GET** `/graph/{user_id}/changes?hours=24`

检测最近 N 小时内的图谱变化（新增实体/关系、权重变动）。

**参数:**
- `hours` (query, 可选): 回溯小时数，默认 24

**响应示例:**

```json
[
  {
    "change_type": "new_entity",
    "description": "新增Person: 赵明",
    "timestamp": "2026-02-13T09:00:00+00:00"
  },
  {
    "change_type": "new_relation",
    "description": "新增关系: 赵明 -[COMPETES_WITH]-> 用户 (权重:0.6, 情感:negative)",
    "timestamp": "2026-02-13T09:00:00+00:00"
  },
  {
    "change_type": "updated_relation",
    "description": "关系更新: 陈副总 -[INFLUENCES]-> 王局建 (当前权重:0.8, 情感:negative)",
    "timestamp": "2026-02-13T10:00:00+00:00"
  }
]
```

### 9. 获取图谱洞察
**GET** `/graph/{user_id}/insights`

返回图谱分析洞察：关键人物（按连接度排序）、风险关系、近期变化。

**响应示例:**

```json
{
  "key_players": [
    {"name": "王局建", "centrality": 8},
    {"name": "张副总", "centrality": 5},
    {"name": "陈副总", "centrality": 4}
  ],
  "risk_relations": [
    {
      "source": "陈副总",
      "target": "搞了吗系统",
      "type": "BLOCKS",
      "weight": 0.7,
      "sentiment": "negative",
      "confidence": 0.8,
      "evidence": ["列了12条整改清单"]
    }
  ],
  "recent_changes": [
    {"description": "新增Person: 赵明", "timestamp": "2026-02-13T09:00:00+00:00"},
    {"description": "新增关系: 赵明 -[COMPETES_WITH]-> 用户", "timestamp": "2026-02-13T09:00:00+00:00"}
  ]
}
```

### 10. 清空图谱
**DELETE** `/graph/{user_id}`

清空该用户的全部图谱数据（所有节点和关系）。

**响应示例:**

```json
{
  "message": "用户 demo_user 的图谱数据已清空"
}
```

### 11. 删除指定实体
**DELETE** `/graph/{user_id}/entity/{entity_name}`

删除指定实体及其所有关联关系。

**响应示例:**

```json
{
  "message": "实体 '赵明' 及其关系已删除"
}
```

---

## 记忆管理 (Memory)

### 12. 查询记忆
**POST** `/memory/query`

根据语义检索相关的历史记忆。

**请求体 (JSON):**

```json
{
  "user_id": "demo_user",
  "query": "安全合规风险",
  "limit": 10
}
```

### 13. 获取所有记忆
**GET** `/memory/{user_id}/all`

按时间倒序返回该用户的所有记忆片段。

**响应示例:**

```json
{
  "memories": [
    {
      "id": "uuid-...",
      "memory": "陈副总对安全合规极度敏感...",
      "created_at": "2026-02-13T...",
      "metadata": {
        "category": "political",
        "risk_level": "low"
      }
    }
  ]
}
```

### 14. 触发记忆整理
**POST** `/memory/{user_id}/consolidate`

手动触发"长期记忆整理"。系统分析近期零散记忆，提炼出高维度的洞察（Insight）。

**响应示例:**

```json
{
  "message": "Consolidated 10 memories into 3 insights",
  "insights": [
    "陈副总在安全问题上具有一票否决权，应提前化解而非回避",
    "张副总是潜在盟友，但需注意刘总对其品牌战略的态度"
  ]
}
```

### 15. 删除记忆
**DELETE** `/memory/{user_id}/{memory_id}`

删除指定的单条记忆。

### 16. 清空记忆
**DELETE** `/memory/{user_id}`

清空该用户的所有记忆数据。

---

## 职场模拟器 (Simulator)

基于 AutoGen 多智能体框架，模拟真实的职场人际交互环境。模拟器**只读**消费图谱上下文作为背景信息，其产出**不写入**图谱和记忆库。

补充能力：
1. 可在 `people[].engine` 为不同人物指定不同模型（如 deepseek/qwen3/glm）
2. 若传入 `user_id`，系统会持久化"画像校准"，并在后续会话自动加载最新画像
3. 若传入 `situation` 或已保存局势，`analysis` 会把局势纳入风险与策略判断

### 数据结构说明

**人物配置（people）**

```json
{
  "kind": "leader",
  "name": "王局建",
  "title": "部门总监",
  "persona": "守成型，避免偏差，看重执行力。",
  "engine": "deepseek"
}
```

| 字段 | 说明 |
|------|------|
| kind | `"leader"` 或 `"colleague"` |
| name | 人物名称（对话标识、画像存取 key） |
| title | 头衔 |
| persona | 初始画像文本 |
| engine | 模型引擎名（可选，如 `"deepseek"` / `"qwen3"` / `"glm"`） |

### 17. 初始化模拟会话
**POST** `/simulator/start`

创建新的职场模拟环境。

**请求体 (JSON):**

```json
{
  "user_id": "demo_user_001",
  "user_name": "Me",
  "people": [
    {
      "kind": "leader",
      "name": "王局建",
      "title": "部门总监",
      "persona": "守成型，避免偏差，看重执行力，口头上强调'从严'。",
      "engine": "deepseek"
    },
    {
      "kind": "leader",
      "name": "陈副总",
      "title": "分管运维与安全",
      "persona": "保守派，一票否决权持有者，安全隐患会被无限放大。",
      "engine": "qwen3"
    }
  ]
}
```

**响应示例:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 18. 发送消息并获取回复
**POST** `/simulator/chat`

**请求体 (JSON):**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "各位领导，关于系统验收的安全架构，我做了专门的方案，想向大家汇报一下。"
}
```

**响应示例:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "new_messages": [
    {
      "sender": "王局建",
      "content": "好，你说说看，验收标准可不能打折扣。",
      "role": "assistant"
    },
    {
      "sender": "陈副总",
      "content": "安全方面我有几个问题，权限模块是怎么设计的？",
      "role": "assistant"
    }
  ],
  "analysis": {
    "situation_insights": ["陈副总对安全模块高度关注，需要准备详细的技术应答"],
    "overall_risk_score": 60,
    "risks": [
      {
        "title": "安全审查可能导致验收延期",
        "severity": "medium",
        "trigger": "无法充分回答陈副总的安全细节问题",
        "impact": "项目验收被推迟，影响晋升窗口",
        "evidence": ["陈副总: 安全方面我有几个问题"],
        "mitigation": ["准备权限模块架构图", "提前做安全渗透测试报告"]
      }
    ],
    "persona_updates": [],
    "next_actions": ["展示安全架构分层设计，用数据说话"],
    "uncertainties": []
  }
}
```

### 19. 重置会话
**DELETE** `/simulator/reset/{session_id}`

结束并清除指定的模拟会话。

### 20. 运行完整场景模拟
**POST** `/simulator/run`

一键运行完整的职场模拟场景，后台自动进行多轮对话推演。

**请求体 (JSON):**

```json
{
  "user_id": "demo_user_001",
  "user_name": "Me",
  "people": [
    {"kind": "leader", "name": "王局建", "title": "部门总监", "persona": "守成型", "engine": "deepseek"},
    {"kind": "leader", "name": "陈副总", "title": "分管安全", "persona": "保守派", "engine": "qwen3"}
  ],
  "scenario": "向领导汇报：系统验收前发现一个权限模块的潜在漏洞，已修复但需要说明情况。",
  "max_rounds": 10
}
```

**响应示例:**

```json
{
  "messages": [
    {"sender": "王局建", "content": "这个问题怎么到现在才发现？", "role": "assistant"},
    {"sender": "陈副总", "content": "安全问题必须零容忍。", "role": "assistant"}
  ],
  "analysis": {
    "overall_risk_score": 75,
    "risks": [],
    "persona_updates": [],
    "situation_insights": [],
    "next_actions": [],
    "uncertainties": []
  }
}
```

### 21. 启动单轮对话作业（异步）
**POST** `/simulator/jobs/chat`

将 `/simulator/chat` 变为后台作业。

**请求体 (JSON):**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "我想把验收时间提前一周，因为竞聘窗口可能提前。"
}
```

**响应示例:**

```json
{
  "job_id": "a2f7c0c0-1111-2222-3333-444455556666",
  "status": "pending",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1730000000.0,
  "updated_at": 1730000000.0
}
```

### 22. 启动完整场景作业（异步）
**POST** `/simulator/jobs/run`

等价于 `/simulator/run`，但以后台作业执行。

### 23. 查询作业状态
**GET** `/simulator/jobs/{job_id}/status`

### 24. 获取作业结果
**GET** `/simulator/jobs/{job_id}/result`

返回字段：
- `messages`: 已生成的消息（随作业运行逐步累积）
- `analysis`: 完成后的结构化洞察

### 25. SSE 流式订阅
**GET** `/simulator/jobs/{job_id}/stream`

返回 `text/event-stream`，事件类型：
- `status`: 作业状态变更
- `message`: 新消息
- `analysis`: 最终洞察
- `done`: 结束

```bash
curl -N "http://localhost:8001/simulator/jobs/<job_id>/stream"
```

### 26. WebSocket 流式订阅
**WS** `/simulator/jobs/{job_id}/ws`

消息格式：
- `{"type":"status","job_id":"...","status":"running"}`
- `{"type":"message","data":{...}}`
- `{"type":"analysis","data":{...}}`
- `{"type":"error","error":"..."}`
- `{"type":"done"}`

### 27. 列出画像版本
**GET** `/simulator/persona/{user_id}/{person_name}/versions?limit=50`

**响应示例:**

```json
{
  "versions": [
    {
      "id": "persona-version-id",
      "person_title": "部门总监",
      "persona": "更新后的画像...",
      "deviation_summary": "偏差举证与论证...",
      "confidence": 0.82,
      "created_at": "2026-02-13 11:00:00"
    }
  ]
}
```

### 28. 回滚到指定画像版本
**POST** `/simulator/persona/{user_id}/{person_name}/rollback`

**请求体 (JSON):**

```json
{
  "persona_version_id": "the-version-id-to-rollback"
}
```

**响应示例:**

```json
{
  "rolled_back_to": "the-version-id-to-rollback",
  "new_version_id": "new-version-id"
}
```

---

## 用户反馈 (Feedback)

### 29. 提交反馈
**POST** `/feedback/submit`

提交用户对系统生成建议的反馈。

**请求体 (JSON):**

```json
{
  "user_id": "demo_user",
  "fact": "部门例会上被表扬",
  "advice_result": { ... },
  "rating": 5,
  "comment": "策略建议很实用"
}
```

**响应示例:**

```json
{
  "message": "Feedback received",
  "id": "uuid-..."
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 401 | API Key 校验失败 |
| 422 | 参数格式错误（Pydantic 校验失败） |
| 500 | 服务端内部错误（LLM 调用失败、数据库错误等） |

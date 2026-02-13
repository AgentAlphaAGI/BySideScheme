from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.core.memory import MemoryManager
from src.core.decision import DecisionEngine
from src.core.generator import NarrativeGenerator
from src.services.advisor import AdvisorService
from src.api.schemas import FactInput, SituationUpdate, MemoryQuery
from src.core.situation import SituationModel, Stakeholder
from src.core.database import DatabaseManager
from src.core.logger import logger
from src.api.security import require_api_key
import os
from dotenv import load_dotenv
import logging

# Filter out the specific AutoGen warning about API key format
class APIKeyWarningFilter(logging.Filter):
    def filter(self, record):
        return "The API key specified is not a valid OpenAI format" not in record.getMessage()

logging.getLogger("autogen.oai.client").addFilter(APIKeyWarningFilter())

# 加载环境变量
load_dotenv()

from src.api.routers import simulator, feedback, graph

from contextlib import asynccontextmanager

# 依赖注入单例
class ServiceContainer:
    def __init__(self):
        self.memory_manager = None
        self.decision_engine = None
        self.narrative_generator = None
        self.advisor_service = None
        self.db = None
        self.graph_engine = None

    def initialize(self):
        logger.info("Initializing Services...")
        self.db = DatabaseManager()
        self.memory_manager = MemoryManager()
        self.decision_engine = DecisionEngine()
        self.narrative_generator = NarrativeGenerator()

        # 初始化图谱引擎（可选：如果 Neo4j 未配置则跳过）
        try:
            from src.core.neo4j_client import Neo4jClient
            from src.core.graph_engine import GraphEngine
            neo4j_client = Neo4jClient()
            self.graph_engine = GraphEngine(neo4j_client)
            logger.info("GraphEngine initialized successfully.")
        except Exception as e:
            logger.warning(f"GraphEngine initialization skipped (Neo4j may not be configured): {e}")
            self.graph_engine = None

        self.advisor_service = AdvisorService(
            self.memory_manager,
            self.decision_engine,
            self.narrative_generator,
            graph_engine=self.graph_engine
        )
        logger.info("Services Initialized.")

container = ServiceContainer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container.initialize()
    logger.info("Application startup complete.")
    yield
    # Shutdown
    if container.graph_engine:
        try:
            from src.core.neo4j_client import Neo4jClient
            Neo4jClient().close()
        except Exception:
            pass
    logger.info("Application shutdown.")

app = FastAPI(title="来事儿 (BySideScheme) API", version="1.0.0", lifespan=lifespan)

def _parse_cors_allow_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
    if not raw:
        return []
    if raw == "*":
        return ["*"]
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins

# 配置 CORS
allow_origins = _parse_cors_allow_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False if allow_origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册子路由
app.include_router(simulator.router, dependencies=[Depends(require_api_key)])
app.include_router(feedback.router, dependencies=[Depends(require_api_key)])
app.include_router(graph.router, dependencies=[Depends(require_api_key)])

def get_advisor_service():
    if not container.advisor_service:
        logger.error("Services not initialized when accessing advisor service.")
        raise HTTPException(status_code=500, detail="Services not initialized")
    return container.advisor_service

@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to BySideScheme API. Stay safe in the workplace!"}

@app.post("/situation/update")
async def update_situation(input_data: SituationUpdate, _: None = Depends(require_api_key)):
    """
    更新用户的职场局势模型
    """
    logger.info(f"Updating situation for user: {input_data.user_id}")
    container.db.save_situation(input_data.user_id, input_data.situation)
    return {"message": "Situation updated successfully", "situation": input_data.situation}

@app.get("/situation/{user_id}")
async def get_situation(user_id: str, _: None = Depends(require_api_key)):
    """
    获取用户的当前局势
    """
    logger.info(f"Fetching situation for user: {user_id}")
    situation = container.db.get_situation(user_id)
    if not situation:
        logger.warning(f"No situation found for user {user_id}, using default.")
        # 返回默认 Mock 局势方便测试
        return {
            "message": "No specific situation found, using default.",
            "situation": SituationModel(
                career_type="互联网大厂",
                current_level="P6",
                target_level="P7",
                promotion_window=True,
                stakeholders=[
                    Stakeholder(
                        name="默认老板",
                        role="直属上级",
                        style="风险厌恶型",
                        relationship="中立",
                        influence_level="High"
                    )
                ],
                current_phase="观察期",
                personal_goal="想拼一把冲一下",
                recent_events=[]
            )
        }
    return {"situation": situation}

@app.post("/advice/generate")
async def generate_advice(
    input_data: FactInput,
    service: AdvisorService = Depends(get_advisor_service),
    _: None = Depends(require_api_key),
):
    """
    核心接口：输入今日事实，生成策略建议
    """
    logger.info(f"Generating advice for user {input_data.user_id}. Fact: {input_data.fact[:30]}...")
    # 获取用户局势
    situation = container.db.get_situation(input_data.user_id)
    if not situation:
        logger.warning(f"No situation found for user {input_data.user_id}, using default for advice generation.")
        # 如果没有设置，使用默认配置 (或者报错)
        situation = SituationModel(
                career_type="互联网大厂",
                current_level="P6",
                target_level="P7",
                promotion_window=True,
                stakeholders=[
                    Stakeholder(
                        name="默认老板",
                        role="直属上级",
                        style="风险厌恶型",
                        relationship="中立",
                        influence_level="High"
                    )
                ],
                current_phase="观察期",
                personal_goal="想拼一把冲一下",
                recent_events=[]
            )
    
    try:
        result = service.process_daily_input(input_data.user_id, input_data.fact, situation)
        logger.info(f"Advice generated successfully for user {input_data.user_id}")
        return result
    except Exception as e:
        logger.error(f"Error generating advice for user {input_data.user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/query")
async def query_memory(input_data: MemoryQuery, _: None = Depends(require_api_key)):
    """
    查询用户记忆
    """
    query = input_data.query or "重要"
    logger.info(f"Querying memory for user {input_data.user_id}. Query: {query}")
    results = container.memory_manager.get_relevant_memories(
        input_data.user_id, 
        query, 
        limit_per_category=input_data.limit // 4
    )
    return results

@app.get("/memory/{user_id}/all")
async def get_all_memories(user_id: str, _: None = Depends(require_api_key)):
    """
    获取用户的所有记忆历史
    """
    logger.info(f"Fetching all memories for user {user_id}")
    memories = container.memory_manager.get_all_memories(user_id)
    return {"memories": memories}

@app.delete("/memory/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str, _: None = Depends(require_api_key)):
    """
    删除单条记忆
    """
    logger.info(f"Deleting memory {memory_id} for user {user_id}")
    container.memory_manager.delete_memory(memory_id)
    return {"message": f"Memory {memory_id} deleted"}

@app.delete("/memory/{user_id}")
async def delete_all_memories(user_id: str, _: None = Depends(require_api_key)):
    """
    清空用户的所有记忆
    """
    logger.info(f"Deleting all memories for user {user_id}")
    container.memory_manager.delete_all_memories(user_id)
    return {"message": f"All memories for user {user_id} deleted"}

@app.delete("/situation/{user_id}")
async def delete_situation(user_id: str, _: None = Depends(require_api_key)):
    """
    重置/删除用户局势
    """
    logger.info(f"Deleting situation for user {user_id}")
    container.db.delete_situation(user_id)
    return {"message": f"Situation for user {user_id} deleted"}

@app.post("/memory/{user_id}/consolidate")
async def consolidate_memories(user_id: str, _: None = Depends(require_api_key)):
    """
    触发记忆整理：将零散记忆归纳为长期洞察
    """
    logger.info(f"Consolidating memories for user {user_id}")
    # 1. 获取所有记忆
    raw_memories_data = container.memory_manager.get_all_memories(user_id)
    if not raw_memories_data:
        logger.info(f"No memories to consolidate for user {user_id}")
        return {"message": "No memories to consolidate", "insights": []}
    
    # 提取记忆文本
    raw_memories = [m.get("memory") for m in raw_memories_data]
    
    # 2. 调用 LLM 进行整理
    insights = container.narrative_generator.consolidate_memories(raw_memories)
    
    # 3. 将新洞察存回记忆库
    for insight in insights:
        container.memory_manager.add_insight_memory(user_id, insight)
    
    logger.info(f"Consolidated {len(raw_memories)} memories into {len(insights)} insights for user {user_id}")
    return {
        "message": f"Consolidated {len(raw_memories)} memories into {len(insights)} insights",
        "insights": insights
    }

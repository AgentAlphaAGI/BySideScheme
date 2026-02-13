from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from src.core.graph_engine import GraphEngine
from src.core.neo4j_client import Neo4jClient
from src.core.logger import logger

router = APIRouter(prefix="/graph", tags=["graph"])


# ------------------------------------------------------------------
# Request / Response schemas
# ------------------------------------------------------------------

class GraphExtractRequest(BaseModel):
    text: str = Field(..., description="待抽取实体关系的文本")
    situation_context: Optional[str] = Field(None, description="当前局势上下文（可选）")


class GraphNodeResponse(BaseModel):
    id: str
    name: str
    type: str
    properties: Dict[str, Any]


class GraphEdgeResponse(BaseModel):
    source: str
    target: str
    type: str
    weight: float
    sentiment: str
    confidence: float
    evidence: List[str]


class GraphDataResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]


class GraphChangeResponse(BaseModel):
    change_type: str
    description: str
    timestamp: str


class KeyPlayerResponse(BaseModel):
    name: str
    centrality: int


class GraphInsightsResponse(BaseModel):
    key_players: List[KeyPlayerResponse]
    risk_relations: List[GraphEdgeResponse]
    recent_changes: List[Dict[str, str]]


# ------------------------------------------------------------------
# Helper: 获取 GraphEngine 实例
# ------------------------------------------------------------------

def _get_graph_engine() -> GraphEngine:
    """
    从全局 ServiceContainer 获取 GraphEngine。
    在 main.py 的 lifespan 中初始化。
    """
    from src.api.main import container
    if not container.graph_engine:
        raise HTTPException(status_code=500, detail="GraphEngine not initialized")
    return container.graph_engine


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.get("/{user_id}", response_model=GraphDataResponse)
async def get_graph(user_id: str, engine: GraphEngine = Depends(_get_graph_engine)):
    """
    获取用户完整图谱数据（用于前端可视化）
    """
    logger.info(f"Fetching graph data for user {user_id}")
    try:
        data = engine.get_graph_data(user_id)
        return data
    except Exception as e:
        logger.error(f"Error fetching graph for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/entity/{entity_name}", response_model=GraphDataResponse)
async def get_entity_detail(
    user_id: str,
    entity_name: str,
    depth: int = 2,
    engine: GraphEngine = Depends(_get_graph_engine),
):
    """
    获取指定实体的邻域子图
    """
    logger.info(f"Fetching entity '{entity_name}' neighborhood for user {user_id} (depth={depth})")
    try:
        data = engine.get_entity_neighborhood(user_id, entity_name, depth=depth)
        return data
    except Exception as e:
        logger.error(f"Error fetching entity detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/extract")
async def extract_graph(
    user_id: str,
    request: GraphExtractRequest,
    engine: GraphEngine = Depends(_get_graph_engine),
):
    """
    手动触发实体关系抽取并写入图谱
    """
    logger.info(f"Manual graph extraction for user {user_id}, text length={len(request.text)}")
    try:
        extracted = engine.process_fact(
            user_id=user_id,
            fact=request.text,
            situation_context=request.situation_context or "",
        )
        return {
            "message": f"抽取完成：{len(extracted['entities'])} 个实体，{len(extracted['relations'])} 条关系",
            "extracted": extracted,
        }
    except Exception as e:
        logger.error(f"Error during graph extraction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/changes", response_model=List[GraphChangeResponse])
async def get_graph_changes(
    user_id: str,
    hours: int = 24,
    engine: GraphEngine = Depends(_get_graph_engine),
):
    """
    获取近期图谱变化
    """
    logger.info(f"Fetching graph changes for user {user_id} (last {hours}h)")
    try:
        changes = engine.detect_changes(user_id, hours=hours)
        return changes
    except Exception as e:
        logger.error(f"Error fetching graph changes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/insights", response_model=GraphInsightsResponse)
async def get_graph_insights(
    user_id: str,
    engine: GraphEngine = Depends(_get_graph_engine),
):
    """
    获取图谱洞察（关键人物、风险关系、近期变化）
    """
    logger.info(f"Fetching graph insights for user {user_id}")
    try:
        insights = engine.get_centrality_analysis(user_id)
        return insights
    except Exception as e:
        logger.error(f"Error fetching graph insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def clear_graph(
    user_id: str,
    engine: GraphEngine = Depends(_get_graph_engine),
):
    """
    清空用户的全部图谱数据
    """
    logger.info(f"Clearing all graph data for user {user_id}")
    try:
        engine.clear_graph(user_id)
        return {"message": f"用户 {user_id} 的图谱数据已清空"}
    except Exception as e:
        logger.error(f"Error clearing graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/entity/{entity_name}")
async def delete_entity(
    user_id: str,
    entity_name: str,
    engine: GraphEngine = Depends(_get_graph_engine),
):
    """
    删除指定实体及其所有关系
    """
    logger.info(f"Deleting entity '{entity_name}' for user {user_id}")
    try:
        engine.delete_entity(user_id, entity_name)
        return {"message": f"实体 '{entity_name}' 及其关系已删除"}
    except Exception as e:
        logger.error(f"Error deleting entity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

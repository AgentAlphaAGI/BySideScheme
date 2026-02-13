from typing import Dict, Any, Optional
from src.core.situation import SituationModel
from src.core.memory import MemoryManager
from src.core.decision import DecisionEngine
from src.core.generator import NarrativeGenerator
from src.core.graph_engine import GraphEngine
from src.core.logger import logger

class AdvisorService:
    def __init__(self, 
                 memory_manager: MemoryManager, 
                 decision_engine: DecisionEngine, 
                 narrative_generator: NarrativeGenerator,
                 graph_engine: Optional[GraphEngine] = None):
        self.memory_manager = memory_manager
        self.decision_engine = decision_engine
        self.narrative_generator = narrative_generator
        self.graph_engine = graph_engine

    def process_daily_input(self, user_id: str, fact: str, situation: SituationModel) -> Dict[str, Any]:
        """
        处理每日事实输入，生成建议和文案。
        仅用户输入的事实会触发图谱抽取和记忆更新。
        """
        logger.info(f"[{user_id}] Processing daily input: {fact[:50]}...")
        
        # 1. 准备上下文
        # 使用事实作为查询词来检索相关记忆
        memory_context = self.memory_manager.get_context_string(user_id, query=fact)
        situation_context = situation.to_prompt_context()

        # 1b. 获取图谱上下文（只读）
        graph_context = ""
        if self.graph_engine:
            try:
                graph_context = self.graph_engine.get_graph_context(user_id, query=fact)
                logger.debug(f"[{user_id}] Graph context retrieved ({len(graph_context)} chars)")
            except Exception as e:
                logger.warning(f"[{user_id}] Failed to get graph context: {e}")

        # 2. 决策阶段
        logger.debug(f"[{user_id}] Running decision engine...")
        decision = self.decision_engine.evaluate(
            fact, situation_context, memory_context, graph_context=graph_context
        )
        
        # 3. 生成阶段
        logger.debug(f"[{user_id}] Generating narratives...")
        narrative = self.narrative_generator.generate(
            fact, decision, situation_context, memory_context, graph_context=graph_context
        )

        # 4. 自动记忆更新 (如果是有效决策)
        if decision.get("should_say", False):
            # 记录生成的"官方说法"
            if narrative.get("boss_version"):
                self.memory_manager.add_narrative_memory(
                    user_id, 
                    f"关于'{fact[:10]}...'的说法: {narrative['boss_version']}", 
                    source="generated_advice"
                )
            
            # 记录策略
            if decision.get("strategy_summary"):
                self.memory_manager.add_political_memory(
                    user_id,
                    f"针对事件'{fact[:10]}...'的策略: {decision['strategy_summary']}"
                )
            logger.info(f"[{user_id}] Added new memories from generated advice.")

        # 5. 图谱抽取与更新（仅用户事实输入触发写入）
        graph_extracted = None
        if self.graph_engine:
            try:
                graph_extracted = self.graph_engine.process_fact(
                    user_id=user_id,
                    fact=fact,
                    situation_context=situation_context,
                )
                logger.info(
                    f"[{user_id}] Graph updated: "
                    f"{len(graph_extracted.get('entities', []))} entities, "
                    f"{len(graph_extracted.get('relations', []))} relations"
                )
            except Exception as e:
                logger.warning(f"[{user_id}] Graph extraction failed (non-critical): {e}")

        return {
            "decision": decision,
            "narrative": narrative,
            "context_used": {
                "situation": situation_context,
                "memory": memory_context,
                "graph": graph_context
            },
            "graph_extracted": graph_extracted
        }

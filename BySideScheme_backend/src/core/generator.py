import json
from src.core.prompt_loader import PromptLoader
from src.core.logger import logger
from src.core.llm_client import LLMClientFactory

class NarrativeGenerator:
    def __init__(self):
        self.client, self.model = LLMClientFactory.create_client("NARRATIVE_ENGINE")
        logger.info(f"NarrativeGenerator initialized with model: {self.model}")

    def generate(self, fact: str, decision: dict, situation_context: str, memory_context: str, graph_context: str = "") -> dict:
        """
        生成三层输出：对上、对自己、策略提示
        """
        logger.debug(f"Generating narrative for fact: {fact[:30]}...")
        
        try:
            prompt_data = PromptLoader.load_prompt("narrative", "generate")
            system_msg = prompt_data["system"]
            user_msg = prompt_data["user"].format(
                situation_context=situation_context,
                memory_context=memory_context,
                graph_context=graph_context or "(暂无图谱数据)",
                fact=fact,
                decision_json=json.dumps(decision, ensure_ascii=False)
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"}
            )
            logger.debug("Narrative generated successfully")
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in NarrativeGenerator: {e}", exc_info=True)
            return {
                "boss_version": "生成失败",
                "self_version": "生成失败",
                "strategy_hints": "生成失败"
            }

    def consolidate_memories(self, memories: list) -> list:
        """
        整理和归纳长期记忆
        """
        if not memories:
            return []
        
        logger.info(f"Consolidating {len(memories)} memories...")
        memories_text = "\n".join([f"- {m}" for m in memories])
        
        try:
            prompt_data = PromptLoader.load_prompt("narrative", "consolidate")
            system_msg = prompt_data["system"]
            user_msg = prompt_data["user"].format(memories_text=memories_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            insights = result.get("insights", [])
            logger.info(f"Consolidated memories into {len(insights)} insights.")
            return insights
        except Exception as e:
            logger.error(f"Error in consolidate_memories: {e}", exc_info=True)
            return []

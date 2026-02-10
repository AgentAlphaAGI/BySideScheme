from openai import OpenAI
import os
import json
from src.core.prompt_loader import PromptLoader
from src.core.logger import logger

class NarrativeGenerator:
    def __init__(self):
        if os.getenv("SILICONFLOW_API_KEY"):
            self.client = OpenAI(
                api_key=os.getenv("SILICONFLOW_API_KEY"),
                base_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
            )
            self.model = os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")
            logger.info(f"NarrativeGenerator initialized with SiliconFlow model: {self.model}")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o"
            logger.info("NarrativeGenerator initialized with OpenAI model: gpt-4o")

    def generate(self, fact: str, decision: dict, situation_context: str, memory_context: str) -> dict:
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

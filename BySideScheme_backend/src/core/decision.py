from typing import Dict
from openai import OpenAI
import os
import json
from src.core.prompt_loader import PromptLoader
from src.core.logger import logger

class DecisionEngine:
    def __init__(self):
        # 优先使用 SiliconFlow，如果未配置则回退到 OpenAI (或者根据需求强制)
        if os.getenv("SILICONFLOW_API_KEY"):
            self.client = OpenAI(
                api_key=os.getenv("SILICONFLOW_API_KEY"),
                base_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
            )
            self.model = os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o"

    def evaluate(self, fact: str, situation_context: str, memory_context: str) -> Dict:
        """
        执行 5 个维度的决策判断
        """
        try:
            prompt_data = PromptLoader.load_prompt("decision", "evaluate")
            system_msg = prompt_data["system"]
            user_msg = prompt_data["user"].format(
                situation_context=situation_context,
                memory_context=memory_context,
                fact=fact
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in DecisionEngine: {e}", exc_info=True)
            return {
                "should_say": False,
                "timing_check": "API Error",
                "target_audience": "Unknown",
                "strategic_intent": "Unknown",
                "future_impact": "Unknown",
                "strategy_summary": "系统错误，无法判断"
            }

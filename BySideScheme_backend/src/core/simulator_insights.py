import json
from typing import Any, Dict, List

from src.core.logger import logger
from src.core.prompt_loader import PromptLoader
from src.core.llm_client import LLMClientFactory


class SimulatorInsightsEngine:
    def __init__(self):
        self.client, self.model = LLMClientFactory.create_client("SIMULATOR_INSIGHTS_ENGINE")
        logger.info(f"SimulatorInsightsEngine initialized with model: {self.model}")

    def analyze(
        self,
        conversation: List[Dict[str, Any]],
        leaders: List[Dict[str, Any]],
        situation_context: str = "",
    ) -> Dict[str, Any]:
        try:
            prompt_data = PromptLoader.load_prompt("simulator", "analyze")
            system_msg = prompt_data["system"]
            user_msg = prompt_data["user"].format(
                leaders_json=json.dumps(leaders, ensure_ascii=False),
                conversation_json=json.dumps(conversation, ensure_ascii=False),
                situation_context=situation_context or "",
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in SimulatorInsightsEngine.analyze: {e}", exc_info=True)
            return {
                "situation_insights": [],
                "overall_risk_score": 0,
                "risks": [],
                "persona_updates": [],
                "next_actions": [],
                "uncertainties": ["insights_engine_error"],
            }

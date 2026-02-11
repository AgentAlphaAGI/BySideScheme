import os
from openai import OpenAI
from typing import Optional, Tuple
from src.core.logger import logger

class LLMClientFactory:
    @staticmethod
    def get_config(engine_env_var: str = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Returns (api_key, base_url, model) based on environment variables.
        Priority:
        1. engine_env_var (e.g. DECISION_ENGINE=deepseek -> DEEPSEEK_*)
        2. SILICONFLOW_*
        3. OPENAI_*
        """
        # 1. Check specific engine env var
        if engine_env_var:
            engine_name = os.getenv(engine_env_var, "").strip()
            if engine_name:
                prefix = engine_name.upper()
                api_key = os.getenv(f"{prefix}_API_KEY")
                base_url = os.getenv(f"{prefix}_BASE_URL")
                model = os.getenv(f"{prefix}_MODEL")
                
                # Try to fallback to SiliconFlow/OpenAI keys if only model is specified? 
                # No, if engine is specified, we expect full config or at least key + model.
                # Actually, sometimes we might just want to switch model but keep provider?
                # For simplicity, assume "Engine" implies a full set of prefix vars.
                
                if api_key and model:
                    logger.info(f"Using configured engine '{engine_name}' for {engine_env_var}")
                    return api_key, base_url, model
                else:
                    logger.warning(f"Engine '{engine_name}' configured for {engine_env_var} but missing {prefix}_API_KEY or {prefix}_MODEL")

        # 2. Check SiliconFlow
        if os.getenv("SILICONFLOW_API_KEY"):
            logger.debug("Using default SiliconFlow configuration")
            return (
                os.getenv("SILICONFLOW_API_KEY"),
                os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
                os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")
            )

        # 3. Check OpenAI
        if os.getenv("OPENAI_API_KEY"):
            logger.debug("Using default OpenAI configuration")
            return (
                os.getenv("OPENAI_API_KEY"),
                None, # OpenAI default base_url
                "gpt-4o"
            )
            
        return None, None, None

    @staticmethod
    def create_client(engine_env_var: str = None) -> Tuple[OpenAI, str]:
        """
        Returns (client, model_name)
        """
        api_key, base_url, model = LLMClientFactory.get_config(engine_env_var)
        
        if not api_key:
            # Try one last fallback for cases where only API key is needed and model is hardcoded (legacy)
            # But here we enforce config.
            raise ValueError(f"No valid LLM API key found. Please configure SILICONFLOW_API_KEY, OPENAI_API_KEY, or specific engine keys for {engine_env_var}.")
            
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model

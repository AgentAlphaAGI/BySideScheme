import yaml
import os
from typing import Dict, Any
from src.core.logger import logger

class PromptLoader:
    _prompts: Dict[str, Any] = {}
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _prompts_dir = os.path.join(_base_dir, "prompts")

    @classmethod
    def load_prompt(cls, filename: str, key: str) -> Dict[str, str]:
        """
        加载指定 YAML 文件中的 prompt key
        """
        file_path = os.path.join(cls._prompts_dir, f"{filename}.yaml")
        
        # 简单的缓存机制，避免每次都读文件 (生产环境可优化为只读一次或检测文件变更)
        if filename not in cls._prompts:
            if not os.path.exists(file_path):
                logger.error(f"Prompt file not found: {file_path}")
                raise FileNotFoundError(f"Prompt file not found: {file_path}")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cls._prompts[filename] = yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Error loading prompt file {filename}: {e}")
                raise e
        
        prompts = cls._prompts.get(filename, {})
        if key not in prompts:
             logger.error(f"Key '{key}' not found in {filename}.yaml")
             raise KeyError(f"Key '{key}' not found in {filename}.yaml")
             
        return prompts[key]

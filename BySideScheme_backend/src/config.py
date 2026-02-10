import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
    SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    SILICONFLOW_MODEL = os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")
    
    # 职场局势默认配置
    DEFAULT_CAREER_TYPE = "大厂"
    DEFAULT_LEVEL = "P6"
    DEFAULT_TARGET_LEVEL = "P7"

import os
from src.core.memory import MemoryManager
from src.autogen_agents.agents import MemoryAwareAssistantAgent
from dotenv import load_dotenv

class AgentFactory:
    def __init__(self):
        load_dotenv()
        # 初始化 MemoryManager
        self.memory_manager = MemoryManager()
        
        # 配置 LLM Config
        self.llm_config = self.build_llm_config()

    def _get_engine_env(self, engine: str) -> tuple[str | None, str | None, str | None]:
        prefix = engine.upper()
        api_key = os.getenv(f"{prefix}_API_KEY")
        base_url = os.getenv(f"{prefix}_BASE_URL")
        model = os.getenv(f"{prefix}_MODEL")
        return api_key, base_url, model

    def build_llm_config(self, engine: str | None = None) -> dict:
        # 优先使用 SiliconFlow
        api_key = os.getenv("SILICONFLOW_API_KEY")
        base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        model = os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")

        if engine:
            e_key, e_base, e_model = self._get_engine_env(engine)
            if e_key:
                api_key = e_key
            if e_model:
                model = e_model
            if e_base:
                base_url = e_base
        
        # 构造 config_list
        config_list = []
        
        if api_key:
            config_list.append({
                "model": model,
                "api_key": api_key,
                "base_url": base_url,
                "price": [0, 0], # Disable cost calculation warning
            })
        
        # Fallback to OpenAI if configured
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here":
            config_list.append({
                "model": "gpt-4o",
                "api_key": openai_key
            })
            
        if not config_list:
            raise ValueError("No valid API key found for SiliconFlow or OpenAI.")
        
        return {
            "config_list": config_list,
            "temperature": 0.7,
            "timeout": 120,
        }

    def build_leader_system_message(self, name: str, title: str, persona: str, persona_notes: str = "") -> str:
        notes = f"\n\n【近期观察与校准】\n{persona_notes}\n" if persona_notes else ""
        return f"""你是一个公司的{title}，名字叫 {name}。
        你的性格/管理风格是：{persona}。{notes}
        
        【你的角色】：
        1. 你是用户（User/Me）的上级或更高层领导。
        2. 你需要基于你的职位视角进行决策、点评或提问。
        3. 你关注团队目标、风险控制和资源分配。
        
        【行为准则】：
        1. 请保持符合你职位和人设的说话语气。
        2. 当涉及到过去的对话或决策时，请调用你的记忆。
        3. 如果有其他领导在场，请注意职场礼仪和层级关系。
        """

    def create_leader_agent(self, name: str, title: str, persona: str, engine: str | None = None, user_id: str = None) -> MemoryAwareAssistantAgent:
        """
        创建一个领导/上级 Agent
        :param name: 名字
        :param title: 职位/头衔 (如: 直属领导, 部门总监, 经理)
        :param persona: 人设/性格描述
        :param user_id: 真实用户ID，用于隔离记忆
        """
        system_message = self.build_leader_system_message(name=name, title=title, persona=persona)
        return MemoryAwareAssistantAgent(
            name=name,
            system_message=system_message,
            memory_manager=self.memory_manager,
            llm_config=self.build_llm_config(engine),
            user_id=user_id
        )

    def create_colleague_agent(self, name: str, persona: str, engine: str | None = None, user_id: str = None) -> MemoryAwareAssistantAgent:
        """创建一个同事 Agent"""
        system_message = f"""你是一个职场同事，名字叫 {name}。
        你的性格是：{persona}。
        你需要与用户（User/Me）以及其他同事进行互动。
        请根据你的性格进行回复，不要过于像 AI，要像一个真实的人。
        当涉及到过去的对话时，你会自动回忆起相关信息。
        """
        return MemoryAwareAssistantAgent(
            name=name,
            system_message=system_message,
            memory_manager=self.memory_manager,
            llm_config=self.build_llm_config(engine),
            user_id=user_id
        )

    def create_boss_agent(self, name: str, style: str, engine: str | None = None, user_id: str = None) -> MemoryAwareAssistantAgent:
        """创建一个领导 Agent"""
        system_message = f"""你是一个公司领导，名字叫 {name}。
        你的管理风格是：{style}。
        你关注结果，但也关注团队动态。
        请以领导的口吻进行回复。
        当涉及到过去的对话时，你会自动回忆起相关信息。
        """
        return MemoryAwareAssistantAgent(
            name=name,
            system_message=system_message,
            memory_manager=self.memory_manager,
            llm_config=self.build_llm_config(engine),
            user_id=user_id
        )

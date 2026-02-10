from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import autogen
from src.autogen_agents.factory import AgentFactory
from src.core.logger import logger

router = APIRouter(prefix="/simulator", tags=["simulator"])

# --- Models ---
class LeaderProfile(BaseModel):
    name: str
    title: str
    persona: str

class InitSimulatorRequest(BaseModel):
    user_name: str = "Me"
    leaders: List[LeaderProfile] = [
        {"name": "David", "title": "直属领导", "persona": "控制欲强，喜欢听好话，但关键时刻能扛事。口头禅是'抓手'、'赋能'。"},
        {"name": "Sarah", "title": "部门总监", "persona": "结果导向，雷厉风行，不喜欢听借口，只看数据。"}
    ]
    # Deprecated fields kept for backward compatibility if needed, or removed
    colleagues: Optional[List[Dict[str, str]]] = None 
    boss: Optional[Dict[str, str]] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    new_messages: List[Dict[str, Any]]

class RunScenarioRequest(BaseModel):
    user_name: str = "Me"
    leaders: List[LeaderProfile] = [
        {"name": "David", "title": "直属领导", "persona": "控制欲强，喜欢听好话，但关键时刻能扛事。"},
        {"name": "Sarah", "title": "部门总监", "persona": "结果导向，雷厉风行，不喜欢听借口。"}
    ]
    scenario: str
    max_rounds: int = 10

class ScenarioResponse(BaseModel):
    messages: List[Dict[str, Any]]

# --- Session Management ---

class SimulationSession:
    def __init__(self, request: InitSimulatorRequest):
        self.session_id = str(uuid.uuid4())
        self.factory = AgentFactory()
        
        # 1. User Agent
        self.user_proxy = autogen.UserProxyAgent(
            name=request.user_name,
            human_input_mode="NEVER",  # API 模式下不使用控制台输入
            max_consecutive_auto_reply=0,
            code_execution_config=False,
            system_message="我是团队的一员，正在向领导汇报或请示。"
        )
        
        # 2. Agents
        self.agents = [self.user_proxy]
        
        # Create Leader Agents
        if request.leaders:
            for leader in request.leaders:
                agent = self.factory.create_leader_agent(
                    name=leader.name,
                    title=leader.title,
                    persona=leader.persona
                )
                self.agents.append(agent)
        
        # Backward compatibility for colleagues/boss fields (Optional)
        if request.colleagues:
            for col in request.colleagues:
                agent = self.factory.create_colleague_agent(col["name"], col["persona"])
                self.agents.append(agent)
        
        if request.boss:
             # Map old boss field to new leader agent
             agent = self.factory.create_leader_agent(
                 name=request.boss["name"], 
                 title="领导", 
                 persona=request.boss["style"]
             )
             self.agents.append(agent)
            
        # 3. GroupChat
        self.groupchat = autogen.GroupChat(
            agents=self.agents,
            messages=[],
            max_round=10  # 初始 max_round，后续动态增加
        )
        
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.factory.llm_config
        )
        
    def step(self, message: str) -> List[Dict[str, Any]]:
        """
        执行一轮对话交互
        """
        # 记录开始时的消息数
        start_len = len(self.groupchat.messages)
        
        # 动态增加 max_round 以允许对话继续
        # 假设每次用户发言后，Agents 最多回复 4 次
        self.groupchat.max_round = len(self.groupchat.messages) + 5
        
        logger.info(f"Session {self.session_id}: User sending message: {message}")
        
        try:
            # 发送消息
            # 注意：send 是阻塞的，直到达到 max_round 或其他终止条件
            self.user_proxy.send(
                message=message,
                recipient=self.manager,
                request_reply=True
            )
        except Exception as e:
            logger.error(f"Error in simulation step: {e}")
            # AutoGen 有时会在 max_round 到达时抛出异常或警告，我们捕获它但继续返回已生成的消息
            pass
            
        # 获取新增消息
        new_messages = self.groupchat.messages[start_len:]
        
        # 过滤掉 User 自己的消息（如果需要），这里保留以便前端显示完整流
        return new_messages

# In-memory session storage (not production ready, but good for demo)
sessions: Dict[str, SimulationSession] = {}

# --- Endpoints ---

@router.post("/start", response_model=Dict[str, str])
async def start_simulation(request: InitSimulatorRequest):
    """初始化一个新的模拟会话"""
    session = SimulationSession(request)
    sessions[session.session_id] = session
    logger.info(f"Created new simulation session: {session.session_id}")
    return {"session_id": session.session_id}

@router.post("/chat", response_model=ChatResponse)
async def chat_simulation(request: ChatRequest):
    """发送消息并获取回复"""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    new_messages = session.step(request.message)
    
    # 格式化消息以适应前端
    formatted_messages = []
    for msg in new_messages:
        # AutoGen 消息格式: {'role': 'user', 'content': '...', 'name': 'Alice'}
        # 只有当消息内容非空时才返回
        if msg.get("content"):
            formatted_messages.append({
                "sender": msg.get("name", msg.get("role")),
                "content": msg.get("content"),
                "role": msg.get("role")
            })
            
    return ChatResponse(
        session_id=session.session_id,
        new_messages=formatted_messages
    )

@router.delete("/reset/{session_id}")
async def reset_simulation(session_id: str):
    """结束并清除会话"""
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "success", "message": "Session cleared"}
    raise HTTPException(status_code=404, detail="Session not found")

@router.post("/run", response_model=ScenarioResponse)
async def run_scenario_simulation(request: RunScenarioRequest):
    """
    运行一次完整的场景模拟
    """
    # Reuse InitSimulatorRequest structure for initialization
    init_req = InitSimulatorRequest(
        user_name=request.user_name,
        leaders=request.leaders
    )
    session = SimulationSession(init_req)
    
    # Set max rounds
    session.groupchat.max_round = request.max_rounds
    
    logger.info(f"Running scenario: {request.scenario}")
    
    try:
        # Initiate chat
        session.user_proxy.initiate_chat(
            session.manager,
            message=request.scenario
        )
    except Exception as e:
        logger.error(f"Error in scenario run: {e}")
        # Continue to return whatever messages were generated
        pass
        
    # Collect all messages
    formatted_messages = []
    for msg in session.groupchat.messages:
        if msg.get("content"):
            formatted_messages.append({
                "sender": msg.get("name", msg.get("role")),
                "content": msg.get("content"),
                "role": msg.get("role")
            })
            
    return ScenarioResponse(messages=formatted_messages)

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Literal
import uuid
import autogen
import asyncio
import json
import threading
import time
from src.autogen_agents.factory import AgentFactory
from src.core.logger import logger
from src.core.simulator_insights import SimulatorInsightsEngine
from src.core.database import DatabaseManager
from src.core.situation import SituationModel
from starlette.concurrency import run_in_threadpool
from src.api.security import verify_api_key

router = APIRouter(prefix="/simulator", tags=["simulator"])

# --- Models ---
class LeaderProfile(BaseModel):
    name: str
    title: str
    persona: str
    engine: Optional[str] = None

class ColleagueProfile(BaseModel):
    name: str
    persona: str
    engine: Optional[str] = None

class PersonProfile(BaseModel):
    kind: Literal["leader", "colleague"] = "leader"
    name: str
    title: str = ""
    persona: str
    engine: Optional[str] = None

class InitSimulatorRequest(BaseModel):
    user_id: Optional[str] = None
    situation: Optional[SituationModel] = None
    people: Optional[List[PersonProfile]] = None
    user_name: str = "Me"
    leaders: List[LeaderProfile] = [
        {"name": "David", "title": "直属领导", "persona": "控制欲强，喜欢听好话，但关键时刻能扛事。口头禅是'抓手'、'赋能'。"},
        {"name": "Sarah", "title": "部门总监", "persona": "结果导向，雷厉风行，不喜欢听借口，只看数据。"}
    ]
    colleagues: Optional[List[ColleagueProfile]] = None
    boss: Optional[Dict[str, str]] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    new_messages: List[Dict[str, Any]]
    analysis: Optional[Dict[str, Any]] = None

class RunScenarioRequest(BaseModel):
    user_id: Optional[str] = None
    situation: Optional[SituationModel] = None
    people: Optional[List[PersonProfile]] = None
    user_name: str = "Me"
    leaders: List[LeaderProfile] = [
        {"name": "David", "title": "直属领导", "persona": "控制欲强，喜欢听好话，但关键时刻能扛事。"},
        {"name": "Sarah", "title": "部门总监", "persona": "结果导向，雷厉风行，不喜欢听借口。"}
    ]
    scenario: str
    max_rounds: int = 10

class ScenarioResponse(BaseModel):
    messages: List[Dict[str, Any]]
    analysis: Optional[Dict[str, Any]] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    session_id: Optional[str] = None
    error: Optional[str] = None
    created_at: float
    updated_at: float

class JobResultResponse(BaseModel):
    job_id: str
    session_id: Optional[str] = None
    status: Literal["pending", "running", "completed", "failed"]
    messages: List[Dict[str, Any]]
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class StartChatJobRequest(BaseModel):
    session_id: str
    message: str

class StartRunJobRequest(BaseModel):
    user_id: Optional[str] = None
    situation: Optional[SituationModel] = None
    people: Optional[List[PersonProfile]] = None
    user_name: str = "Me"
    leaders: List[LeaderProfile] = []
    colleagues: Optional[List[ColleagueProfile]] = None
    boss: Optional[Dict[str, str]] = None
    scenario: str
    max_rounds: int = 10

class PersonaRollbackRequest(BaseModel):
    persona_version_id: str

# --- Session Management ---

class SimulationSession:
    def __init__(self, request: InitSimulatorRequest):
        self.session_id = str(uuid.uuid4())
        self.factory = AgentFactory()
        self.insights_engine = SimulatorInsightsEngine()
        self.user_name = request.user_name
        self.user_id = request.user_id
        self.db = DatabaseManager()
        self.situation: Optional[SituationModel] = request.situation
        if not self.situation and self.user_id:
            self.situation = self.db.get_situation(self.user_id)
        self.situation_context = self.situation.to_prompt_context() if self.situation else ""

        effective_people: List[PersonProfile] = []
        if request.people:
            effective_people = request.people
        else:
            for leader in (request.leaders or []):
                effective_people.append(
                    PersonProfile(
                        kind="leader",
                        name=leader.name,
                        title=leader.title,
                        persona=leader.persona,
                        engine=leader.engine,
                    )
                )
            for col in (request.colleagues or []):
                effective_people.append(
                    PersonProfile(
                        kind="colleague",
                        name=col.name,
                        title="",
                        persona=col.persona,
                        engine=col.engine,
                    )
                )
        self.leader_agents: Dict[str, Any] = {}
        self.leaders: List[Dict[str, Any]] = []
        self.leader_titles: Dict[str, str] = {}
        
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
        
        for person in effective_people:
            if person.kind == "leader":
                persona = person.persona
                persona_notes = ""
                if self.user_id:
                    latest = self.db.get_latest_persona(self.user_id, person.name)
                    if latest and latest.get("persona"):
                        persona = latest["persona"]
                        persona_notes = (latest.get("deviation_summary") or "").strip()

                agent = self.factory.create_leader_agent(
                    name=person.name,
                    title=person.title or "领导",
                    persona=persona,
                    engine=person.engine,
                )
                if persona_notes:
                    agent.system_message = self.factory.build_leader_system_message(
                        name=person.name,
                        title=person.title or "领导",
                        persona=persona,
                        persona_notes=persona_notes,
                    )
                self.agents.append(agent)
                self.leader_agents[person.name] = agent
                self.leader_titles[person.name] = person.title or "领导"
                self.leaders.append({"name": person.name, "title": person.title or "领导", "persona": persona})
            else:
                agent = self.factory.create_colleague_agent(
                    name=person.name,
                    persona=person.persona,
                    engine=person.engine,
                )
                self.agents.append(agent)

        if request.boss:
            agent = self.factory.create_leader_agent(
                name=request.boss["name"],
                title="领导",
                persona=request.boss["style"],
            )
            self.agents.append(agent)
            self.leader_agents[request.boss["name"]] = agent
            self.leader_titles[request.boss["name"]] = "领导"
            self.leaders.append({"name": request.boss["name"], "title": "领导", "persona": request.boss["style"]})
            
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

    def _format_messages_slice(self, start_index: int) -> List[Dict[str, Any]]:
        formatted = []
        for msg in self.groupchat.messages[start_index:]:
            if not msg.get("content"):
                continue
            formatted.append(
                {
                    "sender": msg.get("name", msg.get("role")),
                    "content": msg.get("content"),
                    "role": msg.get("role"),
                }
            )
        return formatted
        
    def _format_conversation(self) -> List[Dict[str, Any]]:
        conversation = []
        for msg in self.groupchat.messages:
            if not msg.get("content"):
                continue
            conversation.append(
                {
                    "sender": msg.get("name", msg.get("role")),
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                }
            )
        return conversation

    def _apply_persona_updates(self, analysis: Dict[str, Any]) -> None:
        updates = analysis.get("persona_updates") or []
        for u in updates:
            if not isinstance(u, dict):
                continue
            name = u.get("name")
            if not name or name not in self.leader_agents:
                continue
            deviation = bool(u.get("deviation_detected"))
            confidence = float(u.get("update_confidence") or 0.0)
            updated_persona = (u.get("updated_persona") or "").strip()
            deviation_summary = (u.get("deviation_summary") or "").strip()
            if not deviation or confidence < 0.6 or not updated_persona:
                continue
            title = self.leader_titles.get(name, "领导")
            agent = self.leader_agents[name]
            # MemoryAwareAssistantAgent (and AutoGen agents) store system_message in ._oai_system_message 
            # or simply use update_system_message() method if available, or recreate the agent.
            # AutoGen ConversableAgent has update_system_message method.
            agent.update_system_message(
                self.factory.build_leader_system_message(
                    name=name,
                    title=title,
                    persona=updated_persona,
                    persona_notes=deviation_summary,
                )
            )

            for leader in self.leaders:
                if leader.get("name") == name:
                    leader["persona"] = updated_persona
                    break
            if self.user_id:
                self.db.save_persona_version(
                    persona_id=str(uuid.uuid4()),
                    user_id=self.user_id,
                    person_name=name,
                    person_title=title,
                    persona=updated_persona,
                    deviation_summary=deviation_summary,
                    confidence=confidence,
                )

    def analyze(self) -> Dict[str, Any]:
        analysis = self.insights_engine.analyze(
            conversation=self._format_conversation(),
            leaders=self.leaders,
            situation_context=self.situation_context,
        )
        self._apply_persona_updates(analysis)
        return analysis

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

# In-memory job storage (not production ready, but good for demo)
_jobs_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}

def _job_get(job_id: str) -> Optional[Dict[str, Any]]:
    with _jobs_lock:
        return _jobs.get(job_id)

def _job_update(job_id: str, patch: Dict[str, Any]) -> None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.update(patch)
        job["updated_at"] = time.time()

def _job_append_messages(job_id: str, messages: List[Dict[str, Any]]) -> None:
    if not messages:
        return
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["messages"].extend(messages)
        job["updated_at"] = time.time()

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
    
    new_messages = await run_in_threadpool(session.step, request.message)
    analysis = await run_in_threadpool(session.analyze)
    
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
        new_messages=formatted_messages,
        analysis=analysis,
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
        user_id=request.user_id,
        situation=request.situation,
        people=request.people,
        user_name=request.user_name,
        leaders=request.leaders
    )
    session = SimulationSession(init_req)
    
    # Set max rounds
    session.groupchat.max_round = request.max_rounds
    
    logger.info(f"Running scenario: {request.scenario}")
    
    try:
        await run_in_threadpool(lambda: session.user_proxy.initiate_chat(session.manager, message=request.scenario))
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
            
    analysis = await run_in_threadpool(session.analyze)
    return ScenarioResponse(messages=formatted_messages, analysis=analysis)

@router.post("/jobs/chat", response_model=JobStatusResponse)
async def start_chat_job(request: StartChatJobRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    job_id = str(uuid.uuid4())
    now = time.time()
    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "session_id": request.session_id,
            "created_at": now,
            "updated_at": now,
            "messages": [],
            "analysis": None,
            "error": None,
            "kind": "chat",
        }

    async def runner():
        _job_update(job_id, {"status": "running"})
        start_len = len(session.groupchat.messages)
        future = asyncio.create_task(run_in_threadpool(session.step, request.message))
        last_seen = start_len
        try:
            while not future.done():
                current_len = len(session.groupchat.messages)
                if current_len > last_seen:
                    _job_append_messages(job_id, session._format_messages_slice(last_seen))
                    last_seen = current_len
                await asyncio.sleep(0.2)
            await future
            current_len = len(session.groupchat.messages)
            if current_len > last_seen:
                _job_append_messages(job_id, session._format_messages_slice(last_seen))
            analysis = await run_in_threadpool(session.analyze)
            _job_update(job_id, {"status": "completed", "analysis": analysis})
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            _job_update(job_id, {"status": "failed", "error": str(e)})

    asyncio.create_task(runner())
    return JobStatusResponse(job_id=job_id, status="pending", session_id=request.session_id, created_at=now, updated_at=now)

@router.post("/jobs/run", response_model=JobStatusResponse)
async def start_run_job(request: StartRunJobRequest):
    init_req = InitSimulatorRequest(
        user_id=request.user_id,
        situation=request.situation,
        people=request.people,
        user_name=request.user_name,
        leaders=request.leaders,
        colleagues=request.colleagues,
        boss=request.boss,
    )
    session = SimulationSession(init_req)
    sessions[session.session_id] = session
    session.groupchat.max_round = request.max_rounds

    job_id = str(uuid.uuid4())
    now = time.time()
    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "session_id": session.session_id,
            "created_at": now,
            "updated_at": now,
            "messages": [],
            "analysis": None,
            "error": None,
            "kind": "run",
        }

    async def runner():
        _job_update(job_id, {"status": "running"})
        last_seen = 0
        future = asyncio.create_task(
            run_in_threadpool(lambda: session.user_proxy.initiate_chat(session.manager, message=request.scenario))
        )
        try:
            while not future.done():
                current_len = len(session.groupchat.messages)
                if current_len > last_seen:
                    _job_append_messages(job_id, session._format_messages_slice(last_seen))
                    last_seen = current_len
                await asyncio.sleep(0.2)
            await future
            current_len = len(session.groupchat.messages)
            if current_len > last_seen:
                _job_append_messages(job_id, session._format_messages_slice(last_seen))
            analysis = await run_in_threadpool(session.analyze)
            _job_update(job_id, {"status": "completed", "analysis": analysis})
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            _job_update(job_id, {"status": "failed", "error": str(e)})

    asyncio.create_task(runner())
    return JobStatusResponse(job_id=job_id, status="pending", session_id=session.session_id, created_at=now, updated_at=now)

@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    job = _job_get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        session_id=job.get("session_id"),
        error=job.get("error"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
    )

@router.get("/jobs/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(job_id: str):
    job = _job_get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResultResponse(
        job_id=job["job_id"],
        session_id=job.get("session_id"),
        status=job["status"],
        messages=list(job.get("messages") or []),
        analysis=job.get("analysis"),
        error=job.get("error"),
    )

@router.get("/jobs/{job_id}/stream")
async def stream_job_sse(job_id: str):
    job = _job_get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_gen():
        sent = 0
        last_status = None
        while True:
            job_now = _job_get(job_id)
            if not job_now:
                yield "event: error\ndata: {\"detail\":\"Job not found\"}\n\n"
                return

            status = job_now.get("status")
            if status != last_status:
                last_status = status
                yield f"event: status\ndata: {json.dumps({'job_id': job_id, 'status': status}, ensure_ascii=False)}\n\n"

            msgs = job_now.get("messages") or []
            while sent < len(msgs):
                yield f"event: message\ndata: {json.dumps(msgs[sent], ensure_ascii=False)}\n\n"
                sent += 1

            if status in ("completed", "failed"):
                analysis = job_now.get("analysis")
                if analysis is not None:
                    yield f"event: analysis\ndata: {json.dumps(analysis, ensure_ascii=False)}\n\n"
                if status == "failed":
                    yield f"event: error\ndata: {json.dumps({'error': job_now.get('error')}, ensure_ascii=False)}\n\n"
                yield "event: done\ndata: {}\n\n"
                return

            await asyncio.sleep(0.2)

    return StreamingResponse(event_gen(), media_type="text/event-stream")

@router.websocket("/jobs/{job_id}/ws")
async def stream_job_ws(websocket: WebSocket, job_id: str):
    try:
        verify_api_key(websocket.headers.get("x-api-key"))
    except HTTPException:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    sent = 0
    last_status = None
    try:
        while True:
            job_now = _job_get(job_id)
            if not job_now:
                await websocket.send_json({"type": "error", "detail": "Job not found"})
                await websocket.close()
                return

            status = job_now.get("status")
            if status != last_status:
                last_status = status
                await websocket.send_json({"type": "status", "job_id": job_id, "status": status})

            msgs = job_now.get("messages") or []
            while sent < len(msgs):
                await websocket.send_json({"type": "message", "data": msgs[sent]})
                sent += 1

            if status in ("completed", "failed"):
                if job_now.get("analysis") is not None:
                    await websocket.send_json({"type": "analysis", "data": job_now.get("analysis")})
                if status == "failed":
                    await websocket.send_json({"type": "error", "error": job_now.get("error")})
                await websocket.send_json({"type": "done"})
                await websocket.close()
                return

            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        return

@router.get("/persona/{user_id}/{person_name}/versions")
async def list_persona_versions(user_id: str, person_name: str, limit: int = 50):
    db = DatabaseManager()
    return {"versions": db.list_persona_versions(user_id=user_id, person_name=person_name, limit=limit)}

@router.post("/persona/{user_id}/{person_name}/rollback")
async def rollback_persona(user_id: str, person_name: str, request: PersonaRollbackRequest):
    db = DatabaseManager()
    version = db.get_persona_version(request.persona_version_id)
    if not version or version.get("user_id") != user_id or version.get("person_name") != person_name:
        raise HTTPException(status_code=404, detail="Persona version not found")
    new_id = str(uuid.uuid4())
    db.save_persona_version(
        persona_id=new_id,
        user_id=user_id,
        person_name=person_name,
        person_title=version.get("person_title") or "",
        persona=version.get("persona") or "",
        deviation_summary=f"rollback_from:{request.persona_version_id}",
        confidence=1.0,
    )
    return {"rolled_back_to": request.persona_version_id, "new_version_id": new_id}

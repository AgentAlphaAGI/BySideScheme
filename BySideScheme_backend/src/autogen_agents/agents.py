from typing import List, Dict, Optional, Union
import autogen
from src.core.memory import MemoryManager
from src.core.logger import logger

class MemoryAwareAssistantAgent(autogen.AssistantAgent):
    """
    一个集成了 Mem0 记忆能力的 AutoGen Agent。
    每个人格（Agent）拥有独立的记忆空间（基于 agent_name）。
    """

    def __init__(
        self,
        name: str,
        system_message: str,
        memory_manager: MemoryManager,
        llm_config: dict,
        **kwargs
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            **kwargs
        )
        self.memory_manager = memory_manager
        # 使用 agent 的名字作为 memory 的 user_id，实现数据隔离
        self.memory_user_id = f"agent_{name}" 
        
        # 注册钩子：在处理消息前/后进行记忆操作
        # 注意：AutoGen 的 register_reply 主要用于生成回复。
        # 我们使用 hook 来在生成回复前注入记忆上下文。
        self.register_reply([autogen.Agent, None], self._reply_with_memory, position=0)

    def _reply_with_memory(self, recipient, messages=None, sender=None, config=None):
        """
        在生成回复前，检索相关记忆并注入到上下文中。
        """
        if messages is None:
            if sender is None:
                return False, None
            messages = self.chat_messages[sender]
            
        if not messages:
            return False, None
            
        # 1. 获取最后一条消息内容作为查询
        last_message = messages[-1]
        last_content = last_message.get('content', '')
        if not last_content:
            return False, None
            
        # 2. 检索记忆 (限制 3 条)
        logger.debug(f"[{self.name}] Searching memory for: {last_content[:20]}...")
        relevant_memories = self.memory_manager._search(
            query=last_content,
            user_id=self.memory_user_id,
            limit=3
        )
        
        # 3. 如果有记忆，构造 Context
        if relevant_memories:
            memory_text = "\n".join([f"- {m['memory']}" for m in relevant_memories])
            logger.info(f"[{self.name}] Found relevant memories: {memory_text}")
            
            # 4. 注入记忆到 System Message (临时)
            # 这种方式会影响当前对话的所有后续交互，直到被重置。
            # 为了不污染原始 system_message，我们可以在 messages 列表中插入一条 system 消息
            # 但 AutoGen 的 AssistantAgent 默认会将 messages 发送给 LLM
            
            # 策略：插入一条临时的 System 消息到当前对话历史的末尾（在 User 消息之前）
            # 或者，更简单地，追加到 User 的消息后面
            
            # 这里我们选择追加到 User 消息后面，用特殊的标记
            # 注意：我们需要修改 messages 列表中的最后一条消息，但这会影响 self.chat_messages
            # 为了安全起见，我们只修改传递给 LLM 的 messages 副本
            # 但在这里我们是在 register_reply hook 中，如果返回 False, None，后续的 reply_func 会使用原始 messages
            
            # 因此，我们必须在这里调用 generate_oai_reply，传入修改后的 messages
            
            augmented_content = f"{last_content}\n\n[Internal Memory Recall]:\n{memory_text}"
            
            # 创建消息副本
            augmented_messages = messages.copy()
            augmented_messages[-1] = {
                "role": last_message["role"],
                "content": augmented_content
            }
            
            # 调用父类的生成逻辑 (autogen.AssistantAgent -> ConversableAgent.generate_oai_reply)
            return self.generate_oai_reply(augmented_messages, sender, config)
            
        # 如果没有记忆，继续默认流程
        return False, None

    def receive(self, message: Union[Dict, str], sender: autogen.Agent, request_reply: Optional[bool] = None, silent: Optional[bool] = False):
        """
        重写 receive 方法以记录收到的消息到记忆中。
        """
        # 1. 处理消息内容
        content = message.get('content') if isinstance(message, dict) else message
        
        # 2. 存入记忆 (异步或同步)
        # 只有当消息是来自 User 或者其他 Agent 的实质性内容时才存储
        if content and sender.name != self.name:
            # 简单去重或过滤可以放在这里
            logger.debug(f"[{self.name}] Storing memory from {sender.name}")
            self.memory_manager._add(
                content=f"Received from {sender.name}: {content}",
                user_id=self.memory_user_id,
                category="conversation",
                extra_metadata={"sender": sender.name}
            )
            
        # 3. 调用父类 receive
        super().receive(message, sender, request_reply, silent)

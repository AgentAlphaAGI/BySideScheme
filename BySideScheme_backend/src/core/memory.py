from mem0 import Memory
from typing import List, Dict, Any, Optional
import os
from src.core.logger import logger

class MemoryManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化 MemoryManager (单例模式)
        :param config: mem0 的配置字典，如果为 None 则使用默认本地持久化配置
        """
        if self._initialized:
            return

        if config is None:
            # 获取项目根目录 (假设当前文件在 src/core/memory.py)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "path": os.path.join(data_dir, "qdrant"),
                        "on_disk": True
                    }
                },
                "history_db_path": os.path.join(data_dir, "history.db")
            }
            
            # 配置 LLM 为 SiliconFlow (如果有 Key)
            if os.getenv("SILICONFLOW_API_KEY"):
                config["llm"] = {
                    "provider": "openai",
                    "config": {
                        "api_key": os.getenv("SILICONFLOW_API_KEY"),
                        "openai_base_url": os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
                        "model": os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")
                    }
                }
                
                # 配置 Embedder 为 SiliconFlow (使用 OpenAI 兼容协议)
                # 使用 BAAI/bge-m3 作为嵌入模型 (维度 1024)
                config["embedder"] = {
                    "provider": "openai",
                    "config": {
                        "api_key": os.getenv("SILICONFLOW_API_KEY"),
                        "openai_base_url": os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
                        "model": "BAAI/bge-m3",
                        "embedding_dims": 1024
                    }
                }
                
                # 更新向量库维度配置以匹配 Embedder
                config["vector_store"]["config"]["embedding_model_dims"] = 1024
            
            logger.info(f"Using local persistence storage at: {data_dir}")

        self.memory = Memory.from_config(config)
        self._initialized = True

    def _add(self, content: str, user_id: str, category: str, extra_metadata: Dict[str, Any] = None):
        metadata = {"category": category}
        if extra_metadata:
            metadata.update(extra_metadata)
        # mem0 v1.0.3 add method signature: add(messages, user_id=None, agent_id=None, run_id=None, metadata=None, filters=None, prompt=None)
        # 这里的 messages 可以是 string
        logger.debug(f"Adding memory for user {user_id} in category {category}")
        self.memory.add(content, user_id=user_id, metadata=metadata)

    def _rerank_results(self, results: List[Dict], limit: int) -> List[Dict]:
        """
        对检索结果进行重排序（时间加权）
        """
        if not results:
            return []
            
        from datetime import datetime, timezone
        
        # Helper to parse time
        def get_timestamp(item):
            # Try to find created_at in various places
            ts_str = item.get("created_at")
            if not ts_str and item.get("metadata"):
                ts_str = item.get("metadata", {}).get("created_at")
                
            if ts_str:
                try:
                    # Mem0 usually uses ISO format like '2023-10-27T10:00:00.123456'
                    # Handle potential 'Z' or offset
                    dt = datetime.fromisoformat(str(ts_str).replace('Z', '+00:00'))
                    return dt.timestamp()
                except:
                    pass
            return 0
            
        current_ts = datetime.now(timezone.utc).timestamp()
        
        for res in results:
            # Normalize original score (assuming it's cosine similarity ~0-1)
            original_score = res.get("score", 0.0)
            
            # Time decay
            item_ts = get_timestamp(res)
            if item_ts > 0:
                # Days since creation
                days_diff = max(0, (current_ts - item_ts) / 86400)
                # Decay function: 1 / (1 + 0.1 * days)
                # Day 0: 1.0
                # Day 10: 0.5
                time_weight = 1.0 / (1.0 + 0.1 * days_diff)
            else:
                time_weight = 0.5 # Default for unknown time
                
            # Final Score: 70% Relevance + 30% Recency
            # This is a heuristic.
            res["_final_score"] = original_score * 0.7 + time_weight * 0.3
            
        # Sort by final score descending
        results.sort(key=lambda x: x.get("_final_score", 0), reverse=True)
        
        return results[:limit]

    def _search(self, query: str, user_id: str, category: str = None, limit: int = 5) -> List[Dict]:
        # mem0 v1.0.3 search method signature: search(query, user_id=None, agent_id=None, run_id=None, limit=100, filters=None)
        filters = None
        if category:
            filters = {"category": category}
            
        logger.debug(f"Searching memory for user {user_id} with query '{query}' in category {category}")
        
        # Fetch more candidates for reranking (e.g. 2x limit)
        fetch_limit = limit * 2
        results = self.memory.search(query, user_id=user_id, limit=fetch_limit, filters=filters)
        results_list = results.get("results", [])
        
        # Rerank
        return self._rerank_results(results_list, limit)

    # --- 特定记忆类型的便捷方法 ---

    def add_narrative_memory(self, user_id: str, content: str, source: str = "daily_report"):
        """添加叙事记忆：官方说法、已使用的关键词"""
        self._add(content, user_id, "narrative", {"source": source})

    def add_political_memory(self, user_id: str, content: str, risk_level: str = "low"):
        """添加关系记忆：上级偏好、谁被绕过"""
        self._add(content, user_id, "political", {"risk_level": risk_level})

    def add_career_state_memory(self, user_id: str, content: str, phase: str):
        """添加状态记忆：当前阶段、加分/扣分项"""
        self._add(content, user_id, "career_state", {"phase": phase})

    def add_commitment_memory(self, user_id: str, content: str, status: str = "pending", due_date: str = None):
        """添加承诺记忆：未完成承诺、模糊表态"""
        self._add(content, user_id, "commitment", {"status": status, "due_date": due_date})

    def get_relevant_memories(self, user_id: str, query: str, limit_per_category: int = 3) -> Dict[str, List[str]]:
        """
        根据查询词获取所有相关类别的记忆
        """
        categories = ["narrative", "political", "career_state", "commitment"]
        memories = {}
        
        for cat in categories:
            results = self._search(query, user_id, category=cat, limit=limit_per_category)
            # 提取记忆文本
            memories[cat] = [res.get("memory") for res in results]
            
        return memories

    def get_context_string(self, user_id: str, query: str = "当前局势 风险 承诺") -> str:
        """
        构建用于 Prompt 的上下文
        """
        mems = self.get_relevant_memories(user_id, query)
        
        def format_list(items):
            if not items:
                return "  (无相关记录)"
            return "\n".join([f"  - {item}" for item in items])

        return f"""
[记忆库提取]
> 叙事记忆 (Narrative - 官方口径/历史说法):
{format_list(mems['narrative'])}

> 关系记忆 (Political - 上级偏好/人际风险):
{format_list(mems['political'])}

> 状态记忆 (Career State - 个人表现/阶段):
{format_list(mems['career_state'])}

> 承诺记忆 (Commitment - 待办/模糊承诺):
{format_list(mems['commitment'])}
"""

    def get_all_memories(self, user_id: str) -> List[Dict]:
        """
        获取用户的所有记忆
        """
        results = self.memory.get_all(user_id=user_id)
        # mem0 returns dict with 'results' key or list depending on version. 
        # Safely handle both.
        if isinstance(results, dict):
            return results.get("results", [])
        return results

    def delete_memory(self, memory_id: str):
        """
        删除指定 ID 的记忆
        """
        self.memory.delete(memory_id)

    def delete_all_memories(self, user_id: str):
        """
        删除用户的所有记忆
        """
        self.memory.delete_all(user_id=user_id)

    def add_insight_memory(self, user_id: str, content: str):
        """添加洞察记忆：长期模式、总结"""
        self._add(content, user_id, "insight", {"source": "consolidation"})

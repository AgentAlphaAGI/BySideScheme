import json
import time
import os
from typing import List, Dict, Any

class MockMemoryManager:
    def __init__(self):
        # 模拟持久化：尝试从本地文件加载
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.storage_file = os.path.join(self.data_dir, "mock_memories.json")
        
        self.memories = self._load_memories()

    def _load_memories(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Mock memory load failed: {e}")
        
        return {
            "narrative": [],
            "political": [],
            "career_state": [],
            "commitment": []
        }

    def _save_memories(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Mock memory save failed: {e}")

    def add_narrative_memory(self, user_id, content, source="daily_report"):
        self.memories["narrative"].append(content)
        self._save_memories()

    def add_political_memory(self, user_id, content, risk_level="low"):
        self.memories["political"].append(content)
        self._save_memories()
    
    def add_career_state_memory(self, user_id, content, phase):
        self.memories["career_state"].append(content)
        self._save_memories()
        
    def add_commitment_memory(self, user_id, content, status="pending", due_date=None):
        self.memories["commitment"].append(content)
        self._save_memories()

    def get_context_string(self, user_id, query):
        # 简单模拟检索：返回最近的几条
        narrative = self.memories["narrative"][-3:] if self.memories["narrative"] else ["(无)"]
        political = self.memories["political"][-3:] if self.memories["political"] else ["(无)"]
        state = self.memories["career_state"][-3:] if self.memories["career_state"] else ["(无)"]
        commitment = self.memories["commitment"][-3:] if self.memories["commitment"] else ["(无)"]
        
        def format_list(items):
            return "\n".join([f"  - {item}" for item in items])

        return f"""
[Mock 记忆库提取] (已持久化至 {self.storage_file})
> 叙事记忆:
{format_list(narrative)}
> 关系记忆:
{format_list(political)}
> 状态记忆:
{format_list(state)}
> 承诺记忆:
{format_list(commitment)}
"""

class MockDecisionEngine:
    def evaluate(self, fact, situation_context, memory_context):
        time.sleep(1) # 模拟思考
        return {
            "should_say": True,
            "timing_check": "合适",
            "target_audience": "直属领导",
            "strategic_intent": "铺路",
            "future_impact": "展示解决问题的能力",
            "strategy_summary": "建议低调处理，强调修复过程中的技术难点，弱化历史遗留问题的人为因素。"
        }

class MockNarrativeGenerator:
    def generate(self, fact, decision, situation_context, memory_context):
        time.sleep(1) # 模拟生成
        return {
            "boss_version": "今日修复了支付模块的潜在稳定性问题（Issue #1024）。经排查，该问题涉及历史代码的边界情况处理。目前已通过补丁修复并验证通过，确保了线上服务的稳定性。",
            "self_version": "其实是隔壁组半年前留下的坑，代码逻辑完全混乱。为了不惹麻烦，我没说是谁写的，只说是'历史代码边界情况'。把这个雷排了，防止后面爆在自己手里。",
            "strategy_hints": "下次周会如果提到代码质量，可以顺带提一下这次修复的复杂度，侧面印证你对系统的掌控力，但千万别点名隔壁组。"
        }

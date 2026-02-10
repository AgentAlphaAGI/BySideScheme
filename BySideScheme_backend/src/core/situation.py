from pydantic import BaseModel, Field
from typing import List, Optional

class SituationModel(BaseModel):
    career_type: str = Field(..., description="职业类型: 公务员/大厂/央国企/小公司")
    current_level: str = Field(..., description="当前职级")
    target_level: str = Field(..., description="目标职级")
    promotion_window: bool = Field(False, description="是否在晋升窗口")
    boss_style: str = Field(..., description="上级风格: 控制型/结果型/风险型/情绪型")
    current_phase: str = Field(..., description="当前状态: 上升期/稳定期/观察期/危险期")
    personal_goal: str = Field(..., description="个人目标: 躺平/冲刺")
    recent_events: List[str] = Field(default_factory=list, description="最近关键事件")

    def to_prompt_context(self) -> str:
        return f"""
        当前局势：
        - 职业环境：{self.career_type}
        - 职级：{self.current_level} -> {self.target_level}
        - 晋升窗口：{'是' if self.promotion_window else '否'}
        - 上级风格：{self.boss_style}
        - 当前阶段：{self.current_phase}
        - 个人目标：{self.personal_goal}
        - 最近事件：{', '.join(self.recent_events)}
        """

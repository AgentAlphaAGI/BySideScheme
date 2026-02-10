from pydantic import BaseModel, Field
from typing import List, Optional

class Stakeholder(BaseModel):
    name: str = Field(..., description="角色名称/称呼 (e.g. 直属老板, 大老板, HR, 隔壁老王)")
    role: str = Field(..., description="角色身份 (e.g. Line Manager, Skip Manager, Peer, HRBP)")
    style: str = Field(..., description="行事风格 (e.g. 风险厌恶型, 结果导向型, 政治动物)")
    relationship: str = Field("Neutral", description="当前关系状态 (e.g. 信任, 猜忌, 盟友, 敌对)")
    influence_level: str = Field("Medium", description="对晋升的影响力 (High/Medium/Low)")

class SituationModel(BaseModel):
    career_type: str = Field(..., description="职业类型: 公务员/大厂/央国企/小公司")
    current_level: str = Field(..., description="当前职级")
    target_level: str = Field(..., description="目标职级")
    promotion_window: bool = Field(False, description="是否在晋升窗口")
    stakeholders: List[Stakeholder] = Field(default_factory=list, description="关键干系人列表")
    current_phase: str = Field(..., description="当前状态: 上升期/稳定期/观察期/危险期")
    personal_goal: str = Field(..., description="个人目标: 躺平/冲刺")
    recent_events: List[str] = Field(default_factory=list, description="最近关键事件")

    def to_prompt_context(self) -> str:
        stakeholders_text = "暂无"
        if self.stakeholders:
            stakeholders_text = "\n".join([
                f"        - {s.name} ({s.role}): 风格[{s.style}], 关系[{s.relationship}], 影响力[{s.influence_level}]"
                for s in self.stakeholders
            ])

        return f"""
        当前局势：
        - 职业环境：{self.career_type}
        - 职级：{self.current_level} -> {self.target_level}
        - 晋升窗口：{'是' if self.promotion_window else '否'}
        - 关键角色分析：
{stakeholders_text}
        - 当前阶段：{self.current_phase}
        - 个人目标：{self.personal_goal}
        - 最近事件：{', '.join(self.recent_events)}
        """

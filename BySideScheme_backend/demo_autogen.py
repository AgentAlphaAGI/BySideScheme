import sys
import os
import autogen
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.autogen_agents.factory import AgentFactory

def main():
    print(">>> 初始化 AutoGen 职场模拟器...")
    try:
        factory = AgentFactory()
    except ValueError as e:
        print(f"Error: {e}")
        print("请确保 .env 文件中配置了 SILICONFLOW_API_KEY 或 OPENAI_API_KEY")
        return

    # 1. 创建 User Agent (我)
    user_proxy = autogen.UserProxyAgent(
        name="Me",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
        system_message="我是团队的一员，正在参与讨论。"
    )
    
    # 2. 创建同事 Agent
    print(">>> 正在召集同事...")
    colleague_a = factory.create_colleague_agent(
        name="Alice", 
        persona="热心肠，喜欢八卦，但工作能力一般。喜欢在句尾加波浪号~"
    )
    colleague_b = factory.create_colleague_agent(
        name="Bob", 
        persona="卷王，技术大牛，说话直接，有点看不起人，喜欢用专业术语。"
    )
    
    # 3. 创建领导 Agent
    print(">>> 正在请示领导...")
    boss = factory.create_boss_agent(
        name="David", 
        style="控制欲强，喜欢听好话，但关键时刻能扛事。口头禅是'抓手'、'赋能'、'闭环'。"
    )
    
    # 4. 创建 GroupChat
    groupchat = autogen.GroupChat(
        agents=[user_proxy, colleague_a, colleague_b, boss],
        messages=[],
        max_round=15
    )
    
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=factory.llm_config
    )
    
    print("\n>>> 场景：周五下午的临时会议")
    print(">>> Alice, Bob, David (领导) 已上线。")
    print(">>> 请输入你的第一句话来开始讨论 (例如: '这周的项目进度有点慢，大家怎么看？')")
    
    # 5. 开始对话
    user_proxy.initiate_chat(
        manager,
        message="各位，关于下周的项目汇报，大家有什么想法？我有点担心时间不够。"
    )

if __name__ == "__main__":
    main()

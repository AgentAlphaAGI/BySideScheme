import os
import sys
import json
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.situation import SituationModel
from src.services.advisor import AdvisorService
# 使用真实的组件
from src.core.memory import MemoryManager
from src.core.decision import DecisionEngine
from src.core.generator import NarrativeGenerator

def main():
    load_dotenv()
    
    # 检查 API KEY
    silicon_key = os.getenv("SILICONFLOW_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not silicon_key and (not openai_key or openai_key == "your_openai_api_key_here"):
        print("Error: 请在 .env 文件中配置 SILICONFLOW_API_KEY 或 OPENAI_API_KEY")
        return

    print("==================================================")
    print(f"   来事儿 (Laishier) - Real Demo")
    print(f"   Provider: {'SiliconFlow' if silicon_key else 'OpenAI'}")
    print("==================================================")
    
    # 1. 初始化局势
    situation = SituationModel(
        career_type="互联网大厂",
        current_level="P6",
        target_level="P7",
        promotion_window=True,
        boss_style="风险厌恶型",
        current_phase="观察期",
        personal_goal="想拼一把冲一下",
        recent_events=["上周刚出了一个线上小故障", "昨天帮老板挡了一个需求"]
    )
    
    print("\n>>> 1. 职场局势建模")
    print(situation.to_prompt_context())
    
    # 2. 初始化服务 (使用真实组件)
    print("\n>>> 2. 系统初始化...")
    try:
        # MemoryManager 会自动使用本地持久化存储 (laishier-backend/data)
        memory_manager = MemoryManager()
        decision_engine = DecisionEngine()
        narrative_generator = NarrativeGenerator()
        
        advisor = AdvisorService(
            memory_manager=memory_manager,
            decision_engine=decision_engine,
            narrative_generator=narrative_generator
        )
        print("核心服务已启动。")
    except Exception as e:
        print(f"初始化失败: {e}")
        return
    
    # 3. 模拟用户输入
    user_id = "real_user_001"
    fact = "今天修复了一个遗留的支付bug，发现其实是隔壁组半年前留下的坑。但我如果直说，可能会得罪隔壁组leader，他是老板的老战友。"
    
    print(f"\n>>> 3. 接收今日事实")
    print(f"用户输入: {fact}")
    
    # 4. 执行处理流程
    print("\n>>> 4. 正在调用 AI 进行决策与生成 (请稍候)...")
    try:
        result = advisor.process_daily_input(user_id, fact, situation)
        
        # 5. 展示结果
        print("\n>>> 5. 处理结果")
        
        print("\n[决策分析]")
        print(json.dumps(result["decision"], indent=2, ensure_ascii=False))
        
        print("\n[生成文案]")
        print("-" * 30)
        print(f"【对上版本】:\n{result['narrative']['boss_version']}")
        print("-" * 30)
        print(f"【对自己版本】:\n{result['narrative']['self_version']}")
        print("-" * 30)
        print(f"【策略提示】:\n{result['narrative']['strategy_hints']}")
        print("-" * 30)
        
        print("\n>>> 6. 记忆更新")
        print("已自动存入持久化记忆库。")
        
    except Exception as e:
        print(f"\n处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

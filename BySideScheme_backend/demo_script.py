import requests
import json
import time

BASE_URL = "http://localhost:8001"
USER_ID = "demo_user_script"
HEADERS = {"Content-Type": "application/json"}

def print_step(title):
    print(f"\n{'='*50}")
    print(f"🚀 {title}")
    print(f"{'='*50}")

def print_response(response):
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

def run_demo():
    print("🤖 欢迎使用“来事儿”一键体验脚本")
    print(f"📍 目标服务器: {BASE_URL}")
    print(f"👤 测试用户: {USER_ID}\n")

    # 1. 设置局势
    print_step("步骤 1: 设定职场局势 (Setup Situation)")
    print("📝 场景：你在互联网大厂，P6冲P7，但老板是风险厌恶型。")
    
    situation_data = {
        "user_id": USER_ID,
        "situation": {
            "career_type": "互联网大厂",
            "current_level": "P6",
            "target_level": "P7",
            "promotion_window": True,
            "stakeholders": [
                {
                    "name": "直属老板",
                    "role": "Line Manager",
                    "style": "风险厌恶型",
                    "relationship": "中立",
                    "influence_level": "High"
                }
            ],
            "current_phase": "冲刺期",
            "personal_goal": "建立靠谱人设，争取晋升",
            "recent_events": []
        }
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/situation/update", json=situation_data, headers=HEADERS)
        print("✅ 局势更新成功：")
        print_response(resp)
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保后端服务已在 localhost:8001 启动。")
        return

    time.sleep(1)

    # 2. Day 1 - 埋下伏笔
    print_step("步骤 2: 第一天 - 建立防御基线 (Day 1)")
    print("📝 事件：项目因第三方延期，你提前在周报预警了。")
    
    day1_fact = {
        "user_id": USER_ID,
        "fact": "项目A因为第三方API不稳定导致延期1天，但我上周五已经在周报里提示过这个风险了。"
    }
    
    print("⏳ AI 正在思考中...")
    resp = requests.post(f"{BASE_URL}/advice/generate", json=day1_fact, headers=HEADERS)
    print("✅ AI 建议：")
    data = resp.json()
    print(f"💡 策略摘要: {data.get('decision', {}).get('strategy_summary')}")
    print(f"🗣️ 话术 (对上): {data.get('narrative', {}).get('boss_version')}")

    time.sleep(2)

    # 3. Day 2 - 遭遇责难
    print_step("步骤 3: 第二天 - 遭遇责难与反击 (Day 2)")
    print("📝 事件：老板因为延期发火了，说进度不可控。")
    
    day2_fact = {
        "user_id": USER_ID,
        "fact": "今天早会老板因为项目A延期发火了，说进度不可控。"
    }
    
    print("⏳ AI 正在检索记忆并生成策略...")
    resp = requests.post(f"{BASE_URL}/advice/generate", json=day2_fact, headers=HEADERS)
    print("✅ AI 建议：")
    data = resp.json()
    print(f"💡 决策判断: {data.get('decision', {}).get('strategic_intent')}")
    print(f"🗣️ 话术 (对上): {data.get('narrative', {}).get('boss_version')}")
    print(f"🧠 调用记忆: {data.get('context_used', {}).get('memory')}")

    time.sleep(2)

    # 4. 记忆整理
    print_step("步骤 4: 周末复盘 - 提取长期洞察 (Consolidation)")
    print("📝 触发记忆整理，提炼老板的行为模式...")
    
    print("⏳ AI 正在归纳总结...")
    resp = requests.post(f"{BASE_URL}/memory/{USER_ID}/consolidate", headers=HEADERS)
    print("✅ 洞察结果：")
    print_response(resp)

    # 5. 查看所有记忆
    print_step("步骤 5: 查看记忆库 (Final Check)")
    resp = requests.get(f"{BASE_URL}/memory/{USER_ID}/all", headers=HEADERS)
    memories = resp.json().get("memories", [])
    print(f"📚 共存储了 {len(memories)} 条记忆片段。")
    
    print("\n🎉 演示结束！这就是一个具备‘长期记忆’的职场 AI。")

if __name__ == "__main__":
    run_demo()

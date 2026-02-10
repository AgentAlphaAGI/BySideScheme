import os
import autogen
from dotenv import load_dotenv

# Load env vars
load_dotenv()

api_key = os.getenv("SILICONFLOW_API_KEY")
base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
model = os.getenv("SILICONFLOW_MODEL", "Pro/zai-org/GLM-4.7")

print(f"Testing with API Key: {api_key[:5]}... (len={len(api_key)})")
print(f"Base URL: {base_url}")
print(f"Model: {model}")

config_list = [
    {
        "model": model,
        "api_key": api_key,
        "base_url": base_url,
        "price": [0, 0],
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "timeout": 120,
}

# Create a simple agent
agent = autogen.AssistantAgent(
    name="test_agent",
    llm_config=llm_config,
    system_message="You are a helpful assistant. Respond with 'Hello World'."
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    code_execution_config=False,
)

try:
    user_proxy.initiate_chat(
        agent,
        message="Say hello."
    )
    print("\n>>> Success! AutoGen is working with SiliconFlow.")
except Exception as e:
    print(f"\n>>> Failed: {e}")

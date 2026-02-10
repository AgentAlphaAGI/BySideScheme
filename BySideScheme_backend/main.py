import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    load_dotenv()
    
    # 检查 API KEY 配置
    silicon_key = os.getenv("SILICONFLOW_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not silicon_key and (not openai_key or openai_key == "your_openai_api_key_here"):
        print("Please set a valid SILICONFLOW_API_KEY or OPENAI_API_KEY in .env file")
        return
        
    print(f">>> 使用模型服务: {'SiliconFlow' if silicon_key else 'OpenAI'}")
    if silicon_key:
        print(f">>> 模型: {os.getenv('SILICONFLOW_MODEL', 'Pro/zai-org/GLM-4.7')}")
    
    print("\n>>> Starting FastAPI Server...")
    # 启动 FastAPI 服务
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    main()

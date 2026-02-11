import json
import os
import urllib.request


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    api_key = os.getenv("BySideScheme_API_KEY")
    if api_key:
        req.add_header("X-API-Key", api_key)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    base_url = os.getenv("BASE_URL", "http://localhost:8001")

    start = _post_json(
        f"{base_url}/simulator/start",
        {
            "user_id": "demo_user_001",
            "user_name": "Me",
            "people": [
                {
                    "kind": "leader",
                    "name": "David",
                    "title": "直属领导",
                    "persona": "控制欲强，喜欢听好话，但关键时刻能扛事。口头禅是'抓手'、'赋能'。",
                    "engine": "deepseek",
                },
                {
                    "kind": "leader",
                    "name": "Sarah",
                    "title": "部门总监",
                    "persona": "结果导向，雷厉风行，不喜欢听借口，只看数据。",
                    "engine": "qwen3",
                },
                {
                    "kind": "colleague",
                    "name": "Alex",
                    "persona": "谨慎务实，擅长补充细节，喜欢把事情拆成可执行清单。",
                    "engine": "glm",
                },
            ],
        },
    )
    session_id = start["session_id"]
    print("session_id:", session_id)

    chat = _post_json(
        f"{base_url}/simulator/chat",
        {
            "session_id": session_id,
            "message": "我想把核心功能上线时间从本周五调整到下周三，原因是关键依赖方不稳定。你们怎么看？",
        },
    )
    print(json.dumps(chat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

import json
import os
import time
import urllib.request


def _request_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    api_key = os.getenv("BySideScheme_API_KEY")
    if api_key:
        req.add_header("X-API-Key", api_key)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    base_url = os.getenv("BASE_URL", "http://localhost:8001")

    start = _request_json(
        "POST",
        f"{base_url}/simulator/start",
        {
            "user_id": "demo_user_001",
            "user_name": "Me",
            "people": [
                {
                    "kind": "leader",
                    "name": "David",
                    "title": "直属领导",
                    "persona": "控制欲强，喜欢听好话，但关键时刻能扛事。",
                    "engine": "deepseek",
                },
                {
                    "kind": "leader",
                    "name": "Sarah",
                    "title": "部门总监",
                    "persona": "结果导向，雷厉风行，不喜欢听借口，只看数据。",
                    "engine": "qwen3",
                },
            ],
        },
    )
    session_id = start["session_id"]
    print("session_id:", session_id)

    job = _request_json(
        "POST",
        f"{base_url}/simulator/jobs/chat",
        {
            "session_id": session_id,
            "message": "我想把核心功能上线时间从本周五调整到下周三，原因是关键依赖方不稳定。你们怎么看？",
        },
    )
    job_id = job["job_id"]
    print("job_id:", job_id)

    printed = 0
    while True:
        result = _request_json("GET", f"{base_url}/simulator/jobs/{job_id}/result")
        msgs = result.get("messages") or []
        while printed < len(msgs):
            m = msgs[printed]
            printed += 1
            print(f"[{m.get('sender')}] {m.get('content')}")

        status = result.get("status")
        if status in ("completed", "failed"):
            print("status:", status)
            if result.get("analysis"):
                print("analysis:", json.dumps(result["analysis"], ensure_ascii=False, indent=2))
            if result.get("error"):
                print("error:", result["error"])
            break
        time.sleep(0.5)


if __name__ == "__main__":
    main()


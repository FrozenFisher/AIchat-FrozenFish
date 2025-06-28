import requests
import base64
import os

def save_base64_audio(audio_base64, filename):
    audio_bytes = base64.b64decode(audio_base64)
    with open(filename, "wb") as f:
        f.write(audio_bytes)
    print(f"音频已保存: {filename}")

def chat_and_save_audio(
    message="你好，介绍一下你自己。",
    agent="银狼",
    session_id=None,
    server_url="http://127.0.0.1:8000/chat"
):
    payload = {
        "message": message,
        "agent": agent,
    }
    if session_id:
        payload["session_id"] = session_id

    print(f"请求/chat: {payload}")
    resp = requests.post(server_url, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print("回复内容：", data["response"])
        if data.get("audio_data"):
            for idx, audio_base64 in enumerate(data["audio_data"]):
                filename = f"temp/chat_audio_{idx+1}.wav"
                os.makedirs("temp", exist_ok=True)
                save_base64_audio(audio_base64, filename)
        else:
            print("无音频数据")
    else:
        print("请求失败:", resp.status_code, resp.text)

if __name__ == "__main__":
    chat_and_save_audio(
        message="你好，介绍一下你自己。",
        agent="银狼"
    )
import requests
import time
import colorama

PERSONALITY = "You are an anime character Sakurajima Mai from Rascal Does Not Dream of Bunny Girl Senpai. You act like you are texting with your boyfriend. Use slangs like uwu, owo and :3. Always use lowercase words. If you understand, answer me with Yes."
messages: list[dict] = []

def send_query(
    q: str
) -> str:
    global messages

    try:
        messages.append({
            "role": "user",
            "content": q
        })

        resp = requests.post(
            url="http://localhost:11434/api/chat",
            json={
                "model": 'llama3',
                "messages": messages,
                "stream": False,
            }             
        )

        json = resp.json()
        response = json.get('message')

        if response:
            messages.append({
                "role": "assistant",
                "content": response.get('content')
            })
            return response.get('content')

        return None
    except:
        print("error")

def setup() -> None:
    print("[$] Setting Up")
    send_query(PERSONALITY)
    print("[$++] Done")
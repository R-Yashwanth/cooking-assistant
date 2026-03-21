import json
import os
from datetime import datetime

HISTORY_FILE = "chat_history.json"

def save_message(role: str, content: str):
    history = get_history()
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

"""
Runs after main.py finishes. Sends the JSON file it produced for each
processed topic back to the Telegram chat that requested them.
"""
import json
import os
import re
import requests
import config

STATE_FILE = "state.json"
TOPICS_FILE = "topics.txt"


def _topic_filename(topic):
    safe = re.sub(r"[^A-Za-z0-9]+", "_", topic).strip("_")
    return safe or "untitled_topic"


def send_document(token, chat_id, path):
    if not os.path.exists(path):
        return
    with open(path, "rb") as f:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendDocument",
                data={"chat_id": chat_id},
                files={"document": f},
                timeout=60,
            )
        except Exception:
            pass


def send_message(token, chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=15,
        )
    except Exception:
        pass


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token or not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    chat_id = state.get("chat_id")
    if not chat_id:
        return

    if not os.path.exists(TOPICS_FILE):
        return
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]

    for topic in topics:
        name = _topic_filename(topic)
        path = os.path.join(config.OUTPUT_DIR, f"{name}.json")
        if os.path.exists(path):
            send_document(token, chat_id, path)
        else:
            send_message(token, chat_id, f"'{topic}' ke liye koi result nahi mila.")

    send_message(token, chat_id, "Scraping complete.")


if __name__ == "__main__":
    main()

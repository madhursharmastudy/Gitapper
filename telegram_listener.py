"""
Runs at the start of every GitHub Actions run.

What it does, in order:
1. Asks Telegram "any new messages since last time?" (using state.json to
   remember where we left off, so old messages aren't reprocessed).
2. Looks for the most recent message that starts with /scrape.
3. If found, writes the topics inside it to topics.txt (one topic per
   line) so main.py can pick them up, and tells the workflow
   (via GITHUB_ENV) that there's work to do.
4. If nothing new, tells the workflow to skip the scraping step.

Message format expected from the user, either:
    /scrape
    Topic one
    Topic two
or on a single line:
    /scrape Topic one | Topic two
"""
import json
import os
import sys
import requests

STATE_FILE = "state.json"
TOPICS_FILE = "topics.txt"
GITHUB_ENV = os.environ.get("GITHUB_ENV")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"offset": 0, "chat_id": None}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def set_env(key, value):
    """Writes KEY=value so later steps in the same workflow run can read
    it as env.KEY (this is how GitHub Actions passes data between steps)."""
    if GITHUB_ENV:
        with open(GITHUB_ENV, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def send_message(token, chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=15,
        )
    except Exception:
        pass


def parse_topics(text):
    body = text[len("/scrape"):].strip()
    if not body:
        return []
    if "\n" in body:
        parts = body.split("\n")
    else:
        parts = body.split("|")
    return [p.strip() for p in parts if p.strip()]


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN not set — add it in GitHub Secrets.")
        set_env("NEW_TOPIC", "false")
        sys.exit(0)

    state = load_state()

    resp = requests.get(
        f"https://api.telegram.org/bot{token}/getUpdates",
        params={"offset": state["offset"], "timeout": 0},
        timeout=20,
    )
    updates = resp.json().get("result", [])

    latest_command = None
    highest_update_id = state["offset"] - 1

    for u in updates:
        highest_update_id = max(highest_update_id, u["update_id"])
        msg = u.get("message") or u.get("edited_message")
        if not msg:
            continue
        text = msg.get("text", "")
        if text.strip().startswith("/scrape"):
            latest_command = msg  # keep the most recent one if several came in

    # Mark every message we saw as read, so unrelated chatter doesn't
    # get checked again next run.
    state["offset"] = highest_update_id + 1

    if not latest_command:
        save_state(state)
        set_env("NEW_TOPIC", "false")
        print("No new /scrape command since last check.")
        return

    chat_id = latest_command["chat"]["id"]
    topics = parse_topics(latest_command.get("text", ""))
    state["chat_id"] = chat_id
    save_state(state)

    if not topics:
        send_message(token, chat_id, "Koi topic nahi mila. Format: /scrape Topic one | Topic two")
        set_env("NEW_TOPIC", "false")
        return

    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(topics) + "\n")

    send_message(token, chat_id, f"{len(topics)} topic mile, scraping shuru:\n" + "\n".join(topics))
    set_env("NEW_TOPIC", "true")
    print(f"New topics found: {topics}")


if __name__ == "__main__":
    main()

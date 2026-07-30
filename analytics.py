import json
import os
import config


def log_topic_result(topic, entry_count):
    """Record topics with low result counts for future re-crawl targeting."""
    record = {}
    if os.path.exists(config.ANALYTICS_LOG):
        with open(config.ANALYTICS_LOG, "r", encoding="utf-8") as f:
            try:
                record = json.load(f)
            except json.JSONDecodeError:
                record = {}

    record[topic] = {
        "entry_count": entry_count,
        "thin": entry_count < 3,
    }

    os.makedirs(os.path.dirname(config.ANALYTICS_LOG), exist_ok=True)
    with open(config.ANALYTICS_LOG, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


def thin_topics():
    if not os.path.exists(config.ANALYTICS_LOG):
        return []
    with open(config.ANALYTICS_LOG, "r", encoding="utf-8") as f:
        record = json.load(f)
    return [t for t, v in record.items() if v["thin"]]

import argparse
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from search import search_topic
from extractor import extract
from classifier import classify_type
from validator import build_entry
from storage.json_writer import save_json
from storage.export_writer import save_csv, save_pdf
from analytics import log_topic_result


def quality_ok(entries):
    if len(entries) < config.MIN_ENTRIES_PER_TOPIC:
        return False
    good = [e for e in entries if e["confidence_score"] >= config.MIN_CONFIDENCE_ACCEPT]
    return len(good) >= config.MIN_ENTRIES_PER_TOPIC


def _fetch_and_build(topic, url):
    raw = extract(url)
    if not raw or not raw.get("text"):
        return None
    entry_type = classify_type(raw.get("title", ""), raw["text"])
    return build_entry(topic, entry_type, raw)


def scrape_once(topic, already_tried):
    """
    URLs are fetched in parallel via a thread pool (network calls are
    I/O-bound, so this is a safe, big speed win over one-at-a-time).
    `already_tried` carries across retry attempts within the same topic so a
    retry doesn't waste time re-fetching URLs that already failed.
    """
    urls = [u for u in search_topic(topic) if u not in already_tried]
    entries = []

    with ThreadPoolExecutor(max_workers=config.MAX_FETCH_WORKERS) as pool:
        futures = {pool.submit(_fetch_and_build, topic, url): url for url in urls}
        for future in as_completed(futures):
            already_tried.add(futures[future])
            entry = future.result()
            if entry:
                entries.append(entry)

    return entries


def process_topic(topic):
    entries = []
    already_tried = set()
    for attempt in range(1, config.MAX_SCRAPE_ATTEMPTS + 1):
        entries.extend(scrape_once(topic, already_tried))
        if quality_ok(entries):
            break
        print(f"    -> attempt {attempt}: {len(entries)} entries, quality not met, retrying")

    log_topic_result(topic, len(entries))
    return entries


def _topic_filename(topic):
    """Turns the topic name into a safe filename, so each topic's output is
    its own file named after that topic."""
    safe = re.sub(r"[^A-Za-z0-9]+", "_", topic).strip("_")
    return safe or "untitled_topic"


def save_topic_output(topic, entries):
    if not entries:
        print("    -> nothing to save")
        return

    name = _topic_filename(topic)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(config.OUTPUT_DIR, f"{name}.json")
    csv_path  = os.path.join(config.OUTPUT_DIR, f"{name}.csv")
    pdf_path  = os.path.join(config.OUTPUT_DIR, f"{name}.pdf")

    total = save_json(entries, json_path)
    print(f"    [JSON] saved ({total} records) -> {json_path}")

    save_csv(entries, csv_path)
    print(f"    [CSV] saved -> {csv_path}")

    save_pdf(entries, pdf_path)
    print(f"    [PDF] saved -> {pdf_path}")


def run(topics):
    for topic in topics:
        print(f"[+] Processing: {topic}")
        entries = process_topic(topic)
        print(f"    -> {len(entries)} entries collected")
        save_topic_output(topic, entries)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("topic", nargs="?", help="Single topic, e.g. 'Kabir Das dohas'")
    ap.add_argument("--batch", help="Path to topics.txt for batch mode")
    args = ap.parse_args()

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            topic_list = [line.strip() for line in f if line.strip()]
    elif args.topic:
        topic_list = [args.topic]
    else:
        ap.error("Provide a topic or --batch topics.txt")

    run(topic_list)

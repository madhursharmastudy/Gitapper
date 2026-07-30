import random
import time
import requests
from bs4 import BeautifulSoup
import config


def _headers():
    return {"User-Agent": random.choice(config.USER_AGENTS)}


def ddg_search(query, max_results=config.MAX_RESULTS_PER_QUERY):
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=_headers(),
        timeout=15,
    )
    soup = BeautifulSoup(resp.text, "html.parser")
    urls = []
    for a in soup.select("a.result__a"):
        href = a.get("href")
        if href and href.startswith("http"):
            urls.append(href)
        if len(urls) >= max_results:
            break
    return urls


def expand_queries(topic):
    return [v.format(topic=topic) for v in config.QUERY_VARIANTS]


def search_topic(topic):
    """Run all query variants for a topic, return deduped URL list."""
    seen = set()
    urls = []
    for q in expand_queries(topic):
        for u in ddg_search(q):
            if u not in seen:
                seen.add(u)
                urls.append(u)
        time.sleep(config.FETCH_DELAY_SECONDS)
    return urls

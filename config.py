MAX_RESULTS_PER_QUERY = 15
FETCH_DELAY_SECONDS = 1.5
MIN_WORDS_POEM = 30
MIN_WORDS_ANALYSIS = 200
MIN_WORDS_DEFAULT = 100

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
]

QUERY_VARIANTS = [
    "{topic}",
    "{topic} biography",
    "{topic} poems analysis",
    "{topic} critical analysis",
    "{topic} literary style",
]

OCR_LANGUAGES = "hin+san+eng"

MIN_ENTRIES_PER_TOPIC = 3
MIN_CONFIDENCE_ACCEPT = 0.5
MAX_SCRAPE_ATTEMPTS = 3

MAX_FETCH_WORKERS = 6  # parallel URL fetches per topic

OUTPUT_DIR = "data/output"  # each topic gets its own <topic_name>.json/.csv/.pdf here
ANALYTICS_LOG = "data/thin_topics.json"

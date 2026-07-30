import re

# Content types matched to what the downstream MCQ pipeline understands
# (writer/poem/essay/literary_device/criticism/movement/era). "work" covers
# novels/plays/longer works that aren't poems.
TYPE_KEYWORDS = {
    "analysis": ["analysis", "critique", "interpretation", "theme", "symbolism", "literary device"],
    "bio": ["biography", "born", "life of", "early life", "career"],
    "movement": ["literary movement", "romanticism", "victorianism", "modernism",
                 "renaissance movement", "school of poetry", "literary period",
                 "movement began", "movement in literature"],
    "era": ["victorian era", "elizabethan era", "medieval period", "romantic era",
            "augustan age", "age of reason", "literary era", "literary age"],
    "work": ["novel", "play", "drama", "epic poem", "collection of poems",
             "anthology", "autobiography", "memoir"],
    "meaning": ["meaning", "summary", "translation", "explanation"],
    "poem": [],  # fallback, checked via structure
}

# Scope is English and Hindi literature only. These markers push subject
# detection to "hindi_literature" — anything else defaults to English.
HINDI_MARKERS = [
    "hindi", "hindi sahitya", "hindi kavita", "urdu", "sanskrit",
    "premchand", "kabir", "tulsidas", "nirala", "mahadevi verma",
    "surdas", "jaishankar prasad", "chhayavad", "hindi literature",
]

# A quick guard against DuckDuckGo returning a completely off-topic (non-
# literature) page for an ambiguous topic name — needs at least one of
# these signal words in the opening chunk of text.
LITERATURE_SIGNALS = [
    "poem", "poetry", "poet", "novel", "author", "writer", "literature",
    "verse", "stanza", "prose", "narrative", "drama", "play",
    "sahitya", "kavi", "kavita", "rachna",
]


def classify_type(title, text):
    lower = (title + " " + text[:500]).lower()
    for t, keywords in TYPE_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return t

    # poem heuristic: short lines, high line-break ratio
    lines = text.split("\n")
    short_lines = [l for l in lines if 0 < len(l.strip()) < 80]
    if len(lines) > 5 and len(short_lines) / max(len(lines), 1) > 0.5:
        return "poem"

    return "general"


def detect_subject(topic, text):
    """Returns 'hindi_literature' or 'english_literature' — the only two
    subjects this pipeline is meant to collect."""
    combined = (topic + " " + text[:1000]).lower()
    if any(m in combined for m in HINDI_MARKERS):
        return "hindi_literature"
    return "english_literature"


def is_literature_relevant(text):
    """Rejects pages that clearly aren't about literature at all, so an
    ambiguous topic name doesn't pull in unrelated scraped content."""
    lower = text[:1000].lower()
    return any(sig in lower for sig in LITERATURE_SIGNALS)


def relevance_score(topic, text):
    """Simple keyword overlap score 0-1."""
    topic_words = set(re.findall(r"\w+", topic.lower()))
    text_words = set(re.findall(r"\w+", text.lower()[:2000]))
    if not topic_words:
        return 0.0
    overlap = topic_words & text_words
    return round(len(overlap) / len(topic_words), 2)

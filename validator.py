import hashlib
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator
import config


class LiteratureEntry(BaseModel):
    topic: str
    type: str
    subject: str = "english_literature"
    title: str = ""
    author: str = ""
    published_date: str = ""
    text: str
    source_url: str
    fetched_at: str = str(date.today())
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    needs_review: bool = True

    @field_validator("text")
    @classmethod
    def not_too_short(cls, v):
        if len(v.split()) < 20:
            raise ValueError("text too short")
        return v


_seen_hashes = set()


def content_hash(text):
    return hashlib.sha256(text[:300].strip().lower().encode("utf-8")).hexdigest()


def is_duplicate(text):
    h = content_hash(text)
    if h in _seen_hashes:
        return True
    _seen_hashes.add(h)
    return False


def min_words_for_type(entry_type):
    if entry_type == "poem":
        return config.MIN_WORDS_POEM
    if entry_type == "analysis":
        return config.MIN_WORDS_ANALYSIS
    return config.MIN_WORDS_DEFAULT


def compute_confidence(entry_type, word_count, relevance):
    """Rough confidence: relevance weighted + length bonus."""
    length_factor = min(word_count / min_words_for_type(entry_type), 1.0)
    score = round(0.6 * relevance + 0.4 * length_factor, 2)
    return score


def build_entry(topic, entry_type, raw):
    word_count = len(raw["text"].split())
    if word_count < min_words_for_type(entry_type):
        return None
    if is_duplicate(raw["text"]):
        return None

    from classifier import relevance_score, is_literature_relevant, detect_subject

    if not is_literature_relevant(raw["text"]):
        return None

    rel = relevance_score(topic, raw["text"])
    if rel < 0.15:  # too irrelevant
        return None

    conf = compute_confidence(entry_type, word_count, rel)
    subject = detect_subject(topic, raw["text"])

    try:
        entry = LiteratureEntry(
            topic=topic,
            type=entry_type,
            subject=subject,
            title=raw.get("title", ""),
            author=raw.get("author", ""),
            published_date=raw.get("published_date", ""),
            text=raw["text"],
            source_url=raw["source_url"],
            relevance_score=rel,
            confidence_score=conf,
            needs_review=conf < 0.5,
        )
        return entry.model_dump()
    except Exception:
        return None

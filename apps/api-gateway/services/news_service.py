"""
India cybersecurity news — RSS feeds + curated resources.
Results cached in memory with 30-minute TTL.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ── Cache ────────────────────────────────────────────────────────

@dataclass
class _CacheEntry:
    data: list
    ts: float = field(default_factory=time.time)

_cache: dict[str, _CacheEntry] = {}
_TTL = 1800  # 30 min


def _get(key: str) -> Optional[list]:
    e = _cache.get(key)
    return e.data if e and (time.time() - e.ts) < _TTL else None


def _set(key: str, data: list) -> None:
    _cache[key] = _CacheEntry(data=data)


# ── RSS sources ──────────────────────────────────────────────────

_FEEDS = [
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
    {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
]

_INDIA_KW = {
    "india", "indian", "cert-in", "rbi", "upi", "aadhaar", "npci",
    "bharat", "delhi", "mumbai", "bangalore", "hyderabad", "chennai",
    "paytm", "phonepe", "google pay", "sbi", "hdfc", "icici",
    "digital india", "meity", "infosys", "tcs", "wipro",
}


async def fetch_news(limit: int = 10, india_only: bool = True) -> list[dict]:
    """Fetch cyber news from RSS. Optionally filter for India relevance."""
    ck = f"news_{limit}_{india_only}"
    cached = _get(ck)
    if cached is not None:
        return cached

    try:
        import feedparser  # optional dependency
    except ImportError:
        logger.warning("feedparser not installed — returning empty news")
        return []

    items: list[dict] = []
    for f in _FEEDS:
        try:
            feed = await asyncio.to_thread(feedparser.parse, f["url"])
            for e in feed.entries[:20]:
                title = e.get("title", "")
                summary = _strip_html(e.get("summary", e.get("description", "")))[:300]
                items.append({
                    "title": title,
                    "summary": summary,
                    "url": e.get("link", ""),
                    "source": f["name"],
                    "published": e.get("published", ""),
                    "india_relevant": _india_match(title, summary),
                })
        except Exception as exc:
            logger.warning("RSS fetch %s failed: %s", f["name"], exc)

    if india_only:
        filtered = [i for i in items if i["india_relevant"]]
        if len(filtered) < 3:
            filtered = items  # fallback to all if too few
    else:
        filtered = items

    result = filtered[:limit]
    _set(ck, result)
    return result


def _india_match(title: str, summary: str) -> bool:
    txt = f"{title} {summary}".lower()
    return any(kw in txt for kw in _INDIA_KW)


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


# ── Curated resources ────────────────────────────────────────────

INDIA_RESOURCES = [
    {
        "title": "National Cyber Crime Reporting Portal",
        "url": "https://cybercrime.gov.in",
        "description": "Report cyber crimes online. For financial fraud, report within the golden hour.",
        "category": "reporting",
    },
    {
        "title": "Cyber Crime Helpline — 1930",
        "url": "tel:1930",
        "description": "24×7 helpline for financial cyber fraud. Immediate freeze of fraudulent transactions.",
        "category": "reporting",
    },
    {
        "title": "CERT-In Advisories",
        "url": "https://www.cert-in.org.in",
        "description": "Official security advisories and vulnerability alerts from India's CERT.",
        "category": "advisory",
    },
    {
        "title": "RBI Ombudsman",
        "url": "https://cms.rbi.org.in",
        "description": "File complaints about unauthorised banking transactions.",
        "category": "reporting",
    },
    {
        "title": "Cyber Surakshit Bharat",
        "url": "https://www.meity.gov.in",
        "description": "MeitY's cybersecurity awareness initiative for government and citizens.",
        "category": "awareness",
    },
]


def get_india_resources() -> list[dict]:
    return INDIA_RESOURCES
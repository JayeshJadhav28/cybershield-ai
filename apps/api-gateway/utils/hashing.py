"""
Input hashing for deduplication and privacy-preserving storage.
"""

import hashlib
from typing import List, Optional


def hash_text_input(
    *parts: str,
    urls: Optional[List[str]] = None,
) -> str:
    """
    Create SHA-256 hash of text input for deduplication.
    Normalizes input before hashing.
    """
    combined = "|".join(
        p.strip().lower() for p in parts if p
    )
    if urls:
        combined += "|" + "|".join(sorted(u.strip().lower() for u in urls if u))

    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def hash_binary_input(data: bytes) -> str:
    """Create SHA-256 hash of binary data."""
    return hashlib.sha256(data).hexdigest()
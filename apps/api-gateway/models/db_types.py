"""
Dialect-aware SQLAlchemy types used across ORM models.

These helpers keep PostgreSQL-native types in production while allowing
SQLite-based tests to create metadata without compilation errors.
"""

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import INET, JSONB


def json_type():
    """Return JSONB on PostgreSQL and JSON on other databases."""
    return JSON().with_variant(JSONB(), "postgresql")


def ip_address_type():
    """Return INET on PostgreSQL and VARCHAR(45) elsewhere."""
    return String(45).with_variant(INET(), "postgresql")

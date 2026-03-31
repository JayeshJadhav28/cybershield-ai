"""
Tests for input hashing utility.
"""

from utils.hashing import hash_text_input, hash_binary_input


class TestHashing:

    def test_text_hash_deterministic(self):
        h1 = hash_text_input("hello", "world")
        h2 = hash_text_input("hello", "world")
        assert h1 == h2

    def test_text_hash_case_insensitive(self):
        h1 = hash_text_input("Hello", "World")
        h2 = hash_text_input("hello", "world")
        assert h1 == h2

    def test_text_hash_strips_whitespace(self):
        h1 = hash_text_input("  hello  ", " world ")
        h2 = hash_text_input("hello", "world")
        assert h1 == h2

    def test_text_hash_different_inputs(self):
        h1 = hash_text_input("hello")
        h2 = hash_text_input("world")
        assert h1 != h2

    def test_text_hash_with_urls(self):
        h1 = hash_text_input("sub", "body", urls=["https://a.com", "https://b.com"])
        h2 = hash_text_input("sub", "body", urls=["https://b.com", "https://a.com"])
        assert h1 == h2  # URLs are sorted

    def test_text_hash_length(self):
        h = hash_text_input("test")
        assert len(h) == 64  # SHA-256 hex digest

    def test_binary_hash_deterministic(self):
        data = b"hello world"
        h1 = hash_binary_input(data)
        h2 = hash_binary_input(data)
        assert h1 == h2

    def test_binary_hash_different_inputs(self):
        h1 = hash_binary_input(b"hello")
        h2 = hash_binary_input(b"world")
        assert h1 != h2

    def test_binary_hash_length(self):
        h = hash_binary_input(b"test")
        assert len(h) == 64
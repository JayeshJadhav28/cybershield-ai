"""
CyberShield AI — Utils Package

Imports are intentionally lazy to avoid pulling in heavy/optional
dependencies (jwt, bcrypt, etc.) when only a subset of utils is needed
(e.g. audio_preprocessing during model training).
"""


def __getattr__(name):
    _security_exports = {
        "hash_password",
        "verify_password",
        "generate_otp",
        "hash_otp",
        "verify_otp",
        "create_access_token",
        "create_refresh_token",
        "decode_token",
        "generate_refresh_token_string",
    }
    if name in _security_exports:
        from utils import security as _sec
        return getattr(_sec, name)
    raise AttributeError(f"module 'utils' has no attribute {name!r}")


__all__ = [
    "hash_password",
    "verify_password",
    "generate_otp",
    "hash_otp",
    "verify_otp",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "generate_refresh_token_string",
]
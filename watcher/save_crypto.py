"""
Shim module — re-exports from crypto.py for compatibility with save_parser.py.
"""
from crypto import (
    MAGIC,
    HEADER_SIZE,
    NONCE_OFF,
    NONCE_SIZE,
    HMAC_OFF,
    HMAC_SIZE,
    DEFAULT_KEY_HEX,
    DEFAULT_KEY,
    parse_header,
    decrypt_payload,
    decrypt_save,
    compute_hmac,
    DecryptionError,
)

import lz4.block


def load_key(hex_text: str) -> bytes:
    key = bytes.fromhex(hex_text)
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes / 64 hex chars")
    return key


def load_lz4_block():
    return lz4.block


def inflate_payload(blob: bytes, key: bytes) -> tuple[dict, bytes, bytes]:
    info, plaintext = decrypt_payload(blob, key)
    raw = lz4.block.decompress(plaintext, uncompressed_size=info["uncompressed_size"])
    return info, plaintext, raw

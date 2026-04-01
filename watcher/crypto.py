"""
Crimson Desert Save File Crypto Pipeline.

Decrypts .save files using:
  1. Fixed 32-byte key (extracted from CrimsonSaveEditor)
  2. 128-byte SAVE header with nonce (16B @ 0x1A), HMAC (32B @ 0x2A)
  3. ChaCha20 (IETF variant, 128-bit nonce) decryption
  4. LZ4 block decompression
  5. Result: PARC binary (Pearl Abyss Reflect Container)

Sources:
  https://github.com/NattKh/CRIMSON-DESERT-SAVE-EDITOR
"""

import hashlib
import hmac as _hmac
import struct
from pathlib import Path

import lz4.block


# ── Constants ─────────────────────────────────────────────────────────────────

MAGIC = b"SAVE"
HEADER_SIZE = 0x80           # 128 bytes
NONCE_OFF   = 0x1A
NONCE_SIZE  = 0x10           # 16 bytes
HMAC_OFF    = 0x2A
HMAC_SIZE   = 0x20           # 32 bytes

# Fixed key — same for all save files
DEFAULT_KEY_HEX = "9a4beb127f9e748b148d6690c25cc9379a315bd56c28af6319fd559f1152ac00"
DEFAULT_KEY = bytes.fromhex(DEFAULT_KEY_HEX)


# ── ChaCha20 (pure-Python, no PyCryptodome needed) ──────────────────────────

def _rotl32(v: int, n: int) -> int:
    return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))


def _quarter_round(s: list[int], a: int, b: int, c: int, d: int) -> None:
    s[a] = (s[a] + s[b]) & 0xFFFFFFFF; s[d] ^= s[a]; s[d] = _rotl32(s[d], 16)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF; s[b] ^= s[c]; s[b] = _rotl32(s[b], 12)
    s[a] = (s[a] + s[b]) & 0xFFFFFFFF; s[d] ^= s[a]; s[d] = _rotl32(s[d], 8)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF; s[b] ^= s[c]; s[b] = _rotl32(s[b], 7)


def _chacha20_block(key32: bytes, counter_nonce16: bytes) -> bytes:
    const_words = struct.unpack("<4I", b"expand 32-byte k")
    key_words = struct.unpack("<8I", key32)
    ctr_words = struct.unpack("<4I", counter_nonce16)
    initial = list(const_words + key_words + ctr_words)
    state = initial.copy()

    for _ in range(10):  # 20 rounds = 10 double-rounds
        _quarter_round(state, 0, 4,  8, 12)
        _quarter_round(state, 1, 5,  9, 13)
        _quarter_round(state, 2, 6, 10, 14)
        _quarter_round(state, 3, 7, 11, 15)
        _quarter_round(state, 0, 5, 10, 15)
        _quarter_round(state, 1, 6, 11, 12)
        _quarter_round(state, 2, 7,  8, 13)
        _quarter_round(state, 3, 4,  9, 14)

    for i in range(16):
        state[i] = (state[i] + initial[i]) & 0xFFFFFFFF
    return struct.pack("<16I", *state)


def _chacha20_xor(key32: bytes, counter_nonce16: bytes, data: bytes) -> bytes:
    words = list(struct.unpack("<4I", counter_nonce16))
    out = bytearray(len(data))
    pos = 0
    while pos < len(data):
        stream = _chacha20_block(key32, struct.pack("<4I", *words))
        chunk = min(64, len(data) - pos)
        for i in range(chunk):
            out[pos + i] = data[pos + i] ^ stream[i]
        pos += chunk
        words[0] = (words[0] + 1) & 0xFFFFFFFF
        if words[0] == 0:
            words[1] = (words[1] + 1) & 0xFFFFFFFF
    return bytes(out)


# ── Header parsing ───────────────────────────────────────────────────────────

class DecryptionError(Exception):
    pass


def parse_header(blob: bytes) -> dict:
    """Parse the 128-byte SAVE header. Returns metadata + raw payload."""
    if len(blob) < HEADER_SIZE:
        raise DecryptionError(f"File too small: {len(blob)} bytes")
    if blob[:4] != MAGIC:
        raise DecryptionError(f"Missing SAVE magic, got: {blob[:4]!r}")

    comp_size = struct.unpack_from("<I", blob, 0x16)[0]
    expected = HEADER_SIZE + comp_size
    if len(blob) != expected:
        raise DecryptionError(
            f"Length mismatch: file={len(blob)} expected={expected}"
        )

    return {
        "version":           struct.unpack_from("<H", blob, 0x04)[0],
        "flags":             struct.unpack_from("<H", blob, 0x06)[0],
        "uncompressed_size": struct.unpack_from("<I", blob, 0x12)[0],
        "payload_size":      comp_size,
        "nonce":             blob[NONCE_OFF:NONCE_OFF + NONCE_SIZE],
        "hmac":              blob[HMAC_OFF:HMAC_OFF + HMAC_SIZE],
        "payload":           blob[HEADER_SIZE:],
        "header":            blob[:HEADER_SIZE],
    }


# ── Decryption pipeline ───────────────────────────────────────────────────────

def compute_hmac(key: bytes, plaintext: bytes) -> bytes:
    return _hmac.new(key, plaintext, hashlib.sha256).digest()


def decrypt_payload(blob: bytes, key: bytes = DEFAULT_KEY) -> tuple[dict, bytes]:
    """Decrypt save file → returns (header_info, plaintext_lz4_payload)."""
    info = parse_header(blob)
    plaintext = _chacha20_xor(key, info["nonce"], info["payload"])
    calc = compute_hmac(key, plaintext)
    info["hmac_ok"] = calc == info["hmac"]
    return info, plaintext


def decrypt_save(raw_bytes: bytes, key: bytes = DEFAULT_KEY) -> bytes:
    """
    Full pipeline: parse header → ChaCha20 decrypt → LZ4 decompress.
    Returns raw PARC binary bytes.
    """
    info, plaintext = decrypt_payload(raw_bytes, key)
    return lz4.block.decompress(plaintext, uncompressed_size=info["uncompressed_size"])


def inspect_save(raw_bytes: bytes, key: bytes = DEFAULT_KEY) -> dict:
    """Debug/analysis — returns header info + HMAC verification."""
    try:
        info, plaintext = decrypt_payload(raw_bytes, key)
        decompressed = lz4.block.decompress(
            plaintext, uncompressed_size=info["uncompressed_size"]
        )
        return {
            "raw_size": len(raw_bytes),
            "version": info["version"],
            "flags": info["flags"],
            "payload_size": info["payload_size"],
            "uncompressed_size": info["uncompressed_size"],
            "hmac_ok": info["hmac_ok"],
            "nonce_hex": info["nonce"].hex(),
            "decompressed_size": len(decompressed),
            "decompressed_header_hex": decompressed[:64].hex(),
            "error": None,
        }
    except Exception as e:
        return {"error": str(e), "raw_size": len(raw_bytes)}

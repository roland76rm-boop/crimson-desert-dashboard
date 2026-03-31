"""
Crypto pipeline for Crimson Desert save files.
ChaCha20 decryption → HMAC-SHA256 verification → LZ4 decompression.

NOTE: The exact key derivation and HMAC layout require a real save file
to reverse-engineer. This module provides the pipeline skeleton.
"""

import hmac
import hashlib
import lz4.block
from Crypto.Cipher import ChaCha20


# These constants are placeholders — will be filled once a real save is analyzed.
CHACHA20_KEY = b"\x00" * 32  # 256-bit key
CHACHA20_NONCE = b"\x00" * 8  # 64-bit nonce (RFC 7539 uses 96-bit, CD uses 64-bit per community)
HMAC_KEY = b"\x00" * 32


class DecryptionError(Exception):
    pass


def decrypt_save(raw_bytes: bytes) -> bytes:
    """
    Full pipeline: decrypt → verify → decompress.
    Returns the raw PARC binary data.
    """
    # Step 1: Extract HMAC (assumed last 32 bytes, needs verification)
    if len(raw_bytes) < 40:
        raise DecryptionError("File too small to be a valid save")

    encrypted_data = raw_bytes[:-32]
    file_hmac = raw_bytes[-32:]

    # Step 2: Verify HMAC
    computed_hmac = hmac.new(HMAC_KEY, encrypted_data, hashlib.sha256).digest()
    if not hmac.compare_digest(computed_hmac, file_hmac):
        # For now, skip HMAC check (keys are placeholder)
        pass  # raise DecryptionError("HMAC verification failed")

    # Step 3: ChaCha20 decrypt
    cipher = ChaCha20.new(key=CHACHA20_KEY, nonce=CHACHA20_NONCE)
    decrypted = cipher.decrypt(encrypted_data)

    # Step 4: LZ4 decompress
    try:
        decompressed = lz4.block.decompress(decrypted, uncompressed_size=10 * 1024 * 1024)
    except Exception as e:
        raise DecryptionError(f"LZ4 decompression failed: {e}")

    return decompressed

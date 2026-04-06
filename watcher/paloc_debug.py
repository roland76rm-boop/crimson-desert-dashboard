"""Dump PALOC structure to understand the binary format."""
import os, sys
from pathlib import Path

paloc_path = Path(__file__).parent / "data" / "localizationstring_ger.paloc"
if not paloc_path.exists():
    print(f"FEHLER: {paloc_path} nicht gefunden!")
    print("Zuerst extract_german.py ausfuehren!")
    sys.exit(1)

data = paloc_path.read_bytes()
print(f"Dateigroesse: {len(data):,} Bytes")
print()

# Show first 200 bytes as hex + ASCII
print("=== Erste 200 Bytes ===")
for i in range(0, min(200, len(data)), 16):
    hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_part = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in data[i:i+16])
    print(f"  {i:6d} | {hex_part:<48s} | {ascii_part}")

# Split on NUL bytes and show first 60 segments
print()
print("=== Erste 60 NUL-getrennte Segmente ===")
segments = []
start = 12  # skip header
seg_start = start
for i in range(start, min(len(data), 50000)):
    if data[i] == 0:
        seg = data[seg_start:i]
        if seg:  # skip empty segments (multiple NULs)
            segments.append((seg_start, seg))
        seg_start = i + 1

    if len(segments) >= 60:
        break

for idx, (offset, seg) in enumerate(segments):
    # Show as text if mostly printable, else as hex
    try:
        text = seg.decode('utf-8')
        printable = sum(1 for c in text if c.isprintable()) / max(len(text), 1)
        if printable > 0.7:
            display = text[:80]
            if len(text) > 80:
                display += "..."
        else:
            display = seg[:40].hex()
    except UnicodeDecodeError:
        display = seg[:40].hex()

    print(f"  [{idx:3d}] @{offset:6d} ({len(seg):4d}B): {display}")

# Show byte values around first few record boundaries
print()
print("=== Bytes um erste Rekord-Grenzen ===")
nul_positions = []
for i in range(12, min(len(data), 5000)):
    if data[i] == 0:
        nul_positions.append(i)
    if len(nul_positions) >= 20:
        break

for nul_pos in nul_positions[:15]:
    context_start = max(0, nul_pos - 5)
    context_end = min(len(data), nul_pos + 15)
    before = ' '.join(f'{b:02x}' for b in data[context_start:nul_pos])
    after = ' '.join(f'{b:02x}' for b in data[nul_pos:context_end])
    ascii_after = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in data[nul_pos:context_end])
    print(f"  NUL @{nul_pos}: ...{before} | {after} | {ascii_after}")

input("\nDruecke Enter...")

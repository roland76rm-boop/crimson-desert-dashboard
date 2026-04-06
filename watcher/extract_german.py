"""
Extract German localization from Crimson Desert PAZ archives.

Run on the Gaming-PC:
  cd C:\\Tools\\watcher
  .venv\\Scripts\\python extract_german.py

Extracts localizationstring_ger.paloc from folder 0027,
parses the PALOC format, and saves german_strings.json.
"""

import os
import sys
import json
import struct
from pathlib import Path

# ── PAZ crypto (pure Python, no extra deps) ──────────────────────────

def _rot(v, k):
    return ((v << k) | (v >> (32 - k))) & 0xFFFFFFFF

def _add(a, b):
    return (a + b) & 0xFFFFFFFF

def _sub(a, b):
    return (a - b) & 0xFFFFFFFF

def hashlittle(data: bytes, initval: int = 0) -> int:
    length = len(data)
    a = b = c = _add(0xDEADBEEF + length, initval)
    off = 0
    while length > 12:
        a = _add(a, struct.unpack_from('<I', data, off)[0])
        b = _add(b, struct.unpack_from('<I', data, off + 4)[0])
        c = _add(c, struct.unpack_from('<I', data, off + 8)[0])
        a = _sub(a, c); a ^= _rot(c, 4);  c = _add(c, b)
        b = _sub(b, a); b ^= _rot(a, 6);  a = _add(a, c)
        c = _sub(c, b); c ^= _rot(b, 8);  b = _add(b, a)
        a = _sub(a, c); a ^= _rot(c, 16); c = _add(c, b)
        b = _sub(b, a); b ^= _rot(a, 19); a = _add(a, c)
        c = _sub(c, b); c ^= _rot(b, 4);  b = _add(b, a)
        off += 12; length -= 12
    tail = data[off:] + b'\x00' * 12
    if length >= 12:   c = _add(c, struct.unpack_from('<I', tail, 8)[0])
    elif length >= 9:
        v = struct.unpack_from('<I', tail, 8)[0]
        c = _add(c, v & (0xFFFFFFFF >> (8 * (12 - length))))
    if length >= 8:    b = _add(b, struct.unpack_from('<I', tail, 4)[0])
    elif length >= 5:
        v = struct.unpack_from('<I', tail, 4)[0]
        b = _add(b, v & (0xFFFFFFFF >> (8 * (8 - length))))
    if length >= 4:    a = _add(a, struct.unpack_from('<I', tail, 0)[0])
    elif length >= 1:
        v = struct.unpack_from('<I', tail, 0)[0]
        a = _add(a, v & (0xFFFFFFFF >> (8 * (4 - length))))
    elif length == 0:  return c
    c ^= b; c = _sub(c, _rot(b, 14))
    a ^= c; a = _sub(a, _rot(c, 11))
    b ^= a; b = _sub(b, _rot(a, 25))
    c ^= b; c = _sub(c, _rot(b, 16))
    a ^= c; a = _sub(a, _rot(c, 4))
    b ^= a; b = _sub(b, _rot(a, 14))
    c ^= b; c = _sub(c, _rot(b, 24))
    return c


HASH_INITVAL = 0x000C5EDE
IV_XOR = 0x60616263
XOR_DELTAS = [0x00000000, 0x0A0A0A0A, 0x0C0C0C0C, 0x06060606,
              0x0E0E0E0E, 0x0A0A0A0A, 0x06060606, 0x02020202]


def derive_key_iv(filename: str) -> tuple[bytes, bytes]:
    basename = os.path.basename(filename).lower()
    seed = hashlittle(basename.encode('utf-8'), HASH_INITVAL)
    iv = struct.pack('<I', seed) * 4
    key_base = seed ^ IV_XOR
    key = b''.join(struct.pack('<I', key_base ^ d) for d in XOR_DELTAS)
    return key, iv


# Pure Python ChaCha20
def _rotl32(v, n):
    return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))

def _qr(s, a, b, c, d):
    s[a] = (s[a]+s[b])&0xFFFFFFFF; s[d]^=s[a]; s[d]=_rotl32(s[d],16)
    s[c] = (s[c]+s[d])&0xFFFFFFFF; s[b]^=s[c]; s[b]=_rotl32(s[b],12)
    s[a] = (s[a]+s[b])&0xFFFFFFFF; s[d]^=s[a]; s[d]=_rotl32(s[d],8)
    s[c] = (s[c]+s[d])&0xFFFFFFFF; s[b]^=s[c]; s[b]=_rotl32(s[b],7)

def chacha20_block(key32, cn16):
    cw = struct.unpack("<4I", b"expand 32-byte k")
    kw = struct.unpack("<8I", key32)
    nw = struct.unpack("<4I", cn16)
    ini = list(cw + kw + nw); s = ini.copy()
    for _ in range(10):
        _qr(s,0,4,8,12); _qr(s,1,5,9,13); _qr(s,2,6,10,14); _qr(s,3,7,11,15)
        _qr(s,0,5,10,15); _qr(s,1,6,11,12); _qr(s,2,7,8,13); _qr(s,3,4,9,14)
    for i in range(16): s[i]=(s[i]+ini[i])&0xFFFFFFFF
    return struct.pack("<16I", *s)

def chacha20_xor(key32, cn16, data):
    words = list(struct.unpack("<4I", cn16))
    out = bytearray(len(data)); pos = 0
    while pos < len(data):
        stream = chacha20_block(key32, struct.pack("<4I", *words))
        chunk = min(64, len(data)-pos)
        for i in range(chunk): out[pos+i] = data[pos+i] ^ stream[i]
        pos += chunk
        words[0] = (words[0]+1)&0xFFFFFFFF
        if words[0]==0: words[1]=(words[1]+1)&0xFFFFFFFF
    return bytes(out)


# ── LZ4 decompression ───────────────────────────────────────────────

try:
    import lz4.block
    def lz4_decompress(data, orig_size):
        return lz4.block.decompress(data, uncompressed_size=orig_size)
except ImportError:
    def lz4_decompress(data, orig_size):
        raise RuntimeError("lz4 nicht installiert — pip install lz4")


# ── PAMT Parser ──────────────────────────────────────────────────────

class PazEntry:
    def __init__(self, path, paz_file, offset, comp_size, orig_size, flags, paz_index):
        self.path = path
        self.paz_file = paz_file
        self.offset = offset
        self.comp_size = comp_size
        self.orig_size = orig_size
        self.flags = flags
        self.paz_index = paz_index

    @property
    def compressed(self):
        return self.comp_size != self.orig_size

    @property
    def compression_type(self):
        return (self.flags >> 16) & 0x0F


def parse_pamt(pamt_path, paz_dir=None):
    with open(pamt_path, 'rb') as f:
        data = f.read()
    if paz_dir is None:
        paz_dir = os.path.dirname(pamt_path) or '.'
    pamt_stem = os.path.splitext(os.path.basename(pamt_path))[0]

    off = 4  # skip magic
    paz_count = struct.unpack_from('<I', data, off)[0]; off += 4
    off += 8  # hash + zero
    for i in range(paz_count):
        off += 8
        if i < paz_count - 1: off += 4

    folder_size = struct.unpack_from('<I', data, off)[0]; off += 4
    folder_end = off + folder_size
    folder_prefix = ""
    while off < folder_end:
        parent = struct.unpack_from('<I', data, off)[0]
        slen = data[off + 4]
        name = data[off + 5:off + 5 + slen].decode('utf-8', errors='replace')
        if parent == 0xFFFFFFFF:
            folder_prefix = name
        off += 5 + slen

    node_size = struct.unpack_from('<I', data, off)[0]; off += 4
    node_start = off
    nodes = {}
    while off < node_start + node_size:
        rel = off - node_start
        parent = struct.unpack_from('<I', data, off)[0]
        slen = data[off + 4]
        name = data[off + 5:off + 5 + slen].decode('utf-8', errors='replace')
        nodes[rel] = (parent, name)
        off += 5 + slen

    def build_path(node_ref):
        parts = []
        cur = node_ref
        while cur != 0xFFFFFFFF and len(parts) < 64:
            if cur not in nodes: break
            p, n = nodes[cur]
            parts.append(n); cur = p
        return ''.join(reversed(parts))

    folder_count = struct.unpack_from('<I', data, off)[0]; off += 4
    off += 4
    off += folder_count * 16

    entries = []
    while off + 20 <= len(data):
        node_ref, paz_offset, comp_size, orig_size, flags = struct.unpack_from('<IIIII', data, off)
        off += 20
        paz_index = flags & 0xFF
        node_path = build_path(node_ref)
        full_path = f"{folder_prefix}/{node_path}" if folder_prefix else node_path
        paz_num = int(pamt_stem) + paz_index
        paz_file = os.path.join(paz_dir, f"{paz_num}.paz")
        entries.append(PazEntry(full_path, paz_file, paz_offset, comp_size, orig_size, flags, paz_index))
    return entries


def extract_entry(entry):
    """Extract and decompress a single PAZ entry, return bytes."""
    read_size = entry.comp_size if entry.compressed else entry.orig_size
    with open(entry.paz_file, 'rb') as f:
        f.seek(entry.offset)
        data = f.read(read_size)

    # PALOC files may also be encrypted (like XML), try with filename-based key
    if entry.path.lower().endswith(('.xml', '.paloc')):
        basename = os.path.basename(entry.path)
        key, iv = derive_key_iv(basename)
        data = chacha20_xor(key, iv, data)

    if entry.compressed and entry.compression_type == 2:
        data = lz4_decompress(data, entry.orig_size)

    return data


# ── PALOC Parser ─────────────────────────────────────────────────────

def parse_paloc(data: bytes) -> dict[str, str]:
    """Parse a PALOC localization file (length-prefixed binary format).

    Format (reverse-engineered from hex dump):
      Header:  [uint32 version] [uint32 reserved]  = 8 bytes
      Record:  [uint32 key_len] [key_bytes] [uint32 val_len] [val_bytes]
      Between records: 8 bytes trailer [uint32 type] [uint32 zero]

    First record starts immediately after header (no trailer prefix).
    Returns dict of {key: value_text}.
    """
    print(f"  PALOC Groesse: {len(data):,} Bytes")

    if len(data) < 12:
        return {}

    version = struct.unpack_from('<I', data, 0)[0]
    reserved = struct.unpack_from('<I', data, 4)[0]
    print(f"  Header: version={version}, reserved={reserved}")

    strings = {}
    off = 8  # skip 8-byte header
    first = True
    errors = 0

    while off + 8 < len(data):
        # Skip 8-byte trailer/gap between records (not before first)
        if not first:
            off += 8
        first = False

        if off + 4 > len(data):
            break

        # Read key
        key_len = struct.unpack_from('<I', data, off)[0]
        off += 4

        if key_len > 200 or key_len == 0:
            errors += 1
            if errors > 100:
                break
            # Try to recover: step back and skip 1 byte
            off -= 3
            first = True  # don't skip trailer on next iteration
            continue

        if off + key_len + 4 > len(data):
            break

        key = data[off:off + key_len].decode('utf-8', errors='replace')
        off += key_len

        # Read value
        val_len = struct.unpack_from('<I', data, off)[0]
        off += 4

        if val_len > 100000:
            errors += 1
            if errors > 100:
                break
            continue

        if off + val_len > len(data):
            break

        value = data[off:off + val_len].decode('utf-8', errors='replace')
        off += val_len

        strings[key] = value

    print(f"  Records geparst: {len(strings):,}")
    if errors > 0:
        print(f"  Uebersprungene Fehler: {errors}")

    return strings


# ── Main ─────────────────────────────────────────────────────────────

def extract_paloc(game_dir: str, folder_num: str) -> bytes:
    """Extract the .paloc file from a language PAZ folder. Returns raw bytes."""
    folder_path = os.path.join(game_dir, folder_num)
    pamt_file = os.path.join(folder_path, "0.pamt")

    if not os.path.isfile(pamt_file):
        raise FileNotFoundError(f"{pamt_file} nicht gefunden")

    entries = parse_pamt(pamt_file, paz_dir=folder_path)
    paloc_entries = [e for e in entries if e.path.lower().endswith('.paloc')]

    if not paloc_entries:
        raise ValueError(f"Keine .paloc Datei in {folder_num}")

    return extract_entry(paloc_entries[0])


def main():
    game_dir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Crimson Desert"
    if not os.path.isdir(game_dir):
        print("Spielverzeichnis nicht gefunden, bitte eingeben:")
        game_dir = input("> ").strip().strip('"')

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"Spielverzeichnis: {game_dir}")
    print()

    # ── Step 1: Extract German PALOC (0027) ──
    print("=== Extrahiere Deutsche Lokalisierung (0027) ===")
    ger_data = extract_paloc(game_dir, "0027")
    print(f"  Extrahiert: {len(ger_data):,} Bytes")
    (data_dir / "localizationstring_ger.paloc").write_bytes(ger_data)

    print("\n=== Parse Deutsches PALOC ===")
    ger_strings = parse_paloc(ger_data)
    print(f"  → {len(ger_strings):,} deutsche Strings")

    # ── Step 2: Extract English PALOC (0020) for key mapping ──
    print("\n=== Extrahiere Englische Lokalisierung (0020) ===")
    eng_data = extract_paloc(game_dir, "0020")
    print(f"  Extrahiert: {len(eng_data):,} Bytes")

    print("\n=== Parse Englisches PALOC ===")
    eng_strings = parse_paloc(eng_data)
    print(f"  → {len(eng_strings):,} englische Strings")

    # ── Step 3: Build English→German translation map ──
    print("\n=== Baue Uebersetzungstabelle ===")
    # Both PALOCs share the same localization keys
    # Map: english_text → german_text (for matching with item_names.json)
    eng_to_ger = {}
    for key in ger_strings:
        if key in eng_strings:
            eng_text = eng_strings[key]
            ger_text = ger_strings[key]
            if eng_text and ger_text and eng_text != ger_text:
                eng_to_ger[eng_text] = ger_text

    print(f"  {len(eng_to_ger):,} Uebersetzungen (EN→DE)")

    # ── Step 4: Translate item_names.json ──
    print("\n=== Uebersetze Item-Namen ===")
    item_file = data_dir / "item_names.json"
    if item_file.exists():
        with open(item_file, 'r', encoding='utf-8') as f:
            item_data = json.load(f)

        items = item_data.get("items", item_data) if isinstance(item_data, dict) else item_data
        translated = 0
        for item in items:
            eng_name = item.get("name", "")
            if eng_name in eng_to_ger:
                item["name_de"] = eng_to_ger[eng_name]
                translated += 1

        print(f"  {translated} / {len(items)} Items uebersetzt")

        # Save translated items
        out_path = data_dir / "item_names_de.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({"items": items} if isinstance(item_data, dict) and "items" in item_data else items,
                      f, indent=2, ensure_ascii=False)
        print(f"  Gespeichert: {out_path}")

        # Show examples
        print("\n  Beispiele:")
        count = 0
        for item in items:
            if "name_de" in item and count < 15:
                print(f"    {item['name']} → {item['name_de']}")
                count += 1
    else:
        print(f"  WARNUNG: {item_file} nicht gefunden!")

    # ── Step 5: Translate quest_names.json ──
    print("\n=== Uebersetze Quest-Namen ===")
    quest_file = data_dir / "quest_names.json"
    if quest_file.exists():
        with open(quest_file, 'r', encoding='utf-8') as f:
            quest_data = json.load(f)

        quests = quest_data if isinstance(quest_data, list) else quest_data.get("quests", [])
        translated = 0
        for q in quests:
            for field in ["name", "display"]:
                eng_name = q.get(field, "")
                if eng_name in eng_to_ger:
                    q[f"{field}_de"] = eng_to_ger[eng_name]
                    translated += 1

        print(f"  {translated} Quest-Felder uebersetzt")

        out_path = data_dir / "quest_names_de.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(quests, f, indent=2, ensure_ascii=False)
        print(f"  Gespeichert: {out_path}")

        print("\n  Beispiele:")
        count = 0
        for q in quests:
            if "display_de" in q and count < 10:
                print(f"    {q.get('display', q.get('name', '?'))} → {q['display_de']}")
                count += 1
    else:
        print(f"  WARNUNG: {quest_file} nicht gefunden!")

    # ── Step 6: Save raw string files ──
    print("\n=== Speichere Rohdaten ===")

    out_ger = data_dir / "german_strings.json"
    with open(out_ger, 'w', encoding='utf-8') as f:
        json.dump(ger_strings, f, indent=2, ensure_ascii=False)
    print(f"  {out_ger} ({len(ger_strings):,} Eintraege)")

    out_eng = data_dir / "english_strings.json"
    with open(out_eng, 'w', encoding='utf-8') as f:
        json.dump(eng_strings, f, indent=2, ensure_ascii=False)
    print(f"  {out_eng} ({len(eng_strings):,} Eintraege)")

    out_map = data_dir / "translation_en_de.json"
    with open(out_map, 'w', encoding='utf-8') as f:
        json.dump(eng_to_ger, f, indent=2, ensure_ascii=False)
    print(f"  {out_map} ({len(eng_to_ger):,} Eintraege)")

    # ── Summary ──
    print("\n" + "=" * 60)
    print("FERTIG!")
    print(f"  Deutsche Strings:    {len(ger_strings):,}")
    print(f"  Englische Strings:   {len(eng_strings):,}")
    print(f"  Uebersetzungen:      {len(eng_to_ger):,}")
    print("=" * 60)

    input("\nDruecke Enter zum Beenden...")


if __name__ == "__main__":
    main()

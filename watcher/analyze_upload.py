"""
Upload + analysis server for Crimson Desert save files.
Run: python3 analyze_upload.py
Open: http://192.168.0.51:8888
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from crypto import decrypt_save, inspect_save, DecryptionError
from parser import parse_parc


def analyze_save(raw: bytes) -> dict:
    """Decrypt + parse a save file, return full analysis."""
    results = {
        "raw_size": len(raw),
        "success": False,
        "error": None,
        "header_info": None,
        "parsed_data": None,
    }

    # Step 1: Inspect (header info + HMAC check)
    info = inspect_save(raw)
    results["header_info"] = info

    if info.get("error"):
        results["error"] = info["error"]
        return results

    # Step 2: Full decrypt + decompress
    try:
        parc_data = decrypt_save(raw)
        results["decompressed_size"] = len(parc_data)
    except DecryptionError as e:
        results["error"] = str(e)
        return results
    except Exception as e:
        results["error"] = f"Decrypt/decompress failed: {e}"
        return results

    # Step 3: Parse PARC
    try:
        parsed = parse_parc(parc_data)
        results["parsed_data"] = parsed
        results["success"] = True
    except Exception as e:
        results["error"] = f"PARC parse failed: {e}"
        # Still save the decompressed data for debugging
        _save_decompressed(parc_data)
        return results

    _save_decompressed(parc_data)
    return results


def _save_decompressed(data: bytes):
    path = Path(__file__).parent / "test_save_decompressed.bin"
    path.write_bytes(data)


UPLOAD_HTML = """<!DOCTYPE html>
<html><head><title>CD Save Analyzer</title>
<style>
body { font-family: monospace; background: #0d1117; color: #e6edf3; padding: 40px; max-width: 800px; margin: 0 auto; }
h1 { color: #c9a227; }
.upload { border: 2px dashed #30363d; border-radius: 12px; padding: 40px; text-align: center; margin: 20px 0; }
button { background: #c9a22730; color: #c9a227; border: 1px solid #c9a22740; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; }
pre { background: #161b22; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 12px; white-space: pre-wrap; }
.ok { color: #4ade80; } .err { color: #f87171; }
</style></head><body>
<h1>Crimson Desert Save Analyzer</h1>
<p>Lade die <code>save.save</code> Datei hoch (aus AppData\\Local\\Pearl Abyss\\CD\\save\\).</p>
<form method="POST" enctype="multipart/form-data" action="/analyze">
<div class="upload">
<input type="file" name="savefile" accept="*">
<br><br>
<button type="submit">Analysieren</button>
</div>
</form>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(UPLOAD_HTML.encode())

    def do_POST(self):
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self.send_response(400)
            self.end_headers()
            return

        boundary = content_type.split("boundary=")[1].encode()
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)

        parts = body.split(b"--" + boundary)
        file_data = None
        for part in parts:
            if b"filename=" in part:
                idx = part.find(b"\r\n\r\n")
                if idx >= 0:
                    file_data = part[idx + 4:]
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    break

        if not file_data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Keine Datei gefunden")
            return

        # Save raw file
        save_path = Path(__file__).parent / "test_save.save"
        save_path.write_bytes(file_data)

        # Analyze
        result = analyze_save(file_data)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        ok = result.get("success", False)
        status_class = "ok" if ok else "err"
        status_text = "ERFOLGREICH" if ok else "FEHLGESCHLAGEN"

        # Build detailed HTML
        info = result.get("header_info", {})
        parsed = result.get("parsed_data")

        char_html = ""
        equip_html = ""
        inv_html = ""
        quest_html = ""

        if parsed:
            char = parsed.get("character", {})
            char_html = f"""
            <h2>Charakter</h2>
            <pre>Level: {char.get('level', '?')}
HP: {char.get('currentHp', '?')} | MP: {char.get('currentMp', '?')}
Character Key: {char.get('characterKey', '?')}
Faction Key: {char.get('factionKey', '?')}</pre>"""

            equip = parsed.get("equipment", [])
            if equip:
                rows = "\n".join(
                    f"  [{e['slot_name']:16s}] {e['name']:30s} (Sharp: {e['sharpness']}, Endur: {e['endurance']}, Enchant: {e['enchant']})"
                    for e in equip
                )
                equip_html = f"<h2>Equipment ({len(equip)})</h2><pre>{rows}</pre>"

            inv = parsed.get("inventory", [])
            if inv:
                rows = "\n".join(
                    f"  {i['name']:30s} x{i['stack']} ({i['category']})"
                    for i in inv
                )
                inv_html = f"<h2>Inventar ({len(inv)})</h2><pre>{rows}</pre>"

            quests = parsed.get("quests", {})
            missions = parsed.get("missions", {})
            quest_html = f"""
            <h2>Quests & Missionen</h2>
            <pre>Quests: {quests.get('total', 0)}
Missionen: {missions.get('total', 0)}
Schema: {parsed.get('schema_info', {}).get('type_count', '?')} Typen, {parsed.get('schema_info', {}).get('object_count', '?')} Objekte</pre>"""

        html = f"""<!DOCTYPE html>
<html><head><title>Analyse-Ergebnis</title>
<style>
body {{ font-family: monospace; background: #0d1117; color: #e6edf3; padding: 40px; max-width: 1000px; margin: 0 auto; }}
h1 {{ color: #c9a227; }}
h2 {{ color: #8b8b8b; font-size: 14px; margin-top: 24px; }}
pre {{ background: #161b22; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 11px; white-space: pre-wrap; max-height: 60vh; overflow-y: auto; }}
.ok {{ color: #4ade80; font-weight: bold; font-size: 18px; }}
.err {{ color: #f87171; font-weight: bold; font-size: 18px; }}
a {{ color: #c9a227; }}
</style></head><body>
<h1>Analyse-Ergebnis</h1>
<p class="{status_class}">{status_text}</p>
{f'<p style="color:#f87171">Fehler: {result["error"]}</p>' if result.get("error") else ''}

<h2>Datei-Info</h2>
<pre>Groesse: {result['raw_size']:,} Bytes
Version: {info.get('version', '?')}
Flags: {info.get('flags', '?')}
Payload (encrypted): {info.get('payload_size', '?'):,} Bytes
PARC (decompressed): {info.get('uncompressed_size', '?'):,} Bytes
HMAC OK: {info.get('hmac_ok', '?')}
Nonce: {info.get('nonce_hex', '?')}</pre>

{char_html}
{equip_html}
{inv_html}
{quest_html}

<h2>Rohdaten (JSON)</h2>
<pre>{json.dumps(result, indent=2, default=str, ensure_ascii=False)[:10000]}</pre>
<br><a href="/">Neue Datei analysieren</a>
</body></html>"""
        self.wfile.write(html.encode())

    def log_message(self, fmt, *args):
        print(f"[UPLOAD] {args[0]}")


if __name__ == "__main__":
    port = 8888
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Save Analyzer laeuft auf http://192.168.0.51:{port}")
    print("Echte Pipeline: SAVE Header -> ChaCha20 -> LZ4 -> PARC Parser")
    print("Ctrl+C zum Beenden.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")

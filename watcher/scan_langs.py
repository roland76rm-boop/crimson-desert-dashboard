"""Scan all language PAZ folders and show ONLY the .paloc filename in each."""
import os
from extract_german import parse_pamt

GAME_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Crimson Desert"

for d in sorted(os.listdir(GAME_DIR)):
    pamt = os.path.join(GAME_DIR, d, "0.pamt")
    if not os.path.isfile(pamt):
        continue
    try:
        entries = parse_pamt(pamt, os.path.join(GAME_DIR, d))
        palocs = [e.path for e in entries if e.path.lower().endswith('.paloc')]
        if palocs:
            print(f"  {d}: {palocs}")
        else:
            print(f"  {d}: (keine .paloc Datei)")
    except Exception as e:
        print(f"  {d}: FEHLER - {e}")

# Crimson Desert Dashboard

## Übersicht
Save-File-Parser-basiertes Dashboard für Crimson Desert.
Architektur: File-Watcher (Gaming-PC) → FastAPI (VPS) → React/Vite (Vercel)

## Stack
- Backend: FastAPI + PostgreSQL (VPS 152.53.0.21, Port 3011)
- Frontend: React + TypeScript + Vite + Tailwind + Recharts (Vercel)
- Watcher: Python + ChaCha20/LZ4/PARC (Gaming-PC)
- Domain: cd.haus543.at (Backend API), crimsondesert.haus543.at (Frontend)

## Verzeichnisstruktur
/backend   — FastAPI Backend
/frontend  — React/Vite Frontend
/watcher   — Python File-Watcher + Save-Parser

## Save-File Format (reverse-engineered)
- **Header**: 128 Bytes, Magic `SAVE`, Nonce (16B @ 0x1A), HMAC-SHA256 (32B @ 0x2A)
- **Encryption**: ChaCha20 mit fixem 32-Byte Key
- **Compression**: LZ4 Block
- **Binary Format**: PARC (Pearl Abyss Reflect Container) — 69 Typen, 94 Objekte
- **Key**: `9a4beb127f9e748b148d6690c25cc9379a315bd56c28af6319fd559f1152ac00`
- **Quelle**: Decompiled aus CrimsonSaveEditor (PyInstaller → save_crypto.py + save_parser.py)

## Watcher Pipeline
```
save.save → parse_header() → ChaCha20 decrypt → LZ4 decompress → PARC parse → JSON → API upload
```

### Dateien
- `crypto.py` — ChaCha20 Entschlüsselung (pure Python, kein PyCryptodome nötig)
- `save_crypto.py` — Kompatibilitäts-Shim für save_parser.py
- `save_parser.py` — PARC Binary Parser (1595 Zeilen, aus CrimsonSaveEditor extrahiert)
- `parser.py` — High-Level Wrapper: PARC → strukturiertes Dict für Dashboard
- `watcher.py` — File-Watcher mit Watchdog + API Upload
- `analyze_upload.py` — Web-basierter Save-Analyzer (Port 8888)
- `data/` — Item-, Quest-, Missions-Datenbanken (6022 Items, Quests, Missionen)

### Geparste Daten
- **Character**: Level, HP, MP, CharacterKey, FactionKey
- **Equipment**: 11 Slots (Waffe, Schild, Bogen, Rüstung, Handschuhe, Stiefel, Umhang, etc.)
- **Inventar**: Items mit Stack-Count, Kategorie
- **Quests**: 615 Quest-States, 2981 Missions-States
- **Schema**: 69 PARC-Typen, 94 Objekte

## Deployment
- **VPS Backend:** ssh root@152.53.0.21, Repo: /root/projects/Crimson_Desert/
  - pm2 Name: `cd-backend`, Start: `/root/projects/Crimson_Desert/backend/start.sh`
  - nginx vhost: `/etc/nginx/sites-enabled/cd-backend` → localhost:3011
  - PostgreSQL DB: `crimson_desert`, User: `postgres`
- **Vercel Frontend:** Team `rolands-projects-0fbc8a46`, Project `crimson-desert-dashboard`
  - Env: `VITE_API_URL=http://cd.haus543.at/api`
- **GitHub:** `roland76rm-boop/crimson-desert-dashboard`

## Status
- [x] Backend: API Endpoints + DB Schema + Mock-Seed (10 Snapshots)
- [x] Frontend: Dashboard mit 7 Seiten (Übersicht, Inventar, Equipment, Quests, Söldner, Timeline, Einstellungen)
- [x] Save-File Reverse Engineering: Crypto + PARC Format vollständig entschlüsselt
- [x] Watcher: Echte Crypto-Pipeline (ChaCha20 + LZ4 + PARC Parser)
- [x] Item-Datenbank: 6022 Items mit Namen + Kategorien
- [x] VPS Deployment: pm2 + nginx (Port 3011)
- [x] Vercel Deployment
- [ ] DNS: A-Records für cd.haus543.at + crimsondesert.haus543.at → 152.53.0.21
- [ ] SSL/HTTPS für Backend
- [ ] Gaming-PC: Watcher Installation + API Key konfigurieren
- [ ] Quest-Detail-Parsing (individuelle Quest-States aus PARC extrahieren)
- [ ] Söldner-Detail-Parsing (Mercenary Clan Daten)

## Referenzen
- Save-Format: ChaCha20 + HMAC-SHA256 + LZ4 + PARC Binary
- Community Save Editor: https://github.com/NattKh/CRIMSON-DESERT-SAVE-EDITOR
- Item-Datenbank: https://github.com/NattKh/CrimsonDesertCommunityItemMapping
- Save-Pfad (Steam): %LOCALAPPDATA%\Pearl Abyss\CD\save\<id>\slot0\save.save

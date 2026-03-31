# Crimson Desert Dashboard

## Übersicht
Save-File-Parser-basiertes Dashboard für Crimson Desert.
Architektur: File-Watcher (Gaming-PC) → FastAPI (VPS) → React/Vite (Vercel)

## Stack
- Backend: FastAPI + PostgreSQL (VPS 152.53.0.21, Port 3010)
- Frontend: React + TypeScript + Vite + Tailwind + Recharts (Vercel)
- Watcher: Python + Watchdog + ChaCha20/LZ4 (Gaming-PC)
- Domain: cd.haus543.at (Backend API), crimsondesert.haus543.at (Frontend)

## Verzeichnisstruktur
/backend   — FastAPI Backend
/frontend  — React/Vite Frontend
/watcher   — Python File-Watcher + Save-Parser

## Status
- [ ] Backend: API Endpoints + DB Schema
- [ ] Frontend: Dashboard mit Mock-Daten
- [ ] Watcher: Skeleton mit Mock-Mode
- [ ] VPS Deployment: pm2 + Caddy
- [ ] Vercel Deployment
- [ ] Gaming-PC: Watcher Installation
- [ ] PARC Parser: Echtes Save-File reverse-engineeren

## Referenzen
- Save-Format: ChaCha20 + HMAC-SHA256 + LZ4 + PARC Binary
- Community Save Editor: https://github.com/NattKh/CRIMSON-DESERT-SAVE-EDITOR
- Item-Datenbank: https://github.com/NattKh/CrimsonDesertCommunityItemMapping
- Save-Pfad (Steam): %LOCALAPPDATA%\Pearl Abyss\CD\save\<id>\slot0\save.save

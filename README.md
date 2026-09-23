# Jibhi–Shoja Couple Trip — Oct 4–8 (+ optional Oct 9)

Static single-page trip guide: 22 quiet shortlisted stays (filter/sort + detail modals with researched Oct 4–8 / Oct 4–9 prices and booking links), 11 places, day-by-day plan, travel booking links, budget bands.

## Run locally
Any static server from this folder, e.g. `python -m http.server` → http://127.0.0.1:8000/

## Deploy (GitHub Pages, project site)
1. Push this folder as repo root to a new public repo.
2. Repo → Settings → Pages → Deploy from branch → `main` / `/ (root)` → Save.
3. Live at `https://<user>.github.io/<repo>/` in ~1–2 min.

All paths are relative — no config needed for the `/repo/` subpath.

## Data provenance
- `data/stays.json` (22) + `data/places.json` (11) compiled from the research layer via `tools/compile.py`.
- `data/site.json`: itinerary, travel links, budget bands.
- Prices = Sep-2025–Aug-2026 baselines for 2 adults; Oct peak may run +10–20%.
- Photos are representative placeholders (room/view/exterior), not actual listing rooms.

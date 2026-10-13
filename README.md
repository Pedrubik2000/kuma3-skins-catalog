# kuma3 Skins catalog

The skins you can download in [kuma3 Skins](https://github.com/Pedrubik2000/kuma3-skins) (open the app, then
**Get more skins**). The app ships with the Anki skin only; everything here is downloaded on demand, and a skin you
don't like is removed with ✕ in the picker. Your XP and streak stay either way: they live in your kuma3 collection.

| Skin | What it is |
| --- | --- |
| Onigiri | A calm dashboard: stats, heatmap, palettes, one Study button |
| Flashcolor | One colour per moment, huge type: green home, yellow question, black answer |
| Anki XP | Windows XP: XP, combos, quests, trophies |
| Anki Hunger | Fear & Hunger fights (sprites are not included: put your own in `Pictures/anki-hunger`) |
| Anki Joker | Balatro-style runs where your reviews are the cards |

## How the app uses this repo

`catalog.json` lists the skins. The app reads it from
`https://raw.githubusercontent.com/Pedrubik2000/kuma3-skins-catalog/main/catalog.json` and downloads only the
files an entry lists, from `skins/<id>/`:

```json
{"id": "onigiri", "name": "Onigiri", "icon": "🍙", "bg": "#2f8f5f", "version": 1, "app": 3,
 "files": ["index.html"], "about": "A calm dashboard: stats, heatmap, palettes, one Study button"}
```

- `id`: lowercase letters, digits and `-`; never changes (it keys the skin's saved data).
- `version`: raise it when a skin changes; the app then offers **Update**.
- `app`: the oldest kuma3 Skins `versionCode` the skin runs on (a skin that needs a new bridge call raises it).
- `files`: every file of the skin, `index.html` first.

## Adding a skin

- **People:** follow [docs/tutorial.md](docs/tutorial.md), a step-by-step first skin (about 30 minutes), then
  [docs/reference.md](docs/reference.md) for the page contract and every bridge call.
- **Coding agents (Claude Code and others):** point it at this repo; [AGENTS.md](AGENTS.md) (also loaded through
  `CLAUDE.md`) has the steps, the rules and the checks it must run.

Every skin can read and answer your kuma3 cards, so the app downloads from this repo only. Unofficial personal
project, not affiliated with Anki, AnkiDroid, Onigiri, Fear & Hunger or Balatro.

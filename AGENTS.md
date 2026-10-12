# Making a kuma3 skin: instructions for coding agents

This repo is the catalog the kuma3 Skins Android app downloads skins from. A skin is a self-contained HTML page in
`skins/<id>/` plus one entry in `catalog.json`. You never need to build the Android app to add or change a skin.

Human docs: [docs/tutorial.md](docs/tutorial.md) (step by step) and [docs/reference.md](docs/reference.md) (contract, bridge).
App source (bridge, picker, card isolation): https://github.com/Pedrubik2000/kuma3-skins
(`src/main/java/.../MainActivity.kt`, `src/main/assets/shared.js`, the built-in `src/main/assets/anki/` skin).

## Hard rules

1. **Never rate real cards.** On a device, only open decks, show answers, and leave. Test `rate()` in a browser
   with the mock. Ratings on a device are the user's real reviews and can't be taken back by you.
2. **Answer cards only through the bridge** (`B.answer`). Never write scheduling or card data yourself.
3. **No network and no third-party assets in a skin.** No CDN scripts, web fonts, remote images, or copyrighted
   music, sprites or art. The app works offline; system fonts only. Device-side assets (e.g. `Music/anki-<id>`)
   are read at run time, never committed.
4. **Don't edit `skins/shared.js`.** It is a copy of the app's file for browser tests only; the app never downloads
   it and always uses its own. If the app's `shared.js` changed, recopy it and keep the two header lines.
5. **Never change an existing skin's `id`** or its localStorage key prefix: they key the user's saved data.
6. **Keep the AnKing controller layout and XP values** (see "Behaviour every skin keeps").
7. Keep `catalog.json` valid JSON (`python -m json.tool catalog.json`); a broken catalog breaks every user's
   "Get more skins".

## Steps for a new skin

1. **Pick an id**: matches `^[a-z][a-z0-9-]{0,31}$`, not used in `catalog.json`. Examples below use `ocean`.
2. **Copy a base**: `cp -r skins/flashcolor skins/ocean` (smallest, ~360 lines). For a dashboard use
   `skins/onigiri`; for game mechanics read `skins/xp` (XP, combos, quests) or `skins/joker`.
3. **Rename identity**: in `skins/ocean/index.html` set `<title>`, and replace every `flash-` (or `onigiri-`)
   with `ocean-`. Then `grep -n "flash-" skins/ocean/index.html` must print nothing.
4. **Make the change** the user asked for. Look is CSS tokens at the top of `<style>`; views are `homeView()`,
   `decksView()`, `reviewView()`, `setupView()`, `errorView()`; game rules go in `rate(ease)` / `score(ease)`.
   Don't touch the card section (`cardDoc`, `typeQ`, `typeA`, `sounds`) unless the task is about cards.
5. **Add the catalog entry** to `catalog.json` (`skins` array):
   `{"id": "ocean", "name": "Ocean", "icon": "🌊", "bg": "#0e4c92", "version": 1, "app": 3, "files": ["index.html"], "about": "<one line>"}`.
   `files` = every file in `skins/ocean/` that the page loads (`index.html` first). `app` = minimum app
   `versionCode` (3 = first catalog version; raise only if you need a newer bridge call).
6. **Verify** (next section). Fix and re-verify until all checks pass.
7. **Commit** `skins/ocean` and `catalog.json` together. Push only if the user asked; otherwise say it's ready.
   Live within ~5 minutes of reaching `main` (the app reads `raw.githubusercontent.com/.../main/catalog.json`,
   which GitHub caches for 300 s).

## Changing an existing skin

Edit `skins/<id>/`, raise that entry's `"version"` by 1 (otherwise installed copies never get the **Update**
button), and add any new file to `"files"`. Keep `id` and storage keys.

## Verify

Serve the repo root and drive the page in a headless browser (Playwright/Chromium or the like):

```bash
python -m http.server 8793
# open http://localhost:8793/skins/<id>/index.html
```

Without `window.Anki` the page uses its `mock` (example decks and cards). Check, at 375×812 and at 800×1280:

- No console errors on load.
- `document.documentElement.scrollWidth <= innerWidth` (no sideways scroll).
- The flow works by clicking the real controls: home → start a deck → show answer → each of the 4 answer buttons
  → "deck done" → back home. `back()` returns `true` inside the reviewer and `false` on home.
- `pad("x")`, `pad("a")`, `pad("y")`, `pad("b")` show the answer on the question side and answer 1-4 on the
  answer side; `pad("r1")` leaves the deck.
- The card iframe is `#face`, inside its own box, and the ✎ 🗑 ⋯ buttons don't cover its first line.
- `python -m json.tool catalog.json` succeeds and the entry's `files` all exist.
- Take a screenshot of home, question and answer and look at them before you report success.

## The page contract

The app and `shared.js` call these globals; every skin defines them:

| Global | Called by | Must |
| --- | --- | --- |
| `refresh()` | app on resume; after a card leaves | reload `B.status()` + decks, redraw (in review: fetch the card again) |
| `back()` | Android Back | close an overlay or leave review → `true`; on home → `false` (app opens the picker) |
| `pad(k)` | gamepad | `k` ∈ `up down left right a b x y l1 r1` |
| `reveal()`, `rate(ease)` | `shared.js` | show the answer; answer 1-4 and show the next card |
| `cardDeleted()` | optional | next card after 🗑 / bury / suspend (else `refresh()`) |
| `away()`, `wordDone(tok)`, `setVol()` | optional | stop timers/music on pause; combo clock; duck music |

Globals `shared.js` reads: `st` (from `B.status()`: `cardUrl`, `mediaBase`), `card`, `typed`, and the iframe
`id="face"`. It provides `B` (bridge proxy, `null` in a browser), `showCard(frame, html)`, `toCard(msg)`
(`{t:"replay"}`, `{t:"scroll", dy}`), `cardGone()`, `FLAGS`, and the card's ✎ 🗑 ⋯ buttons. Load it with
`<script src="../shared.js"></script>` before the page script.

## Bridge calls (`B.name(...)`, all return strings; JSON ones need `JSON.parse`)

`status()` JSON {pkg, anki, media, cardUrl, mediaBase, sprites?, have?} · `grantAnki()` · `grantMedia()` ·
`decks()` JSON [{id, name "A::B", new, learn, due, collapsed?}] · `next(deckId)` JSON {nid, ord, q, a, css, times[4],
fields, flag, tags, lapses, model, queue?} or null · `answer(nid, ord, ease, ms≤60000)` · `undoLabel()` · `undo()` ·
`today()` JSON {cards, seconds} or null · `activity(days)` JSON {"YYYY-MM-DD": [reviews, ms, reviewCards, passed]} ·
`progressRead()` JSON {device: data} · `progressWrite(device, json)` · `bury|suspend(nid, ord)` · `flag(nid, ord, 0-7)` ·
`deleteNote(nid)` · `editNote(nid, ord)` · `openScreen(stats|browser|add|deck_options|settings, deckId)` ·
`browse(search)` · `searchNotes(query)` · `sync()` · `openAnki()` · `useSkin("")` (picker) · `settings(1)` ·
`setCollapsed(deckId, 0|1)` · `model()` · `vibrate("40,60,40")` (ms on, off, on…) · `music()`.
Any call can throw when kuma3 is closed: catch and show `errorView()`. Wrap calls in an `api` object with a
matching `mock` so the page runs in a browser (copy the pattern from the base skin).

## Behaviour every skin keeps

- **Controller (AnKing):** X Again, A Hard, Y Good, B Easy; on the question side any of them reveals. Right/left
  scroll the card (`toCard({t:"scroll", dy})`), L1 replay, R1 leaves the deck. Keyboard: Space/Enter reveal, 1-4 answer.
- **XP:** Again 2, Hard/Good/Easy 10 (Anki XP multiplies by its combo; never exceed that). Progress lives in the
  shared note through `progressRead/progressWrite`: write only this device's part, id `<model>-<id>-<random>`,
  shape `{xp, days: {"Y-M-D": {reps, xp, goal}}}`; day starts at 4 am (`dayKey()`); level
  `floor((sqrt(1 + 0.08·xp) - 1) / 2)`; streak = consecutive days with ≥1 review, no freezes. Copy `merge()` from
  `skins/onigiri`.
- **Card:** build it with `cardDoc` and show it with `showCard`; talk to it only via `postMessage`; leave ~60 px
  top padding for the corner buttons; dark skins add `nightMode night_mode` to the card body.
- **Back order:** overlay → reviewer → picker.

## Report back

Say which files changed, the new `catalog.json` entry (or the version bump), what you verified and how
(screenshots, sizes, console), and anything you could not check (e.g. on a device). Don't claim device testing
you didn't do.

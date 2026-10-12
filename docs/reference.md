# kuma3 skin reference

What a skin is, what it must define, and every bridge call it can use. Start with the step-by-step
[tutorial](tutorial.md) if you haven't made a skin yet.

## What a skin is

A skin is one HTML page that the kuma3 Skins app shows full screen in a WebView. The app ships with the Anki skin
only; every other skin lives in this repo as `skins/<id>/index.html`, and people download it in the app with
**Get more skins** and remove it with ✕. The page draws its own deck list and reviewer, and does everything else
through the bridge, `window.Anki`, which `shared.js` wraps as `B`.

- **The skin does:** how decks, the card and the answer buttons look; game rules (XP, combos, fights); sounds and
  animations.
- **kuma3 does:** scheduling (FSRS-7 and RWKV), the collection, media files, sync with AnkiWeb, the note editor, the
  browser and statistics screens.
- **The app** ([kuma3-skins](https://github.com/Pedrubik2000/kuma3-skins), `MainActivity.kt`) **does:** the bridge,
  the picker and downloads, the settings page, the gamepad, and the card frame that keeps card scripts away from the
  page.

A skin never changes cards by itself: it answers them through kuma3's provider (`B.answer`), so reviews land in
kuma3's revlog exactly like a review in kuma3.

```
Skin page (skins/<id>/index.html) --B.* calls--> Bridge (MainActivity.kt) --content://--> kuma3 provider
      ^                                              |                                   (decks, cards, answers,
      | postMessage only                             +--OPEN_SCREEN intent--> kuma3 screens  revlog, progress notes)
      v                                                                       (editor, browser, stats, options)
Card frame (its own page, cross-origin)
```

The smallest skins to copy from are **Flashcolor** (about 360 lines) and **Onigiri** (about 450). Anki XP, Hunger and
Joker add game code on top of the same parts.

## The page contract

The app and `shared.js` call a few global functions by name, so every skin defines them; everything else in the page
is free.

| Function | Who calls it | What it must do |
| --- | --- | --- |
| `refresh()` | the app on every resume; after a card leaves (🗑, bury, suspend) | reload status and decks, then redraw (in the reviewer: fetch the card again) |
| `back()` | the app on Android Back | close an overlay or leave the reviewer and return `true`; return `false` to let the app go to the picker |
| `pad(k)` | the app on a gamepad press | `k` is `up` `down` `left` `right` `a` `b` `x` `y` `l1` `r1` |
| `reveal()` | `shared.js` (Enter in a type box) | show the answer side |
| `rate(ease)` | `shared.js` (a card that grades itself) | answer the card 1-4 and show the next |
| `cardDeleted()` | optional; after 🗑, bury or suspend | show the next card (without it, `refresh()` runs) |
| `away()` | optional; the app on pause | stop music or timers |
| `wordDone(tok)`, `setVol()` | optional; the card frame | combo clock after the word audio; duck music while card media plays |

The page also keeps these globals, because `shared.js` reads them: `st` (from `B.status()`, holds `cardUrl` and
`mediaBase`), `card` (the card on screen), `typed` (what was typed in a type box), and an iframe with `id="face"`
inside a box for the ✎ 🗑 ⋯ buttons.

`shared.js` (load it with `<script src="../shared.js"></script>` before the page's own script) gives the page: `B`
(the bridge, or `null` in a browser), `showCard(frame, html)`, `toCard(message)` (`{t:"replay"}`,
`{t:"scroll", dy}`), `cardGone()`, `FLAGS`, and the ✎ 🗑 ⋯ corner buttons drawn on every card. In the app it is the
app's own copy; `skins/shared.js` in this repo is only for browser tests.

## Bridge reference

Every call is `B.name(args)` and returns a string; calls marked JSON need `JSON.parse`. Each skin wraps them in an
`api` object with a matching `mock`, so the page also runs in a browser. A call can throw when kuma3 is closed or
busy: catch it and show the error view.

| Call | Returns | Use |
| --- | --- | --- |
| `status()` | JSON `{pkg, anki, media, cardUrl, mediaBase}` (+ `sprites`, `have` for Hunger) | first thing in `refresh()`; no `anki` or `media` = show the setup view |
| `grantAnki()`, `grantMedia()` | | the two permission prompts of the setup view |
| `decks()` | JSON `[{id, name, new, learn, due, collapsed?}]` | deck tree order, names like `Deutsch::Core 1000`, hidden decks left out |
| `next(deckId)` | JSON `{nid, ord, q, a, css, times, fields, flag, tags, lapses, model, queue?}` or `null` | the next card; `null` = deck done |
| `answer(nid, ord, ease, ms)` | | ease 1-4; ms = thinking time, capped at 60000 |
| `undoLabel()`, `undo()` | text; 1 when undone | kuma3's Undo |
| `today()` | JSON `{cards, seconds}` or `null` | kuma3's "Studied N cards today" |
| `activity(days)` | JSON `{"2026-10-11": [reviews, ms, review cards, passed]}` | heatmap, pace, retention (Onigiri) |
| `progressRead()`, `progressWrite(device, json)` | JSON `{device: data}` | the shared XP and streak note |
| `bury`, `suspend`, `flag(nid, ord, f)`, `deleteNote(nid)` | | card actions (the ⋯ menu already has them) |
| `editNote(nid, ord)`, `openScreen(screen, deckId)`, `browse(search)`, `searchNotes(query)` | | kuma3's editor, browser, stats, add, deck options, settings |
| `sync()`, `openAnki()` | | ask kuma3 to sync with AnkiWeb; open kuma3 |
| `useSkin("")`, `settings(1)` | | back to the picker; kuma3 Skins' settings |
| `setCollapsed(deckId, 0/1)` | | collapse a deck in kuma3 too |
| `model()`, `vibrate(pattern)`, `music()` | | device name for the progress note; haptics (`"40,60,40"` = ms on, off, on); audio files in `Music/anki-<id>` |

Anki XP's launcher calls (`loadApps`, `launch`, `wallpaper`), `boss`, `improved` and `openKumapie` exist too, but a
new skin rarely needs them. A skin that needs a new bridge call needs a new app release first (see "Changing the
app").

## Showing the card

Copy the card code from an existing skin and change only the colours: it carries the safety rules and the features
every skin shares.

- **`cardDoc(html, skip)`** builds the card's own page: the `[sound:]` tags become players (the first one autoplays,
  except sounds already played on the question side), `<base>` points at kuma3's media folder, and the note type's CSS
  comes last so it wins. Set your background and text colour here; Onigiri uses the palette, Flashcolor the screen's
  colour, and dark skins add the `nightMode night_mode` classes.
- **`showCard(frame, html)`** shows it. In the app the card is a separate page (`B.setCard`, then `st.cardUrl`),
  cross-origin to the skin, so a shared deck's scripts cannot reach the skin or kuma3. In a browser it falls back to
  `srcdoc`.
- **Type the answer:** wrap the question in `typeQ()` and the answer in `typeA()`. The box's text comes back to the
  page as `typed`; Enter shows the answer.
- **Replay:** `toCard({t: "replay"})` plays the word audio, then the sentence audio, then the clip (the 🐻 German
  template), or the card's first player on other cards.
- **Talk to the card only by messages.** The skin and the card never touch each other's DOM; `cardHelper` (in
  `shared.js`) runs inside the card and answers `replay` and `scroll`.
- Leave room at the top of the card (Onigiri and Flashcolor pad 60 px) so the ✎ 🗑 ⋯ buttons don't cover the first
  line.

## XP, streak and the shared progress note

All skins share one XP total, level and streak through notes of type `🐻 Anki XP progress` in kuma3's collection, so
they sync to every device with the cards.

- **One part per device and skin.** The device id is `<model>-<id>-<random>` (e.g. `Pixel 8a-onigiri-k3x9qa`), made
  once and kept in localStorage. A skin writes only its own part with `B.progressWrite(device, json)`.
- **The part's shape:** `{xp, days: {"2026-10-11": {reps, xp, goal}}}`. Game skins add their own fields (Anki XP:
  `record`, `goal`, achievements; Hunger: `slain`; Joker: `antes`, `best`).
- **Read all, merge:** `B.progressRead()` returns every part. Add up `xp` and each day's `reps`; take the newest
  `goal`. Copy `merge()` from Onigiri.
- **The day starts at 4 am**, like Anki's: use `dayKey()` for the progress note's day keys.
- **Level:** `level(xp) = floor((sqrt(1 + 0.08 xp) - 1) / 2)`; level L starts at 50 · L · (L + 1) XP.
- **Streak:** days in a row with at least one review in any skin, counting from today (or from yesterday while today
  has no review yet). No freezes.
- **XP per answer:** Again 2, Hard/Good/Easy 10. Anki XP multiplies by its combo; a new skin should stay at or below
  that, so no skin becomes the fast way to level up.

## Rules

- **Never rate real cards while testing.** They are real reviews. On a device, only open decks, show answers, and
  leave; test the rating code in the browser with the mock.
- **Answers go through kuma3 only** (`B.answer`). A skin never writes card scheduling itself, so FSRS-7 and RWKV stay
  kuma3's job.
- **No copyrighted files in the repo:** music, wallpapers, game sprites and art stay on the device (`Music/anki-<id>`,
  `Pictures/...`) and are read at run time. A skin draws its own art or uses none.
- **Controller (8BitDo Micro, AnKing layout):** X Again, A Hard, Y Good, B Easy; on the question side any of them shows
  the answer. Right and left scroll the card, L1 replays, R1 leaves the deck. Keep this the same in every skin.
- **Keyboard:** Space or Enter shows the answer, 1-4 answer.
- **Back:** overlay, then reviewer, then the picker (return `false` from `back()`).
- **Offline:** no web fonts or scripts from the internet; the app must work without a connection. Use system fonts.

## Test and publish

1. **Browser first:** serve the repo (`python -m http.server 8793`) and open `skins/<id>/index.html` at phone width
   (375 px) and at tablet width. Check home, question, answer, deck done, and that nothing scrolls sideways.
2. **Publish:** commit `skins/<id>` and `catalog.json` and push to `main` (or open a pull request). Within about
   5 minutes (GitHub caches the catalog) the skin shows up in **Get more skins**.
3. **On a device:** download it there, open a deck and show an answer; don't rate.
4. **Changing a published skin:** raise its `version` in `catalog.json` and push; the app shows **Update** next to it.

## Changing the app

A skin that needs a new bridge call: add the call to `MainActivity.kt` in
[kuma3-skins](https://github.com/Pedrubik2000/kuma3-skins) (a `@JavascriptInterface` method in `Bridge`, reading kuma3
through `contentResolver` inside `ready { }`), raise the app's `versionCode`, release the app, and set the skin's
`"app"` to that `versionCode` so older apps show "Needs a newer kuma3 Skins". If `shared.js` changes, copy it to this
repo's `skins/shared.js` too (keep its two header lines), so browser tests match the app.

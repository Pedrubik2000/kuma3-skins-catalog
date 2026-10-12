# Make your first kuma3 skin

In about 30 minutes you will make **Ocean**, a blue copy of the Flashcolor skin, try it in your browser and download
it on your phone. You don't need Android Studio or to rebuild the app: a skin is one HTML file in this repo.

You need: Git, Python 3 (for a small local web server), a text editor, a browser, and kuma3 Skins 0.3.0 or newer on
your phone. For every detail behind these steps, see [reference.md](reference.md). Using a coding agent instead?
Point it at [AGENTS.md](../AGENTS.md).

## Step 1: Get the catalog and open a skin in your browser

You'll see a real skin running on example cards, so you know your setup works before you change anything.

1. Get the catalog. If you can push to it, clone it; if not, fork it on GitHub first and clone your fork.

   ```bash
   git clone https://github.com/Pedrubik2000/kuma3-skins-catalog.git
   cd kuma3-skins-catalog
   ```

2. Start a local web server in that folder:

   ```bash
   python -m http.server 8793
   ```

3. Open http://localhost:8793/skins/flashcolor/index.html in your browser.

You should see a green screen with a big number and **Start →**. That's Flashcolor using made-up decks (`mock` in the
code), because the browser has no kuma3. Tap **Start**, then **Flip**: the cards are examples, so nothing you do here
touches real reviews.

## Step 2: Copy Flashcolor and give it its own name

Your skin starts as an exact copy, then gets its own id so it never mixes its saved data with Flashcolor's.

1. Copy the folder `skins/flashcolor` to `skins/ocean`. The folder name is the skin's **id**: lowercase letters,
   digits and `-`, and it never changes later.
2. Open `skins/ocean/index.html` in your editor.
3. Change the title on line 6 to `<title>kuma3 Ocean</title>`.
4. Replace every `flash-` with `ocean-` (Find and Replace, all). They are in `flash-deck`, `flash-device`,
   `flash-mine` and the `-flash-` inside the device name. These keys keep Ocean's chosen deck and its part of your XP
   separate from Flashcolor's.
5. Reload http://localhost:8793/skins/ocean/index.html. It still looks like Flashcolor, which is right.

## Step 3: Change the colours and the home screen

All of Flashcolor's colours are at the top of the `<style>` block, so a new look starts there.

1. Find the `:root{--bg:#6be37c;...}` line near the top. Each `--name` is a colour used everywhere in the page:

   | Token | Used for | Flashcolor | Try for Ocean |
   | --- | --- | --- | --- |
   | `--bg`, `--ink` on `:root` | home screen background and text | green, dark green | `#0e4c92`, `#ffffff` |
   | `--bg`, `--ink` on `body[data-s="q"]` | question side | yellow, black | `#7fd3e6`, `#05243a` |
   | `--bg`, `--ink` on `body[data-s="a"]` | answer side | black, white | `#02111f`, `#e6f6ff` |
   | `--again` `--hard` `--good` `--easy` | the four answer buttons | red, grey, green, yellow | keep, or pick your own |

2. Save and reload. Tap **Start** and **Flip** to see all three screens in blue.
3. Change a word: find `today.<br>About` in `homeView()` (the line under the big number) and change "today." to
   "to surf.". Home then says "40 cards to surf."
4. Optional: change the big number's font in `--serif`, or the button shape in `.pill` (its `border-radius`).

Save and reload after each change. If the page goes blank, open the browser's developer console (F12): it shows the
line with the mistake.

## Step 4: Check it like a phone and a tablet would

Phones are narrow and tablets are wide, so try both before anyone downloads it.

1. Open the developer tools (F12) and turn on the device toolbar (Ctrl+Shift+M). Pick a phone around 375 px wide.
2. Go through a whole round: home, **Start**, **Flip**, an answer button, until the deck says **Deck clear**. Tap the
   deck name on home to open the deck list.
3. Switch to a tablet size (about 800 × 1280) and do it again.
4. Check that nothing scrolls sideways, the text fits its buttons, and the ✎ 🗑 ⋯ buttons on the card don't cover the
   first line.

- [ ] Home, question and answer look right on a phone
- [ ] Same on a tablet
- [ ] No sideways scrolling, no errors in the console

## Step 5: Add it to catalog.json

The app only lists skins that `catalog.json` names, and downloads only the files listed there.

1. Open `catalog.json` at the top of the repo.
2. Add a line for Ocean inside `"skins": [ ... ]`, with a comma after the entry before it:

   ```json
   {"id": "ocean", "name": "Ocean", "icon": "🌊", "bg": "#0e4c92", "version": 1, "app": 3, "files": ["index.html"],
    "about": "Flashcolor in blue: deep sea home, shallow water question, night answer"}
   ```

3. Check each field:
   - `id` is the folder name, exactly.
   - `icon` (one emoji) and `bg` (a colour) make its tile in the picker.
   - `version` starts at 1. Raise it each time you change the skin later, and the app offers **Update**.
   - `app` is 3: the first kuma3 Skins version with the catalog.
   - `files` lists every file in the folder. Ocean only has `index.html`; a skin with an image adds it here too.
4. Run `python -m json.tool catalog.json`. If it prints an error, fix it: a missing comma breaks the catalog for
   everyone.

## Step 6: Publish it and download it on your phone

Once Ocean is in the catalog on GitHub, every kuma3 Skins app can download it, yours included.

1. Commit both changes, the `skins/ocean` folder and `catalog.json`:

   ```bash
   git add skins/ocean catalog.json
   git commit -m "Ocean: a blue Flashcolor"
   ```

2. Send it:
   - **Your own catalog** (you can push): `git push`. It's live within about 5 minutes (GitHub caches the catalog).
   - **Someone else's catalog** (you forked it): push to your fork and open a pull request on GitHub. It goes live
     when it's merged.
3. On your phone, open kuma3 Skins. In the picker, tap **Get more skins**, then **Ocean**: it downloads and says
   **Installed**.
4. Tap it to open it, open a deck and flip a card. These are your real cards, so only look; leave without rating
   while you test.

To change Ocean later: edit it, raise `"version"` to 2 in `catalog.json`, push, and tap **Update** in **Get more
skins**. To get rid of it, tap ✕ next to it in the picker.

## Where to go next

You now have a working skin; bigger changes follow the same loop of edit, reload in the browser, push.

- **A different layout:** rewrite `homeView()` and `reviewView()`. Keep the functions they call (`study`, `reveal`,
  `rate`, `leaveDeck`) and the card code at the bottom as they are.
- **A dashboard:** start from Onigiri instead; it already has stat tiles, a heatmap and palettes.
- **A game:** add your rules in `rate(ease)`, which runs after every answer. Keep XP at Again 2, Hard/Good/Easy 10,
  so no skin becomes the fast way to level up.
- **The rules every skin keeps:** answers only through kuma3, no music, sprites or art you don't own in the repo,
  the same gamepad buttons, and no files from the internet (the app works offline).
- **Everything else** (the bridge calls, the page contract, how cards are shown) is in [reference.md](reference.md).

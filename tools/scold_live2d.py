"""Builds Pictures/anki-scold/live2d.js for the Kuma-chan (scold) skin: a Live2D girl instead of the bear.

One script holds everything, because a skin page (file://) may load a device script but not fetch device files:
PixiJS 6 + Cubism Core + pixi-live2d-display (cubism4), then window.SCOLD_MODEL = {json, files: {path: data URL}}.
Nothing of it goes in this repo: Cubism Core is Live2D's proprietary runtime and the models are Live2D samples
(Free Material License), so the file stays on the device.

  python tools/scold_live2d.py <lib dir> <model dir> <out.js>
  adb -s <serial> push out.js /sdcard/Pictures/anki-scold/live2d.js

<lib dir>: pixi.min.js (pixi.js@6.5.10 dist/browser), live2dcubismcore.min.js
(cubism.live2d.com/sdk-web/cubismcore), cubism4.min.js (pixi-live2d-display@0.4.0 dist).
<model dir>: a Cubism 4 model folder with one *.model3.json (e.g. CubismWebSamples Samples/Resources/Haru).
"""
import base64, json, mimetypes, pathlib, sys

lib, model, out = map(pathlib.Path, sys.argv[1:4])
settings_file = next(model.glob("*.model3.json"))
m = json.loads(settings_file.read_text("utf-8"))
refs = m["FileReferences"]
refs.pop("DisplayInfo", None); refs.pop("UserData", None)   # not used by the skin
for group in refs.get("Motions", {}).values():
    for mo in group: mo.pop("Sound", None)                     # she talks in the speech bubble, not in sample voices
paths = [refs["Moc"], *refs["Textures"], *(refs[k] for k in ("Physics", "Pose") if k in refs),
         *(e["File"] for e in refs.get("Expressions", [])), *(mo["File"] for g in refs.get("Motions", {}).values() for mo in g)]
files = {}
for p in paths:
    mime = mimetypes.guess_type(p)[0] or "application/octet-stream"
    files[p] = f"data:{mime};base64," + base64.b64encode((model / p).read_bytes()).decode()
js = "\n;\n".join((lib / f).read_text("utf-8") for f in ("pixi.min.js", "live2dcubismcore.min.js", "cubism4.min.js"))
js += f"\n;\nwindow.SCOLD_MODEL={json.dumps({'name': settings_file.name, 'json': m, 'files': files})};\n"
out.write_text(js, "utf-8")
print(f"{out}: {len(js) / 1e6:.1f} MB, {len(files)} files, expressions {[e['Name'] for e in refs.get('Expressions', [])]}, "
      f"motions {list(refs.get('Motions', {}))}")

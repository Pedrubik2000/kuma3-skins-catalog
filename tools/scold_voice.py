"""Builds Pictures/anki-scold/voice.js for the Kuma-chan (scold) skin: her lines spoken out loud.

Reads the LINES block of skins/scold/index.html and voices every line: Japanese with Kokoro (voice jf_alpha), German
and English with XTTS-v2 cloning that same Kokoro voice, so she sounds like one girl in every language. Output:
window.SCOLD_VOICE = {line: "data:audio/mpeg;base64,…"}; the skin plays a line's mp3 when she says it. Like live2d.js
it stays on the device (XTTS-v2 is under the Coqui Public Model License: non-commercial use).

Heavy dependencies, so its own venv (Python 3.11, CPU torch):
  uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  uv pip install "coqui-tts[codec]" kokoro soundfile pyopenjtalk-plus fugashi jaconv mojimoji unidic-lite "transformers<4.57"
  uv pip install --no-deps misaki
  set COQUI_TOS_AGREED=1 TTS_HOME=<model dir> HF_HOME=<hf dir>; ffmpeg on PATH
  python tools/scold_voice.py skins/scold/index.html <cache dir> <out voice.js>
  adb -s <serial> push voice.js /sdcard/Pictures/anki-scold/voice.js

Wavs are cached per line in <cache dir>, so a changed line costs one synthesis.
"""
import base64, hashlib, json, pathlib, re, subprocess, sys

import numpy as np, soundfile as sf

html, cache, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
cache.mkdir(parents=True, exist_ok=True)
LINES = json.loads(re.search(r"/\*LINES\*/(.*?)/\*LINES\*/", html.read_text("utf-8"), re.S).group(1))
VOICE, SR = "jf_alpha", 24000

_kokoro = None
def kokoro(text):
    global _kokoro
    if _kokoro is None:
        from kokoro import KPipeline
        _kokoro = KPipeline(lang_code="j", repo_id="hexgrad/Kokoro-82M")
    return np.concatenate([a.numpy() for _, _, a in _kokoro(text, voice=VOICE)])

# the voice XTTS clones: a few of her Japanese lines in a row (~10 s)
ref = cache / f"ref-{VOICE}.wav"
if not ref.exists():
    gap = np.zeros(SR // 3, dtype=np.float32)
    sf.write(ref, np.concatenate([np.concatenate([kokoro(t), gap]) for t in
        ["ねえ、ちゃんと聞いてる？今日はドイツ語を一緒に頑張ろうね。", "もう、仕方ないなあ。もう一回だけ教えてあげる。", "ふふっ、よくできました！"]]), SR)

_xtts = None
def xtts(text, lang):
    global _xtts
    if _xtts is None:
        import torch, torchaudio
        from TTS.api import TTS
        # torchaudio reads through torchcodec, which needs FFmpeg's shared DLLs; the reference is a plain wav
        def load(path, *a, **k):
            data, sr = sf.read(path, dtype="float32", always_2d=True)
            return torch.from_numpy(data.T.copy()), sr
        torchaudio.load = load
        _xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    # XTTS sometimes babbles on after a short line ("Hmpf.", "?!"): 3 takes, keep the shortest that isn't cut short
    takes = [np.array(_xtts.tts(text=text, language=lang, speaker_wav=str(ref), temperature=.6, split_sentences=False),
                      dtype=np.float32) for _ in range(3)]
    ok = [t for t in takes if len(t) >= SR * .05 * len(text)] or takes
    return min(ok, key=len)

voice = {}
for lang, sets in LINES.items():
    for text, _ in [l for level in sets["scold"] for l in level] + sets["praise"]:
        mp3 = cache / f"{lang}-{hashlib.sha1(text.encode()).hexdigest()[:12]}.mp3"
        if not mp3.exists():
            wav = mp3.with_suffix(".wav")
            sf.write(wav, kokoro(text) if lang == "ja" else xtts(text, lang), SR)
            trim = "silenceremove=start_periods=1:start_threshold=-45dB"   # both ends: trim, reverse, trim, reverse
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af", f"{trim},areverse,{trim},areverse",
                            "-ac", "1", "-b:a", "64k", mp3], check=True)
            print(lang, text, flush=True)
        voice[text] = "data:audio/mpeg;base64," + base64.b64encode(mp3.read_bytes()).decode()
out.write_text(f"window.SCOLD_VOICE={json.dumps(voice, ensure_ascii=False)};\n", "utf-8")
print(f"{out}: {len(voice)} lines, {out.stat().st_size / 1e6:.1f} MB")

"""Ask large-v3 (no prompt) what is in short ambiguous windows — breath vs. word."""
import sys
import soundfile as sf
from faster_whisper import WhisperModel

a, sr = sf.read("audio.wav", dtype="float32")
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for spec in sys.argv[1:]:
    s, e = map(float, spec.split("-"))
    seg, _ = m.transcribe(a[int(s * sr):int(e * sr)], language="ms", word_timestamps=True,
                          condition_on_previous_text=False, vad_filter=False)
    words = [f"{w.word.strip()}({s + w.start:.2f}-{s + w.end:.2f} p{w.probability:.2f})" for g in seg for w in g.words or []]
    print(f"{spec}: {' '.join(words) or '<nothing>'}", flush=True)

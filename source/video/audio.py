# موسيقى هادئة + مؤثرات (ضغط، كتابة، انتقال، تقليب صفحات وبطاقات) مولّدة بالكامل
import json, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
tl = json.load(open("/home/claude/video/timeline.json"))
DUR = tl["dur"]; N = int(DUR * SR) + SR
rng = np.random.default_rng(7)
t_ = lambda d: np.arange(int(d * SR)) / SR
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
bp = lambda lo, hi: butter(2, [lo, hi], "bandpass", fs=SR, output="sos")
hp = lambda f: butter(2, f, "highpass", fs=SR, output="sos")
lp = lambda f: butter(2, f, "lowpass", fs=SR, output="sos")

# ── الموسيقى ──
mus = np.zeros((N, 2))
def add(buf, x, at, pan=0.0, g=1.0):
    i = int(at * SR); x = x[: max(0, len(buf) - i)]
    buf[i:i + len(x), 0] += x * g * (1 - pan) ** 0.5 / 1.0
    buf[i:i + len(x), 1] += x * g * (1 + pan) ** 0.5 / 1.0

BAR = 3.2
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]     # Am F C G
CH2 = [[57, 60, 64], [50, 53, 57], [53, 57, 60], [52, 56, 59]]    # Am Dm F E
def pad(notes, d):
    t = t_(d); env = np.minimum(1, t / 0.9) * np.minimum(1, (d - t) / 1.2)
    x = sum(np.sin(2 * np.pi * hz(m) * t * k) / k ** 1.6 * (1 + 0.3 * np.sin(2 * np.pi * 0.2 * t))
            for m in notes for k in (1, 2, 3)) + sum(np.sin(2 * np.pi * hz(m) * 1.003 * t) for m in notes) * .5
    return sosfilt(lp(1800), x * env)
def pluck(m, d=1.4):
    t = t_(d)
    return (np.sin(2 * np.pi * hz(m) * t) + .35 * np.sin(4 * np.pi * hz(m) * t) + .12 * np.sin(6 * np.pi * hz(m) * t)) \
        * np.exp(-t * 4.2) * np.minimum(1, t / 0.004)
def bass(m, d):
    t = t_(d); return np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / .05) * np.exp(-t * .5) * np.minimum(1, (d - t) / .2)

nbars = int(DUR / BAR) + 2
pat = [0, 2, 1, 2, 0, 2, 1, 3]
for b in range(nbars):
    prog = CH if (b // 8) % 2 == 0 else CH2
    c = prog[b % 4]; at = b * BAR
    add(mus, pad(c, BAR + 1.0), at, 0, 0.05)
    add(mus, bass(c[0] - 12, BAR), at, 0, 0.16)
    if at > 4.4:                                      # الأربيجيو يبدأ مع ظهور الجوال
        for k in range(8):
            m = c[pat[k] % 3] + (12 if pat[k] == 3 else 12) + (12 if k == 6 else 0)
            add(mus, pluck(m), at + k * BAR / 8, (-.3 if k % 2 else .3), 0.075 * (1.0 if k % 4 == 0 else .7))
# صدى
ir = rng.standard_normal(int(1.9 * SR)) * np.exp(-np.arange(int(1.9 * SR)) / SR * 3.2); ir /= np.abs(ir).sum() / 6
for ch in (0, 1):
    mus[:, ch] = mus[:, ch] + 0.35 * fftconvolve(mus[:, ch], np.roll(ir, ch * 37))[:N]
tt = np.arange(N) / SR
mus *= np.minimum(1, tt / 2.5)[:, None] * np.clip((DUR - tt) / 4.0, 0, 1)[:, None]
mus /= np.abs(mus).max(); mus *= 0.30

# ── المؤثرات ──
sfx = np.zeros((N, 2))
def noise(d): return rng.standard_normal(int(d * SR))
def click():
    t = t_(.05)
    return np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 160) * .5 + sosfilt(hp(3000), noise(.05)) * np.exp(-t * 400) * .6 \
        + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 70) * .35
def key():
    t = t_(.04); f = rng.uniform(1500, 2100)
    return (sosfilt(bp(2500, 7000), noise(.04)) * np.exp(-t * 300) * .9 + np.sin(2 * np.pi * f * t) * np.exp(-t * 250) * .25) * rng.uniform(.6, .9)
def whoosh(d=.65, lo=300, hi=2600):
    n = noise(d); t = t_(d); out = np.zeros_like(n); seg = 512
    for i in range(0, len(n), seg):           # مرشّح يتحرك مع الوقت
        s = i / len(n); f = lo * (hi / lo) ** np.sin(np.pi * s)
        out[i:i + seg] = sosfilt(bp(f * .7, min(f * 1.4, 20000)), n[max(0, i - 2048):i + seg])[-len(n[i:i + seg]):]
    return out * np.sin(np.pi * t / d) ** 2 * .5
def page():
    d = .42; x = np.zeros(int(d * SR)); at = 0.0
    for k in range(7):
        l = .03 + .01 * k; seg = sosfilt(hp(1800), noise(l)) * np.exp(-t_(l) * 70) * (1 - k / 9)
        i = int(at * SR); x[i:i + len(seg)] += seg[: len(x) - i]; at += .025 + .012 * k
    return x * .55 + whoosh(d, 800, 3500) * .5
def card():
    t = t_(.09); x = np.zeros(int(.32 * SR))
    w = whoosh(.22, 600, 3000) * .7; x[:len(w)] += w
    th = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 45) * .6 + sosfilt(hp(2000), noise(.09)) * np.exp(-t * 200) * .3
    i = int(.2 * SR); x[i:i + len(th)] += th[: len(x) - i]
    return x
def pop():
    t = t_(.12); f = 900 - 500 * t / .12
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * .5
def bell(m, d=2.5):
    t = t_(d); f = hz(m)
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dc) for r, a, dc in ((1, 1, 2), (2.0, .5, 3), (2.76, .3, 5), (5.4, .15, 8))) * .35
def send():
    return np.pad(bell(81, 1.8), (0, 0)) * .7 + np.pad(np.pad(bell(88, 1.8), (int(.12 * SR), 0))[: int(1.8 * SR)], (0, 0)) * .6

GEN = {"click": (click, .55), "key": (key, .30), "whoosh": (whoosh, .55), "page": (page, .6),
       "card": (card, .6), "pop": (pop, .5), "send": (send, .5)}
for e in tl["events"]:
    if e["type"] != "sfx": continue
    f, g = GEN[e["kind"]]
    x = f(); pan = rng.uniform(-.15, .15)
    if e["kind"] == "page": x = x.copy(); x[:2400] += click() * .5
    add(sfx, x, max(0, e["t"]), pan, g)
T_OUTRO = next(e["t"] for e in tl["events"] if e["type"] == "outro")
add(sfx, bell(76) + bell(83) * .6, 0.35, 0, .45)                       # المقدمة
for k, dt in enumerate((4.4, 8.8, 13.2)):
    add(sfx, page(), T_OUTRO + dt - .1, 0, .55)
add(sfx, bell(81, 3) + bell(76, 3) * .7 + bell(88, 3) * .4, T_OUTRO + 13.2, 0, .45)  # الختام

mix = mus + sfx
mix /= max(1e-9, np.abs(mix).max()) / 0.89
wavfile.write("/home/claude/video/audio.wav", SR, (mix[: int(DUR * SR)] * 32767).astype(np.int16))
print("audio ok", DUR)

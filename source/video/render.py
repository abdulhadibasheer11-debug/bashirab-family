# يركّب الإطارات: الخلفية + النصوص + الجوال + إصبع الضغط، ويرمّز كل مشهد في ملف
import json, sys, os, subprocess, bisect
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

V = "/home/claude/video"; L = f"{V}/layers"
FPS, WW, HH = 30, 1080, 1920
SX, SY, SW, SH = 240, 566, 600, 1298
tl = json.load(open(f"{V}/timeline.json"))
segs, ev, DUR = tl["segs"], tl["events"], tl["dur"]
seg_t = [s["t"] for s in segs]
caps = [e for e in ev if e["type"] == "cap"]
taps = [e for e in ev if e["type"] == "tap"]
T_IN = next(e["t"] for e in ev if e["type"] == "phone_in")
T_OUT = next(e["t"] for e in ev if e["type"] == "phone_out")
T_OUTRO = next(e["t"] for e in ev if e["type"] == "outro")

ld = lambda n: Image.open(f"{L}/{n}.png").convert("RGBA")
BG, PHONE = ld("bg"), ld("phone")
CARD = {k: ld(k) for k in ("intro", "out1", "out2", "out3", "out4")}
CAPI = [ld(f"cap{i:02d}") for i in range(len(caps))]
MASK = Image.new("L", (SW, SH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((0, 0, SW - 1, SH - 1), radius=62, fill=255)

@lru_cache(maxsize=10)
def shot(path):
    return Image.open(path).convert("RGB")

clamp = lambda x: max(0.0, min(1.0, x))
eo = lambda x: 1 - (1 - clamp(x)) ** 3          # ease out
ei = lambda x: clamp(x) ** 3                     # ease in
eio = lambda x: (lambda s: 3 * s * s - 2 * s ** 3)(clamp(x))

def fade(im, a):
    if a >= 0.999: return im
    r = im.copy(); al = np.asarray(r.getchannel("A"), dtype=np.float32) * a
    r.putalpha(Image.fromarray(al.astype(np.uint8))); return r

def put(frame, im, a, dx=0, dy=0):
    if a <= 0.003: return
    im = fade(im, a)
    x, y = int(dx), int(dy)
    sx, sy = max(0, -x), max(0, -y)
    box = (sx, sy, min(im.width, WW - x), min(im.height, HH - y))
    if box[2] <= box[0] or box[3] <= box[1]: return
    frame.alpha_composite(im, (max(0, x), max(0, y)), box)

def screen(t):
    i = max(0, bisect.bisect_right(seg_t, t) - 1)
    s = segs[i]; im = shot(s["img"])
    if s["xf"] > 0 and i > 0 and t - s["t"] < s["xf"]:
        k = eio((t - s["t"]) / s["xf"])
        im = Image.blend(shot(segs[i - 1]["img"]), im, k)
    return im

def fingers(draw, t, ox, oy):
    for e in taps:
        s = t - e["t"]
        if not (0 <= s <= 1.0): continue
        x, y = ox + e["x"], oy + e["y"]
        # الإصبع: دائرة ذهبية شفافة تقترب ثم تضغط
        a = eo(s / 0.22) * (1 - clamp((s - 0.62) / 0.25))
        r = 40 * (1.35 - 0.35 * eo(s / 0.22)) * (0.86 if 0.3 < s < 0.5 else 1)
        if a > 0:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(184, 144, 28, int(110 * a)),
                         outline=(255, 255, 255, int(230 * a)), width=4)
        # موجة الضغط
        if s > 0.32:
            q = (s - 0.32) / 0.6
            if q < 1:
                R = 40 + 70 * eo(q)
                draw.ellipse((x - R, y - R, x + R, y + R), outline=(184, 144, 28, int(200 * (1 - q))), width=6)

def caption(frame, t, phone_a):
    i = bisect.bisect_right([c["t"] for c in caps], t) - 1
    if i < 0 or phone_a <= 0: return
    s = t - caps[i]["t"]
    same = i > 0 and caps[i]["title"] == caps[i - 1]["title"]
    k = eo(s / 0.45)
    if i > 0 and s < 0.3:
        put(frame, CAPI[i - 1], (1 - s / 0.3) * phone_a, 0, 30)
    put(frame, CAPI[i], k * phone_a, 0, 30 + (0 if same else 40 * (1 - k)))

def frame_at(t):
    f = BG.copy()
    # بطاقة المقدمة
    if t < T_IN + 0.3:
        a = eo(t / 0.9) * (1 - clamp((t - (T_IN - 0.5)) / 0.6))
        put(f, CARD["intro"], a, 0, 50 * (1 - eo(t / 1.2)) - 120 * ei((t - (T_IN - 0.5)) / 0.6))
    # الجوال
    if T_IN - 0.1 <= t <= T_OUT + 0.8:
        din = 1 - eo((t - T_IN) / 0.8)
        dout = ei((t - T_OUT) / 0.7)
        dy = 1400 * din + 1500 * dout
        pa = 1 - clamp((t - T_OUT) / 0.5)
        caption(f, t, pa * (1 - din))
        if dy < 1500:
            put(f, PHONE, 1, 0, dy)
            sc = screen(t)
            ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            fingers(d, t, 0, 0)
            scr = sc.convert("RGBA"); scr.alpha_composite(ov)
            y = SY + int(dy)
            if y < HH:
                scr.putalpha(MASK)
                put(f, scr, 1, SX, y)
    # بطاقات الختام
    if t >= T_OUTRO:
        s = t - T_OUTRO
        times = [0, 4.4, 8.8, 13.2, 99]
        for j, k in enumerate(("out1", "out2", "out3", "out4")):
            a0, a1 = times[j], times[j + 1]
            if a0 - 0.1 <= s <= a1 + 0.6:
                inn = eo((s - a0) / 0.7)
                out = clamp((s - a1) / 0.5) if j < 3 else 0
                end_fade = 1 - clamp((t - (DUR - 1.2)) / 1.2)
                put(f, CARD[k], inn * (1 - out) * end_fade, 0, 60 * (1 - inn) - 80 * ei(out))
    return f.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for tt in sys.argv[2:]:
            frame_at(float(tt)).save(f"{V}/still_{tt}.jpg", quality=90)
        sys.exit()
    # مشاهد: تبدأ عند المقدمة، كل خطوة جديدة، والختام
    bounds = [0.0, T_IN - 0.2]
    last = None
    for c in caps:
        if c["step"] != last and c["t"] > bounds[-1] + 1:
            bounds.append(c["t"] - 0.2); last = c["step"]
        last = c["step"]
    bounds += [T_OUT - 0.2, DUR]
    bounds = sorted(set(round(b * FPS) for b in bounds))
    os.makedirs(f"{V}/scenes", exist_ok=True)
    only = set(map(int, sys.argv[2:])) if len(sys.argv) > 2 else None
    names = []
    for k in range(len(bounds) - 1):
        f0, f1 = bounds[k], bounds[k + 1]
        name = f"{V}/scenes/s{k:02d}.mp4"; names.append(name)
        if only is not None and k not in only: continue
        tmp = name.replace(".mp4", ".tmp.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{WW}x{HH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-g", "60", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for fi in range(f0, f1):
            ff.stdin.write(frame_at(fi / FPS).tobytes())
        ff.stdin.close()
        if ff.wait() == 0: os.replace(tmp, name)
        print("scene", k, f0 / FPS, f1 / FPS, flush=True)
    open(f"{V}/scenes/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))

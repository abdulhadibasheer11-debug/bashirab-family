# يرسم الطبقات الثابتة (الخلفية، إطار الجوال، بطاقات النصوص) صوراً شفافة
import json, os, base64
from playwright.sync_api import sync_playwright

D = "/home/claude/video/layers"; os.makedirs(D, exist_ok=True)
tl = json.load(open("/home/claude/video/timeline.json"))
icon = base64.b64encode(open("/home/claude/bashirab-family/icon-512.png", "rb").read()).decode()
AR = "٠١٢٣٤٥٦٧٨٩"
ar = lambda n: "".join(AR[int(c)] for c in str(n))

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent;width:1080px;font-family:'IBM Plex Sans Arabic';direction:rtl;color:#fff}
.amiri{font-family:Amiri}
"""

def page_html(body, extra=""):
    return f"<!doctype html><html lang=ar dir=rtl><head><meta charset=utf-8><style>{CSS}{extra}</style></head><body>{body}</body></html>"

BG = """
<div style="width:1080px;height:1920px;position:relative;overflow:hidden;
  background:radial-gradient(ellipse 120% 70% at 50% 0%,#2c6a7d 0%,#1f4e5f 45%,#143640 100%)">
  <svg width=1080 height=1920 style="position:absolute;inset:0;opacity:.07">
    <defs><pattern id=p width=120 height=120 patternUnits=userSpaceOnUse>
      <g fill=none stroke=#e9d48a stroke-width=2>
        <rect x=48 y=14 width=24 height=14 rx=3/><rect x=18 y=80 width=24 height=14 rx=3/><rect x=78 y=80 width=24 height=14 rx=3/>
        <path d="M60 28v22M30 80v-18h60v18"/></g></pattern></defs>
    <rect width=1080 height=1920 fill=url(#p)/></svg>
  <div style="position:absolute;inset:auto 0 0 0;height:420px;background:linear-gradient(transparent,rgba(10,30,36,.55))"></div>
</div>"""

# إطار الجوال: الشاشة 600×1298 تبدأ عند (240,566)
PHONE = """
<div style="position:absolute;left:216px;top:542px;width:648px;height:1346px;border-radius:84px;
  background:linear-gradient(145deg,#3b4448,#11171a 60%,#2a3236);
  box-shadow:0 40px 80px rgba(0,0,0,.45),0 0 0 2px rgba(255,255,255,.08) inset">
  <div style="position:absolute;left:24px;top:24px;width:600px;height:1298px;border-radius:62px;
     box-shadow:0 0 0 1000px transparent;background:transparent;outline:0"></div>
</div>"""

def cap_html(c):
    step = c.get("step")
    badge = f"""<div style="width:84px;height:84px;border-radius:50%;background:#b8901c;color:#fff;
        display:flex;align-items:center;justify-content:center;font-weight:700;font-size:48px;
        margin:0 auto 22px;box-shadow:0 6px 18px rgba(0,0,0,.25)">{ar(step)}</div>""" if step else ""
    return f"""<div style="width:1080px;height:520px;display:flex;flex-direction:column;align-items:center;
        justify-content:center;text-align:center;padding:0 70px">
      {badge}
      <div style="font-size:66px;font-weight:700;color:#f3dc8f;line-height:1.25;text-shadow:0 3px 14px rgba(0,0,0,.3)">{c['title']}</div>
      <div style="font-size:39px;font-weight:500;line-height:1.55;margin-top:16px;text-wrap:balance;color:rgba(255,255,255,.93);text-shadow:0 2px 10px rgba(0,0,0,.3)">{c['sub']}</div>
    </div>"""

def card_html(title, sub, big=False):
    ic = f'<img src="data:image/png;base64,{icon}" style="width:230px;height:230px;border-radius:52px;box-shadow:0 18px 50px rgba(0,0,0,.4);margin-bottom:60px">' if big else ""
    tsz = 112 if big else 84
    fam = "Amiri" if big else "'IBM Plex Sans Arabic'"
    return f"""<div style="width:1080px;height:1920px;display:flex;flex-direction:column;align-items:center;
        justify-content:center;text-align:center;padding:0 90px">
      {ic}
      <div style="font-family:{fam};font-size:{tsz}px;font-weight:700;color:#f3dc8f;line-height:1.35;text-shadow:0 4px 18px rgba(0,0,0,.3)">{title}</div>
      <div style="width:120px;height:5px;border-radius:3px;background:#b8901c;margin:44px auto"></div>
      <div style="font-size:48px;font-weight:500;line-height:1.7;color:rgba(255,255,255,.95)">{sub}</div>
    </div>"""

CARDS = {
    "intro": card_html("شجرة عائلة البشيراب", "دليل استخدام الموقع<br><span style='font-size:38px;opacity:.8'>خطوة بخطوة على جوالك</span>", big=True),
    "out1": card_html("الموقع ما زال قيد الإكمال", "نضيف بقية الفروع والأسماء<br>شيئاً فشيئاً، وبمساعدتكم يكتمل"),
    "out2": card_html("هل تعرف أسماء ناقصة؟",
                      "أرسلها لنا من «أرسل تصحيحاً»<br>في قائمة «المزيد»<br><span style='color:#f3dc8f'>فكل اسم تضيفه يكمّل شجرة العائلة</span>"),
    "out3": card_html("لديك اقتراح؟",
                      "إن كانت لديك فكرة لتطوير الموقع<br>أو تغيير شكله وطريقة استخدامه<br>فأرسلها لنا بالطريقة نفسها"),
    "out4": card_html("شجرة عائلة البشيراب",
                      "شكراً لكم، ودمتم بخير<br><span dir=ltr style='display:inline-block;margin-top:34px;font-size:30px;opacity:.85;font-family:IBM Plex Sans Arabic'>abdulhadibasheer11-debug.github.io/bashirab-family</span>", big=True),
}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    def shot(html, path, h=1920):
        pg.set_viewport_size({"width": 1080, "height": h})
        pg.set_content(page_html(html)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
        pg.screenshot(path=path, omit_background=True)
    shot(BG, f"{D}/bg.png")
    shot(PHONE, f"{D}/phone.png")
    for k, h in CARDS.items():
        shot(h, f"{D}/{k}.png")
    caps = [e for e in tl["events"] if e["type"] == "cap"]
    for i, c in enumerate(caps):
        shot(cap_html(c), f"{D}/cap{i:02d}.png", h=520)
    b.close()
print("ok", len(caps))

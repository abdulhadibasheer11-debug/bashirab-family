# يصوّر الموقع على جوال ويكتب timeline.json (اللقطات + الضغطات + النصوص + المؤثرات)
import json, os, math, shutil
from playwright.sync_api import sync_playwright

OUT = "/home/claude/video/shots"
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
W, H, DPR = 390, 844, 600 / 390          # الشاشة في الفيديو 600×1298
URL = "http://localhost:8765/index.html"

T = 0.0          # ساعة الفيديو
segs = []        # صور الشاشة: {t, dur, img, xf}
events = []      # ضغطات ونصوص ومؤثرات
n = 0

def snap():
    global n
    n += 1
    path = f"{OUT}/{n:04d}.jpg"
    page.screenshot(path=path, type="jpeg", quality=92)
    return path

def hold(dur, xf=0.0):
    """لقطة ثابتة للشاشة الحالية"""
    global T
    segs.append({"t": T, "dur": dur, "img": snap(), "xf": xf})
    T += dur

def cap(title, sub="", step=None):
    events.append({"t": T, "type": "cap", "title": title, "sub": sub, "step": step})

def sfx(kind, dt=0.0):
    events.append({"t": T + dt, "type": "sfx", "kind": kind})

def settle(ms=650):
    page.wait_for_timeout(ms)

def center(loc):
    b = loc.bounding_box()
    return (b["x"] + b["width"] / 2) * DPR, (b["y"] + b["height"] / 2) * DPR

def tap(loc, pre=0.7, after=None, sound="click", xf=0.3, wait=650):
    """إصبع يضغط ثم تتغير الشاشة"""
    global T
    loc.scroll_into_view_if_needed()
    x, y = center(loc)
    hold(pre)                                   # لحظة قبل الضغط وفيها الدائرة
    events.append({"t": T - 0.45, "type": "tap", "x": x, "y": y})
    sfx(sound, -0.12)
    loc.click()
    settle(wait)
    if after: after()

def type_in(loc, text, cps=9):
    """كتابة حرفاً حرفاً"""
    global T
    loc.click(); settle(250)
    step = 1 / cps
    for ch in text:
        page.keyboard.insert_text(ch)
        settle(120 if ch != " " else 60)
        sfx("key", 0.0)
        segs.append({"t": T, "dur": step, "img": snap(), "xf": 0})
        T += step

def scroll_to(y_css, dur=1.6, fps=30):
    """تمرير ناعم بلقطة لكل إطار"""
    global T
    y0 = page.evaluate("scrollY")
    maxy = page.evaluate("document.documentElement.scrollHeight - innerHeight")
    y1 = max(0, min(y_css, maxy))
    k = max(2, int(dur * fps))
    for i in range(1, k + 1):
        s = i / k; e = 0.5 - 0.5 * math.cos(math.pi * s)
        page.evaluate(f"window.scrollTo({{top:{y0 + (y1 - y0) * e}, behavior:'instant'}})")
        segs.append({"t": T, "dur": 1 / fps, "img": snap(), "xf": 0})
        T += 1 / fps

def y_of(sel_or_loc, offset=110):
    loc = page.locator(sel_or_loc) if isinstance(sel_or_loc, str) else sel_or_loc
    return loc.first.evaluate("e => e.getBoundingClientRect().top + scrollY") - offset

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": W, "height": H}, device_scale_factor=DPR,
                        is_mobile=True, has_touch=True, locale="ar")
    # لا يُرسل شيء فعلاً: نرد على FormSubmit برد ناجح
    ctx.route("**/formsubmit.co/**", lambda r: r.fulfill(status=200, content_type="application/json",
              body='{"success":"true","message":"ok"}'))
    ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    page = ctx.new_page()
    page.add_init_script("document.documentElement.style.scrollBehavior='auto'")
    page.goto(URL); page.evaluate("localStorage.clear()"); page.reload()
    page.evaluate("document.fonts.ready"); settle(900)

    # ── المقدمة (بطاقة بلا جوال) ──
    events.append({"t": 0, "type": "intro"})
    T = 4.6
    events.append({"t": T, "type": "phone_in"}); sfx("whoosh", -0.2)

    # ── ١ الرئيسية ──
    cap("الصفحة الرئيسية", "افتح رابط الموقع من جوالك، فتظهر لك واجهة العائلة", 1)
    hold(3.6, xf=0)
    cap("فروع العائلة", "تحت البحث بطاقات فروع العائلة، اضغط أي بطاقة لتفتح شجرة ذلك الفرع", 1)
    scroll_to(y_of(".bcard", 160), 1.8)
    hold(3.2)
    scroll_to(0, 1.0)
    hold(0.4)

    # ── ٢ ابحث عن اسمك ──
    sfx("whoosh", -0.15)
    cap("ابحث عن اسمك", "اكتب اسمك في مربع البحث، ولا يضر لو أخطأت في همزة أو حرف", 2)
    hold(1.6)
    type_in(page.locator("#herosearch input"), "عبد الهادي")
    hold(1.6)
    cap("اختر اسمك من النتائج", "تظهر الأسماء مع اسم الأب والجد حتى تميّز اسمك", 2)
    hold(1.6)
    tap(page.locator("#herosearch .results button").first)
    cap("«هل أنت … ؟»", "اضغط «نعم، هذا أنا» ليعرفك الموقع في كل الصفحات", 2)
    hold(2.4, xf=0.3)
    tap(page.locator("#yesme"), sound="page")
    cap("صفحتك في العائلة", "يُحفظ اختيارك في جوالك فقط، ويمكنك تغييره متى شئت", 3)
    hold(3.0, xf=0.35)

    # ── ٣ صفحة الشخص ──
    cap("صفحة كل شخص", "فيها نسبه كاملاً، ووالده ووالدته، وإخوته، وأبناؤه مجمّعين حسب الأم", 3)
    scroll_to(y_of(".mini", 120) if page.locator(".mini").count() else 500, 2.0)
    hold(3.4)
    scroll_to(99999, 1.6)
    hold(2.6)

    # ── ٤ البحث من الشريط السفلي + صلته بك ──
    sfx("whoosh", -0.15)
    cap("البحث من أي صفحة", "زر «بحث» في الشريط السفلي يفتح البحث وأنت في أي مكان", 4)
    hold(0.8)
    tap(page.locator("#tabsearch"), wait=500)
    hold(1.0, xf=0.2)
    type_in(page.locator("#topsearch input"), "هيثم")
    hold(1.2)
    tap(page.locator("#topsearch .results button").first, sound="page")
    cap("«صلته بك»", "في صفحة أي قريب يظهر مربع ذهبي يخبرك بصلته بك", 4)
    hold(1.4, xf=0.35)
    yb = page.evaluate("""() => { const e=[...document.querySelectorAll('main *')].find(x=>x.textContent.trim().startsWith('صلته بك')||x.textContent.trim().startsWith('صلتها بك'));
                         return e ? e.getBoundingClientRect().top + scrollY - 140 : 0 }""")
    scroll_to(yb, 1.4)
    hold(4.2)

    # ── ٥ الشجرة ──
    sfx("whoosh", -0.15)
    cap("الشجرة التفاعلية", "اضغط «الشجرة» في الشريط السفلي", 5)
    hold(0.6)
    tap(page.locator("#tabbar a[data-v=tree]"), sound="page")
    cap("الشجرة التفاعلية", "الجد في الأعلى، وتحته أبناؤه مجمّعين حسب الزوجة. اضغط أي بطاقة لترى أبناءه", 5)
    hold(3.4, xf=0.35)
    card = page.locator(".tcard", has_text="محمد عثمان").first
    scroll_to(y_of(card, 300), 1.0)
    hold(0.6)
    tap(card, sound="card")
    hold(2.4, xf=0.35)
    card = page.locator(".tcard", has_text="عبد المنعم").first
    scroll_to(y_of(card, 300), 1.0)
    hold(0.5)
    tap(card, sound="card")
    cap("المسار في الأعلى", "يبيّن أين أنت في الشجرة، واضغط أي اسم فيه لترجع إليه", 5)
    hold(3.6, xf=0.35)
    scroll_to(y_of(".tcard", 220), 1.2)
    hold(2.0)

    # ── ٦ صلة القرابة ──
    sfx("whoosh", -0.15)
    cap("صلة القرابة", "اعرف كيف تلتقي بأي شخص في العائلة", 6)
    hold(0.6)
    tap(page.locator("#tabbar a[data-v=relation]"), sound="page")
    cap("صلة القرابة", "اسمك مكتوب تلقائياً، فاكتب اسم الشخص الثاني فقط", 6)
    hold(2.4, xf=0.35)
    type_in(page.locator("#inb"), "هيثم")
    hold(0.8)
    tap(page.locator("#pb .results button").first)
    cap("النتيجة", "يوضح لك الموقع صلتكما، وأين تلتقيان من جهة الأب ومن جهة الأم", 6)
    hold(1.0, xf=0.3)
    scroll_to(y_of("#relout", 120), 1.4)
    hold(4.4)

    # ── ٧ المزيد: الإحصائيات والكتاب ──
    sfx("whoosh", -0.15)
    cap("قائمة «المزيد»", "فيها الإحصائيات، وتحميل كتاب العائلة PDF، وإرسال تصحيح", 7)
    hold(0.6)
    tap(page.locator("#tabmore"), sound="pop", wait=450)
    hold(3.2, xf=0.25)
    tap(page.locator("#moresheet a[href='#stats']"), sound="page")
    cap("الإحصائيات", "عدد أفراد العائلة والأجيال والفروع وأكثر الأسماء تكراراً", 7)
    hold(2.4, xf=0.35)
    scroll_to(700, 2.0)
    hold(2.2)

    # ── ٨ أرسل تصحيحاً ──
    sfx("whoosh", -0.15)
    cap("أرسل تصحيحاً", "إن رأيت خطأً أو اسماً ناقصاً فأخبرنا من هنا", 8)
    hold(0.5)
    tap(page.locator("#tabmore"), sound="pop", wait=450)
    hold(0.5, xf=0.2)
    tap(page.locator("#moresheet a[href='#fix']"), sound="page")
    hold(1.4, xf=0.35)
    cap("أرسل تصحيحاً", "اكتب اسمك ورسالتك، ورقم الجوال اختياري", 8)
    type_in(page.locator("#f-name"), "أحمد محمد", cps=10)
    hold(0.4)
    type_in(page.locator("#f-msg"), "ابني الأصغر يوسف غير موجود في الشجرة", cps=14)
    hold(1.0)
    cap("اضغط «إرسال»", "وتصل رسالتك إلينا مباشرة، ونضيفها في التحديث القادم بإذن الله", 8)
    tap(page.locator("#f-send"), sound="send", wait=900)
    hold(4.0, xf=0.3)

    # ── الختام ──
    events.append({"t": T, "type": "phone_out"}); sfx("whoosh", 0)
    events.append({"t": T + 0.4, "type": "outro"})
    T += 17.5
    events.append({"t": T, "type": "end"})
    b.close()

json.dump({"segs": segs, "events": events, "dur": T, "screen": [600, 1298]},
          open("/home/claude/video/timeline.json", "w"), ensure_ascii=False, indent=0)
print("frames", n, "duration", round(T, 1))

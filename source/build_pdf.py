import sys, html
sys.path.insert(0, "/home/claude/family")
from data import people, by_id, children, full_name, missing

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def ar(n): return str(n).translate(AR)
E = html.escape
SYM = {"ذكر": "♂", "أنثى": "♀", "غير معروف": ""}
CLS = {"ذكر": "m", "أنثى": "f", "غير معروف": "u"}
MAR = '<span class="mar">⚭</span>'

# ---------- أرقام الصفحات
ORDER = ["cover", "intro", "root", "ch1", "amna", "mhd", "bashir", "khidr", "others",
         "liba", "dahaba", "ali", "missing", "index"]
PG = {k: i + 1 for i, k in enumerate(ORDER)}
def pg(k): return ar(PG[k])

page_of = {}
CUR = [None]
def mark(p):
    page_of.setdefault(p["id"], CUR[0])

def label(p):
    d = ' <span class="dead">†</span>' if p["dead"] else ""
    return f'{E(p["name"])} <span class="sym">{SYM[p["gender"]]}</span>{d}'

def spouse_txt(p):
    return f'{MAR} {E(p["spouse"])}' if p["spouse"] else ""

def node(p, subs=(), extra="", show_spouse=True):
    mark(p)
    lines = []
    if show_spouse and p["spouse"]: lines.append(spouse_txt(p))
    lines += [s for s in subs if s]
    sub = "".join(f'<div class="sub">{l}</div>' for l in lines)
    return f'<div class="node {CLS[p["gender"]]} {extra}"><div class="nm">{label(p)}</div>{sub}</div>'

def grp(text): return f'<div class="node grp">{E(text)}</div>'

def kids_summary(p):
    ks = children(p["id"])
    parts = [E(c["name"]) + (" †" if c["dead"] else "") for c in ks]
    for c in ks: mark(c)
    if p["unknown"]: parts.append(E(p["unknown"]))
    return ("الأبناء: " + "، ".join(parts)) if parts else ""

def chip(p, subs=(), extra=""):
    mark(p)
    lines = [s for s in subs if s]
    sb = "".join(f'<span class="csub">{l}</span>' for l in lines)
    return f'<div class="chip {CLS[p["gender"]]} {extra}">{label(p)}{sb}</div>'

def unk(text): return f'<div class="chip u dashed">؟ {E(text)}</div>'

def stack(inner): return f'<div class="stack">{inner}</div>' if inner else ""

def gchips(p):
    """أبناء p كرقائق، مع ملخص أحفاده داخل كل رقاقة"""
    out = ""
    for c in children(p["id"]):
        subs = [spouse_txt(c), E(c["group"]) if c["group"] and not p["id"].endswith(".3") else "",
                E(c["notes"]) if c["notes"] in ("متزوجة", "غير متزوجة", "غير متزوج") else "",
                kids_summary(c)]
        out += chip(c, subs)
    if p["unknown"]: out += unk(p["unknown"])
    return stack(out)

def li(inner, kids=None, below=""):
    k = f"<ul>{''.join(kids)}</ul>" if kids else ""
    return f"<li>{inner}{below}{k}</li>"

def tree(root_li, zoom=1):
    return f'<div class="tree" style="zoom:{zoom}"><ul>{root_li}</ul></div>'

def child_subs(c):
    s = []
    if c["notes"] and ("متزوج" in c["notes"] or "تتزوج" in c["notes"] or "أبناء" in c["notes"]):
        s.append(E(c["notes"]))
    return s

def family_grid(p, top_subs=(), cols=4, zoom=1):
    cards = "".join(f'<div class="card">{node(c, child_subs(c))}{gchips(c)}</div>'
                    for c in children(p["id"]))
    return (f'<div style="zoom:{zoom}"><div class="fam-top">{node(p, top_subs, "head")}</div>'
            f'<div class="fgrid" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{cards}</div></div>')

pages = {}
def page(key, body, title=None, cls=""):
    n = PG[key]
    t = f'<div class="ptitle">{title}</div>' if title else ""
    foot = (f'<div class="foot">شجرة عائلة البشيراب · الإصدار الأول ٢٠٢٦ · صفحة {ar(n)}</div>'
            if n > 1 else "")
    pages[key] = f'<section class="page {cls}">{t}<div class="body">{body}</div>{foot}</section>'

def note(t): return f'<p class="note">{t}</p>'

# ================= ١ الغلاف
CUR[0] = "cover"
page("cover", """
<div class="cover">
  <div class="cv-top">بسم الله الرحمن الرحيم</div>
  <div class="cv-mark">❦</div>
  <h1>شجرة عائلة<br><span>البشيراب</span></h1>
  <div class="cv-sub">ذرية الجد محمد بشير</div>
  <div class="cv-ed">الإصدار الأول · نوفمبر ٢٠٢٦</div>
  <div class="cv-note">نسخة أولية — البيانات ما زالت تُجمع، وتُحدَّث في كل إصدار سنوي</div>
</div>""", cls="cover-page")

# ================= ٣ الشجرة الكبرى
CUR[0] = "root"
root = by_id["1"]
groups = {}
for c in children("1"):
    groups.setdefault(c["group"], []).append(c)
glis = []
for g, ks in groups.items():
    chips = "".join(chip(c, [f"الفصل الأول · صفحة {pg('ch1')}"] if c["id"] == "1.10" else [],
                         "hl" if c["id"] == "1.10" else "") for c in ks)
    glis.append(li(grp(g + " (الاسم غير معروف)"), below=stack(chips)))
page("root", tree(li(node(root, ["الجد الأكبر"], "rootnode"), glis), 1.32) +
     note("تقسيم الأبناء حسب الزوجات مبدئي، وأسماء الزوجات لم تُعرف بعد. "
          "فروع بقية الأبناء تُجمع للإصدارات القادمة."),
     title="الشجرة الكبرى: الجد محمد بشير وأبناؤه")

# ================= ٤ الفصل الأول: أبناء بشير
CUR[0] = "ch1"
famkey = {"1.10.1": "mhd", "1.10.3": "amna", "1.10.4": "liba", "1.10.5": "dahaba", "1.10.6": "ali"}
B0 = by_id["1.10"]
bg = {}
for c in children("1.10"):
    bg.setdefault(c["group"], []).append(c)
blis = []
for g, ks in bg.items():
    chips = ""
    for c in ks:
        subs = []
        if c["spouse"]: subs.append(f'{MAR} {E(c["spouse"])}')
        if c["id"] == "1.10.1": subs.append("جد عبد الهادي")
        subs.append(f"صفحة {pg(famkey[c['id']])}" if c["id"] in famkey else "بياناتها في الإصدار القادم")
        chips += chip(c, subs, "big")
    blis.append(li(grp(g + " (الاسم غير معروف)"), below=stack(chips)))
page("ch1", '<div class="chapter-head">الفصل الأول</div>' +
     tree(li(node(B0, ["ابن الجد محمد بشير"], "rootnode"), blis), 1.25) +
     note("أبناء بشير جميعهم متوفون رحمهم الله. ثلاث من بناته تزوجن من أبناء عمومتهن: "
          "آمنة من ابن فضل، وليبة من ابن شريف، ودهابة من ابن إدريس."),
     title="فرع بشير بن محمد بشير")

# ================= ٥ أسرة آمنة
CUR[0] = "amna"
page("amna", family_grid(by_id["1.10.3"], ["بنت بشير"], cols=4, zoom=1.32) +
     note("زوجها محمد فضل هو ابن فضل بن محمد بشير، فأبناؤها ينتسبون إلى فرع فضل."),
     title="أسرة آمنة بنت بشير")

# ================= ٦ أسرة محمد بن بشير (الجد)
CUR[0] = "mhd"
refs = {"1.10.1.1": "bashir", "1.10.1.3": "khidr"}
def count_sub(p):
    n = len(children(p["id"]))
    if p["id"] == "1.10.1.5": return "لا أبناء"
    return f"الأبناء: {ar(n)} · صفحة {pg(refs.get(p['id'], 'others'))}" if n else ""
mk = [li(node(c, [count_sub(c)])) for c in children("1.10.1")]
page("mhd", tree(li(node(by_id["1.10.1"], ["ابن بشير · جد عبد الهادي"], "rootnode"), mk), 1.02) +
     note("؟ اسم زوجة محمد بن بشير (أم أبنائه الستة) غير معروف بعد."),
     title="أسرة محمد بن بشير")

# ================= ٧ أسرة بشير بن محمد
CUR[0] = "bashir"
Bp = by_id["1.10.1.1"]
bk = []
for c in children(Bp["id"]):
    sub = E(c["notes"]) if c["notes"] else None
    gk = children(c["id"])
    bk.append(li(node(c, [sub]), below=stack("".join(chip(x) for x in gk)) if gk else ""))
page("bashir", tree(li(node(Bp, ["ابن محمد"], "rootnode"), bk), 1.5),
     title="أسرة بشير بن محمد بن بشير")

# ================= ٨ أسرة خضر
CUR[0] = "khidr"
K = by_id["1.10.1.3"]
kg = {}
for c in children(K["id"]):
    kg.setdefault(c["group"], []).append(c)
kl = []
for g, ks in kg.items():
    inner = "".join(chip(c) for c in ks)
    if g == "الزوجة الثانية": inner += unk("اثنان لم تُذكر أسماؤهما")
    kl.append(li(grp(g), below=stack(inner)))
page("khidr", tree(li(node(K, ["ابن محمد · له أربع زوجات"], "rootnode"), kl), 1.5) +
     note("؟ أسماء زوجات خضر الأربع، واسما الابنين الناقصين من الزوجة الثانية."),
     title="أسرة خضر بن محمد بن بشير")

# ================= ٩ بقية أسر أبناء محمد
CUR[0] = "others"
small = []
for pid in ["1.10.1.2", "1.10.1.4", "1.10.1.5", "1.10.1.6"]:
    p = by_id[pid]
    ks = children(pid)
    t = tree(li(node(p, ["لا أبناء"] if pid == "1.10.1.5" else []),
                below=stack("".join(chip(c) for c in ks)) if ks else ""), 1.3)
    small.append(f'<div class="cell">{t}</div>')
page("others", '<div class="grid2">' + "".join(small) + '</div>' +
     note("أبناء عواطف ينتسبون إلى أبيهم ناجي إدريس حامد، وهو من خارج فرع إدريس بن محمد بشير."),
     title="أسر الفاضل وعواطف وأحلام وعبد القادر")

# ================= ١٠ أسرة ليبة
CUR[0] = "liba"
page("liba", family_grid(by_id["1.10.4"], ["بنت بشير"], cols=4, zoom=1.32) +
     note(f"زوجها محمد شريف هو ابن شريف بن محمد بشير. "
          f"ابنها عبد الله تزوج فاطمة بنت علي بن بشير، وابنهما محمد ← صفحة {pg('ali')}. "
          f"وشيماء بنت الطيب تزوجت محمد صلاح فضل، حفيد فضل بن محمد بشير."),
     title="أسرة ليبة بنت بشير")

# ================= ١١ أسرة دهابة
CUR[0] = "dahaba"
Dp = by_id["1.10.5"]
dl = []
for c in children(Dp["id"]):
    dl.append(li(node(c, child_subs(c)), below=gchips(c)))
page("dahaba", tree(li(node(Dp, ["بنت بشير"], "rootnode"), dl), 1.18) +
     note("زوجها عبد الله هو ابن إدريس بن محمد بشير. "
          "ابناها عبد الجابر وعماد متوفيان، ومبارك زوج ماجدة متوفى، رحمهم الله."),
     title="أسرة دهابة بنت بشير")

# ================= ١٢ أسرة علي
CUR[0] = "ali"
page("ali", family_grid(by_id["1.10.6"], ["ابن بشير · من الزوجة الثانية"], cols=3, zoom=1.32) +
     note(f"فاطمة بنت علي تزوجت أولاً عبد الله بن ليبة (ابن عمتها) ← صفحة {pg('liba')}، "
          f"وأنجبت منه محمداً، ثم تزوجت مرة أخرى وأنجبت سميرة."),
     title="أسرة علي بن بشير")

# ================= ١٣ ما ينقصنا
CUR[0] = "missing"
items = "".join(f"<li>{E(q)}</li>" for q in missing)
page("missing", '<p>هذه المعلومات نبحث عنها للإصدار القادم. إن كنت تعرف شيئاً منها فأخبرنا به:</p>'
     f'<ol class="missing">{items}</ol>', title="ما ينقصنا")

# الأزواج المذكورون نصاً
for pid, k in [("1.11.1", "amna"), ("1.9.1", "liba"), ("1.8.1", "dahaba"), ("1.11.2.1", "liba")]:
    page_of.setdefault(pid, k)

# ================= ١٤ الفهرس
CUR[0] = "index"
def short(p): return " ".join(full_name(p).split(" ")[:5])
def key(p):
    n = p["name"]; return (n[2:] if n.startswith("ال") else n, full_name(p))
idx = sorted([p for p in people if p["id"] in page_of], key=key)
rowl = [f'<div class="ix"><span class="ixn">{E(short(p))}{" †" if p["dead"] else ""}</span>'
        f'<span class="ixp">{pg(page_of[p["id"]])}</span></div>' for p in idx]
missing_idx = [p["name"] for p in people if p["id"] not in page_of]
PER = 84
chunks = [rowl[i:i + PER] for i in range(0, len(rowl), PER)]
for j, ch in enumerate(chunks):
    k = "index" if j == 0 else f"index{j+1}"
    if k not in PG:
        ORDER.append(k); PG[k] = len(ORDER)
    page(k, f'<div class="index">{"".join(ch)}</div>',
         title="فهرس الأسماء" + (" (تابع)" if j else ""))

# ================= ٢ المقدمة (بعد معرفة الصفحات)
CUR[0] = "intro"
legend = """
<table class="legend">
<tr><td><div class="chip m">اسم <span class="sym">♂</span></div></td><td>ذكر</td></tr>
<tr><td><div class="chip f">اسم <span class="sym">♀</span></div></td><td>أنثى</td></tr>
<tr><td class="big"><span class="mar">⚭</span></td><td>متزوج من</td></tr>
<tr><td class="big dead">†</td><td>متوفى، رحمه الله</td></tr>
<tr><td class="big">★</td><td>سنة الميلاد</td></tr>
<tr><td><div class="chip u dashed">؟</div></td><td>معلومة ناقصة نرجو من يعرفها أن يخبرنا بها</td></tr>
<tr><td class="big">←</td><td>انظر صفحة أخرى في الكتاب</td></tr>
</table>"""
toc = [("الشجرة الكبرى: الجد محمد بشير وأبناؤه", "root", False),
       ("الفصل الأول: فرع بشير بن محمد بشير", "ch1", False),
       ("أسرة آمنة بنت بشير", "amna", True), ("أسرة محمد بن بشير", "mhd", True),
       ("أسرة بشير بن محمد", "bashir", True), ("أسرة خضر بن محمد", "khidr", True),
       ("أسر الفاضل وعواطف وأحلام وعبد القادر", "others", True),
       ("أسرة ليبة بنت بشير", "liba", True), ("أسرة دهابة بنت بشير", "dahaba", True),
       ("أسرة علي بن بشير", "ali", True), ("ما ينقصنا", "missing", False),
       ("فهرس الأسماء", "index", False)]
tr = "".join(f'<tr><td class="{"ind" if i else ""}">{t}</td><td>{pg(k)}</td></tr>' for t, k, i in toc)
page("intro", f"""
<p>هذا الكتاب محاولة لجمع ذرية الجد <b>محمد بشير</b> في مكان واحد، حتى يعرف الأبناء والأحفاد أهلهم
وصلة كل واحد منهم بالآخر. ولأن العائلة كبيرة ومتشعبة، قُسّم الكتاب إلى فصول: لكل فرع من فروع العائلة فصل خاص به.</p>
<p>هذا هو <b>الإصدار الأول</b>، وفيه فرع <b>بشير بن محمد بشير</b>. وفيه أيضاً روابط مع فروع فضل وشريف وإدريس من خلال الزيجات.
وستُضاف بقية الفروع في الإصدارات القادمة بإذن الله، إذ يصدر الكتاب مُحدَّثاً كل سنة.</p>
<h2>دليل الرموز</h2>{legend}
<h2>كيف تساهم؟</h2>
<p>إن وجدت خطأً أو اسماً ناقصاً، أو عندك بيانات فرعك، فأرسلها إلى عبد الهادي بشير.
وفي صفحة {pg('missing')} قائمة بالمعلومات التي نبحث عنها الآن.</p>
<h2>محتويات الكتاب</h2><table class="toc">{tr}</table>
""", title="مقدمة")

CSS = open("/home/claude/family/book.css").read()
body = "".join(pages[k] for k in ORDER)
open("/home/claude/family/book.html", "w").write(
    f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
    f'<title>شجرة عائلة البشيراب</title><style>{CSS}</style></head><body>{body}</body></html>')
print("pages", len(pages), "indexed", len(idx), "not shown:", missing_idx)

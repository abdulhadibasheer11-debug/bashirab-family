import sys, html
sys.path.insert(0, "/home/claude/family")
from data import people, by_id, children, full_name

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def ar(n): return str(n).translate(AR)
E = html.escape
SYM = {"ذكر": "♂", "أنثى": "♀", "غير معروف": ""}
CLS = {"ذكر": "m", "أنثى": "f", "غير معروف": "u"}
MAR = '<span class="mar">⚭</span>'

# ---------- أرقام الصفحات
ORDER = ["cover", "intro", "root", "ch1", "jara", "amna", "mhd", "bashir", "khidr", "others",
         "liba", "dahaba", "ali", "ch2", "nemat", "monem1", "monem2", "ch3", "sharif", "dyab", "husein", "khairy", "abdoun", "abdoun2", "ajaib", "osman", "ch4",
         "ch11", "hakim", "ahmad", "abddaim", "abddaim2", "ali0", "sisters", "index"]
PG = {k: i + 1 for i, k in enumerate(ORDER)}
def pg(k): return ar(PG[k])

page_of = {}
CUR = [None]
def mark(p):
    page_of.setdefault(p["id"], CUR[0])

def label(p):
    d = ' <span class="dead">(ر)</span>' if p["dead"] else ""
    al = f' «{E(p["alias"])}»' if p.get("alias") else ""
    return f'{E(p["name"])}{al} <span class="sym">{SYM[p["gender"]]}</span>{d}'

def spouse_txt(p):
    return f'{MAR} {E(p["spouse"])}' if p["spouse"] else ""

def node(p, subs=(), extra="", show_spouse=True):
    mark(p)
    lines = []
    if show_spouse and p["spouse"]: lines.append(spouse_txt(p))
    lines += [s for s in subs if s]
    sub = "".join(f'<div class="sub">{l}</div>' for l in lines)
    return f'<div class="node {CLS[p["gender"]]} {"dd" if p["dead"] else ""} {extra}"><div class="nm">{label(p)}</div>{sub}</div>'

def grp(text): return f'<div class="node grp">{E(text)}</div>'

def kids_summary(p):
    ks = children(p["id"])
    parts = [E(c["name"]) + (" (ر)" if c["dead"] else "") for c in ks]
    for c in ks: mark(c)
    if p["unknown"]: parts.append(E(p["unknown"]))
    return ("الأبناء: " + "، ".join(parts)) if parts else ""

def chip(p, subs=(), extra=""):
    mark(p)
    lines = [s for s in subs if s]
    sb = "".join(f'<span class="csub">{l}</span>' for l in lines)
    return f'<div class="chip {CLS[p["gender"]]} {"dd" if p["dead"] else ""} {extra}">{label(p)}{sb}</div>'

def unk(text): return f'<div class="chip u dashed">؟ {E(text)}</div>'

def stack(inner): return f'<div class="stack">{inner}</div>' if inner else ""

def gchips(p):
    """أبناء p كرقائق، مع ملخص أحفاده داخل كل رقاقة"""
    out = ""
    for c in children(p["id"]):
        subs = [spouse_txt(c), E(c["group"].split(":")[0]) if c["group"] and not c["group"].startswith("الأم") and p["gender"] == "ذكر" and p["id"] != "1.10.1.3" else "",
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
  <div class="cv-sub">ذرية الجد بشير</div>
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
    CH = {"1.10": ("الفصل الأول", "ch1"), "1.12": ("الفصل الثاني", "ch2"), "1.11": ("الفصل الثالث", "ch3"),
          "1.9": ("الفصل الرابع", "sharif"), "1.1": ("الفصل الخامس", "dyab"), "1.5": ("الفصل السادس", "khairy"),
          "1.6": ("الفصل السابع", "abdoun"), "1.4": ("الفصل الثامن", "ajaib"), "1.2": ("الفصل التاسع", "osman")}
    PART = {"1.8", "1.13", "1.14", "1.15"}
    def rsubs(c):
        if c["id"] in CH: return [f"{CH[c['id']][0]} · صفحة {pg(CH[c['id']][1])}"]
        if c["notes"] and c["id"] in ("1.17", "1.18"): return [E(c["notes"])]
        if c["id"] in PART: return [f"بيانات جزئية · صفحة {pg('ch4')}"]
        return []
    chips = "".join(chip(c, rsubs(c), "hl" if c["id"] in CH else "") for c in ks)
    glis.append(li(grp(g if "(" in g or ":" in g or not g.startswith("الزوجة") else g + " (الاسم غير معروف)"), below=stack(chips)))
TOPSUB = {"1": "", "0.2": f"ابنه الوحيد حسين ⚭ عجائب بنت محمد بشير ← صفحة {pg('ajaib')}",
          "0.3": f"← صفحة {pg('ahmad')}", "0.4": f"← صفحة {pg('hakim')}",
          "0.5": f"← صفحة {pg('abddaim')}", "0.8": f"← صفحة {pg('ali0')}",
          "0.6": f"← صفحة {pg('sisters')}", "0.7": f"← صفحة {pg('sisters')}", "0.9": f"← صفحة {pg('sisters')}", "0.10": f"← صفحة {pg('sisters')}"}
top = (f'<div class="fam-top" style="zoom:1.15">{node(by_id["0"], ["الجد الأكبر"], "head")}</div>'
       f'<div class="chips" style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:6px 0 4px;zoom:1.1">'
       + "".join(chip(c, [TOPSUB.get(c["id"], "")], "hl" if c["id"] == "1" else "") for c in children("0")) + '</div>')
page("root", top + tree(li(node(root, ["ابن الجد الأكبر بشير"], "rootnode"), glis), 1.2) +
     note("الجد الأكبر بشير رحمه الله، وأبناؤه محمد وشقيقه طمبل وأحمد وحاكم رحمهم الله. "
          "لبشير زوجتان: الأولى أم محمد وطمبل وفاطمة «أم النوراب» وآمنة «أم الدبلاب»، والثانية أم عبد الدائم وأحمد وحاكم وعلي، "
          "ومن زوجاته فدلم حاج محمد، وله بنتان أخريان نفرين ودهابة. "
          "ولمحمد بشير ثلاث زوجات: شُمَّة، ثم كلتوم أم دياب وعثمان وعجائب، ثم آمنة الحاج، رحمهن الله. "
          f"وفروع إخوة محمد بشير وأخواته في الفصل الحادي عشر ← صفحة {pg('ch11')}."),
     title="الشجرة الكبرى: الجد الأكبر بشير وذريته")

# ================= ٤ الفصل الأول: أبناء بشير
CUR[0] = "ch1"
famkey = {"1.10.2": "jara", "1.10.1": "mhd", "1.10.3": "amna", "1.10.4": "liba", "1.10.5": "dahaba", "1.10.6": "ali"}
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
    blis.append(li(grp(g if ":" in g else g + " (الاسم غير معروف)"), below=stack(chips)))
page("ch1", '<div class="chapter-head">الفصل الأول</div>' +
     tree(li(node(B0, ["ابن الجد محمد بشير"], "rootnode"), blis), 1.25) +
     note("أبناء بشير جميعهم متوفون رحمهم الله. ثلاث من بناته تزوجن من أبناء عمومتهن: "
          "آمنة من ابن فضل، وليبة من ابن شريف، ودهابة من ابن إدريس."),
     title="فرع بشير بن محمد بشير")

# ================= ٥ أسرة آمنة
CUR[0] = "jara"
page("jara", family_grid(by_id["1.10.2"], ["بنت بشير"], cols=3, zoom=1.4) +
     note("فاطمة بنت جارة زوجة سيد أحمد بن فضل بن محمد بشير رحمه الله، فأبناؤها من فرع فضل أيضاً. "
          ""),
     title="أسرة جارة بنت بشير")

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
page("mhd", tree(li(node(by_id["1.10.1"], ["ابن بشير · جد عبد الهادي"], "rootnode"), mk), 0.8) +
     note("أبناؤه من أم الملك بنت محمد عثمان. وعبد القادر الأول توفي صغيراً رحمه الله، فسُمّي أخوه عليه."),
     title="أسرة محمد بن بشير")

# ================= ٧ أسرة بشير بن محمد
CUR[0] = "bashir"
Bp = by_id["1.10.1.1"]
bk = []
for c in children(Bp["id"]):
    sub = E(c["notes"]) if c["notes"] else None
    gk = children(c["id"])
    bk.append(li(node(c, [sub]), below=stack("".join(chip(x) for x in gk)) if gk else ""))
page("bashir", tree(li(node(Bp, ["ابن محمد"], "rootnode"), bk), 1.4),
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
page("khidr", tree(li(node(K, ["ابن محمد · له أربع زوجات"], "rootnode"), kl), 1.3) +
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
page("dahaba", tree(li(node(Dp, ["بنت بشير"], "rootnode"), dl), 1.08) +
     note("زوجها عبد الله هو ابن إدريس بن محمد بشير. "
          "ابناها عبد الجابر وعماد متوفيان، ومبارك زوج ماجدة متوفى، رحمهم الله."),
     title="أسرة دهابة بنت بشير")

# ================= ١٢ أسرة علي
CUR[0] = "ali"
page("ali", family_grid(by_id["1.10.6"], ["ابن بشير · أمه فاطمة فتح الرحمن"], cols=4, zoom=1.25) +
     note(f"فاطمة بنت علي تزوجت أولاً عبد الله بن ليبة (ابن عمتها) ← صفحة {pg('liba')}، "
          f"وأنجبت منه محمداً، ثم تزوجت مرة أخرى وأنجبت سميرة. وجمال الأول توفي صغيراً رحمه الله، فسُمّي أخوه عليه."),
     title="أسرة علي بن بشير")

# ================= الفصل الثاني: فرع محمد عثمان
CUR[0] = "ch2"
MO = by_id["1.12"]
REFS2 = {"1.12.2": lambda c: f"له زوجتان · الأبناء: {ar(len(children(c['id'])))} ← صفحة {pg('monem1')}",
         "1.12.3": lambda c: f"أم بشير والفاضل وخضر وعواطف وأحلام وعبد القادر ← صفحة {pg('mhd')}",
         "1.12.6": lambda c: f"الأبناء: {ar(len(children(c['id'])))} ← صفحة {pg('nemat')}"}
cards = ""
for c in children("1.12"):
    subs = [E(c["notes"]) if c["notes"] and c["id"] != "1.12.2" else ""]
    inner = ""
    if c["id"] in REFS2:
        subs.append(REFS2[c["id"]](c))
        if c["id"] == "1.12.3": [mark(x) for x in children(c["id"])]
    else:
        inner = gchips(c)
    cards += f'<div class="card">{node(c, subs)}{inner}</div>'
page("ch2", '<div class="chapter-head">الفصل الثاني</div>' +
     f'<div style="zoom:1.0"><div class="fam-top">{node(MO, ["ابن الجد محمد بشير"], "head")}</div>'
     f'<div class="fgrid" style="grid-template-columns:repeat(3,minmax(0,1fr))">{cards}</div></div>' +
     note("زوجة محمد عثمان فاطمة حمد وديدي، أم أبنائه. توفي منهم: زينب وعبد المنعم وأم الملك ومملكة وحسن، رحمهم الله. "
          "زوج زينب الثاني علي خيري حفيد الجد من فرع خيري. أم الملك زوجة محمد بن بشير، جد عبد الهادي. "
          "سليم بن مملكة تزوج صفاء بنت نعمات."),
     title="فرع محمد عثمان بن محمد بشير")

CUR[0] = "nemat"
page("nemat", family_grid(by_id["1.12.6"], ["بنت محمد عثمان"], cols=4, zoom=1.25) +
     note("زوجها الحاج محمد «حانجمت» بن شريف بن محمد بشير. آمنة تزوجت عبد الإله بن زينب (ابن خالتها)، "
          "وصفاء تزوجت سليم بن مملكة (ابن خالتها)."),
     title="أسرة نعمات بنت محمد عثمان")

def monem_grid(ks, cols, zoom, head=True):
    cards = ""
    for c in ks:
        subs = child_subs(c)
        if c["group"] == "الزوجة الثانية": subs.append("من الزوجة الثانية")
        if "توأم" in c["notes"]: subs.append(E(c["notes"]))
        if c["id"] == "1.12.2.2": subs.append(f"أسرتها ← صفحة {pg('bashir')}")
        cards += f'<div class="card">{node(c, subs)}{gchips(c)}</div>'
    top = f'<div class="fam-top">{node(MN, ["ابن محمد عثمان · له زوجتان"], "head")}</div>' if head else ""
    return (f'<div style="zoom:{zoom}">{top}'
            f'<div class="fgrid" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{cards}</div></div>')

MN = by_id["1.12.2"]
mk2 = children("1.12.2")
CUR[0] = "monem1"
page("monem1", monem_grid(mk2[:5], 3, 1.18) +
     note("نجاة زوجة بشير بن محمد بن بشير، فأبناؤها من فرع بشير أيضاً. "
          "ووداد تزوجت كمال عبد الله الحاج محمد عبد الله محمد بشير."),
     title="أسرة عبد المنعم بن محمد عثمان")
CUR[0] = "monem2"
page("monem2", monem_grid(mk2[5:], 3, 1.18, head=False) +
     note("نفيسة تزوجت محمود علي خيري، حفيد خيري بن محمد بشير. "
          "ندى تزوجت وليد إرساوي. "
          "؟ اسما زوجتي عبد المنعم، وزوج حنان."),
     title="أسرة عبد المنعم بن محمد عثمان (تابع)")

# ================= الفصل الثالث: فرع فضل
CUR[0] = "ch3"
cards = ""
for c in children("1.11"):
    if c["id"] == "1.11.2":
        subs = [f"أبناؤه من آمنة بنت بشير ← صفحة {pg('amna')}"]; [mark(x) for x in children(c["id"])]; inner = ""
    else:
        subs = [E(c["notes"]) if c["notes"] else "", "أمه " + E(c["group"].split(": ")[-1]) if ": " in c["group"] else ""]; inner = gchips(c)
    cards += f'<div class="card">{node(c, subs)}{inner}</div>'
page("ch3", '<div class="chapter-head">الفصل الثالث</div>' +
     f'<div style="zoom:1.04"><div class="fam-top">{node(by_id["1.11"], ["ابن الجد محمد بشير"], "head")}</div>'
     f'<div class="fgrid" style="grid-template-columns:repeat(4,minmax(0,1fr))">{cards}</div></div>' +
     note("أبناء فضل كلهم متوفون إلا مهدي ونصرة، رحمهم الله. "
          f"سيد أحمد تزوج فاطمة بنت جارة بنت بشير ← صفحة {pg('jara')}. "
          f"محمد صلاح تزوج شيماء بنت الطيب ← صفحة {pg('liba')}. "
          "لفضل أربع زوجات: ستنا بنت عبد الدائم بن بشير أم محمد، ومكة الزين بنت حاكم بن بشير أم عبد الدائم، "
          "وسعيدة ساتي أم بشير ومهدي وسيد أحمد ونصرة، وفاطمة عثمان أم صلاح. "
          "زوجتا صلاح: شريفة حسن حسين طمبل، وستنا الحاج سعيد. ؟ أبناء عبد الدائم ونصرة."),
     title="فرع فضل بن محمد بشير")

# ================= الفصل الرابع: فرع شريف
CUR[0] = "sharif"
sh_cards = ""
for c, ref, wife in [(by_id["1.9.1"], "nemat", "نعمات بنت محمد عثمان"), (by_id["1.9.2"], "liba", "ليبة بنت بشير")]:
    sh_cards += (f'<div class="card">{node(c, [f"أبناؤه من {wife} · التفاصيل ← صفحة {pg(ref)}"])}'
                 f'{gchips(c)}</div>')
page("sharif", '<div class="chapter-head">الفصل الرابع</div>' +
     f'<div style="zoom:1.3"><div class="fam-top">{node(by_id["1.9"], ["ابن الجد محمد بشير"], "head")}</div>'
     f'<div class="fgrid" style="grid-template-columns:repeat(2,minmax(0,1fr))">{sh_cards}</div></div>' +
     note("شريف بن محمد بشير متوفى رحمه الله، وله ابنان: الحاج محمد «حانجمت» ومحمد. "
          "الحاج محمد تزوج نعمات بنت محمد عثمان، ومحمد تزوج ليبة بنت بشير، فأبناؤهما من فرعي محمد عثمان وبشير أيضاً."),
     title="فرع شريف بن محمد بشير")

# ================= الفصل الخامس: فرع دياب
def branch_page(key, head_id, head_sub, refs, cols, zoom, chap, notes_txt, title):
    CUR[0] = key
    cards = ""
    for c in children(head_id):
        subs = [E(c["notes"]) if c["notes"] and "له زوجتان" not in c["notes"] else ""]
        if "الثانية" in c["group"]: subs.append("من الزوجة الثانية")
        if c["id"] in refs:
            subs.append(refs[c["id"]](c)); inner = ""
            for x in children(c["id"]): mark(x)
        else:
            inner = gchips(c)
        cards += f'<div class="card">{node(c, subs)}{inner}</div>'
    page(key, f'<div class="chapter-head">{chap}</div>' +
         f'<div style="zoom:{zoom}"><div class="fam-top">{node(by_id[head_id], [head_sub], "head")}</div>'
         f'<div class="fgrid" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{cards}</div></div>' +
         note(notes_txt), title=title)

branch_page("dyab", "1.1", "ابن الجد محمد بشير، من زوجته الثانية كلتوم · له زوجتان",
    {"1.1.1": lambda c: f"أبناؤه من جارة بنت بشير ← صفحة {pg('jara')}",
     "1.1.3": lambda c: f"له زوجتان · الأبناء: {ar(len(children(c['id'])))} ← صفحة {pg('husein')}"},
    4, 0.85, "الفصل الخامس",
    "لدياب زوجتان: الأولى، وهي الأقدم زواجاً، روضة الطاهر، أم محمد «شيني» وفاطمة وفرح رحمه الله؛ "
    "والثانية زينب فضل حرنان، أم محمد وحسن وحسين وفاطمة وآمنة وشريفة وكلتوم "
    "(وتكرار الأسماء بين أبناء الزوجتين كان مألوفاً). "
    "فاطمة بنت روضة زوجة إبراهيم فضل، وكلتوم زوجة عبد الجليل محمود. "
    "حسن تزوج قسيمة طمبل حسين طمبل بشير. "
    "أبناء آمنة: عبد الله وحسن زوجا سامية بنت عبد المنعم، ووليد زوج ندى بنت عبد المنعم. "
    "عبد المنعم بن فاطمة لقبه «عبده ربه».",
    "فرع دياب بن محمد بشير")

CUR[0] = "husein"
page("husein", family_grid(by_id["1.1.3"], ["ابن دياب محمد بشير"], cols=4, zoom=1.12) +
     note("زوجته الأولى تومة بنت عثمان بن محمد بشير، والثانية عز اليان سعيد. "
          "وعيدة يقال لها زينب لأن أم أبيها اسمها زينب. "
          f"حسيبة زوجة بشير بن جارة وأم ابنه دياب ← صفحة {pg('jara')}."),
     title="أسرة حسين بن دياب")

# ================= الفصل السادس: فرع خيري
branch_page("khairy", "1.5", "ابن الجد محمد بشير",
    {}, 3, 1.12, "الفصل السادس",
    "زوجة خيري ستنا عمر. علي تزوج زينب بنت محمد عثمان أولاً، فأنجبت خيري وعبد الإله، ثم رقية محمد دياب أم محمود ومحجوب وصفاء. "
    "صفاء بنت علي زوجة أحمد المصطفى بن عبد المنعم، ورقية بنت زينب زوجة خالد بن محمد عثمان. "
    "بقارة تزوج فاطمة ثم أختها زينب بعد وفاتها. حسين بن فاطمة تزوج آسية بنت شامة، وعثمان بن زينب تزوج آمنة بنت شامة، رحمهم الله. واسم شامة نفرين، و«شامة» لقبها. "
    "وفريال بنت خيري بن علي تزوجت محمد عبد الله محمد طاهر، وأبناؤها وافي وأحمد.",
    "فرع خيري بن محمد بشير")
for x in children("1.12.1.2.2"): mark(x)

# ================= الفصل السابع: فرع عبد الله «عبدون»
CUR[0] = "abdoun"
ab_cards = ""
for c in children("1.6"):
    subs = [E(c["notes"]) if c["notes"] else "", "أمه " + E(c["group"].split(": ")[-1]) if ": " in c["group"] else ""]
    if c["id"] == "1.6.2":
        subs.append(f"أبناؤها من طمبل حسين ← صفحة {pg('ajaib')}"); inner = ""
    else:
        inner = gchips(c)
    if c["id"] == "1.6.1": subs.append(f"أسرة ابنه عبد الله ← صفحة {pg('abdoun2')}")
    ab_cards += f'<div class="card">{node(c, subs)}{inner}</div>'
page("abdoun", '<div class="chapter-head">الفصل السابع</div>' +
     f'<div style="zoom:0.95"><div class="fam-top">{node(by_id["1.6"], ["ابن الجد محمد بشير، من زوجته الأولى شُمَّة"], "head")}</div>'
     f'<div class="fgrid" style="grid-template-columns:repeat(4,minmax(0,1fr))">{ab_cards}</div></div>' +
     note("لعبد الله «عبدون» رحمه الله زوجتان: زينب الملك طمبل، أم فاطمة «قلة» وحسن، وتزوجها بعده أخوه عثمان؛ "
          "وآمنة الطاهر من جزيرة أرتقاشا، أم الحاج محمد «حانجمت» وأحمد وعلي ومحمد «باشا» وحسن ومحمود وستنا. "
          "وللحاج محمد زوجتان: سبوكة زبير الملك، أم عبد الله وزبير ودهابة؛ ونصرة علي من حامدنارتي، أم حسين وفاطمة وآمنة «آمنة الشيخ». "
          "آمنة زوجة محمد بن علي بن عبد الدائم بن بشير، ودهابة زوجة عبد المنعم حمد الملك، وستنا بنت عبدون زوجة فضل سلطان «بيه»."),
     title="فرع عبد الله «عبدون» بن محمد بشير")

CUR[0] = "abdoun2"
page("abdoun2", family_grid(by_id["1.6.1.1"], ["ابن الحاج محمد «حانجمت» بن عبد الله «عبدون» بن محمد بشير"], cols=4, zoom=0.98) +
     note("لعبد الله بن الحاج محمد رحمه الله ثلاث زوجات: فاطمة فقيري، ثم رقية «اللقية» بنت طمبل رحمها الله، ثم عائشة عبد الله. "
          f"منى زوجة خضر بن محمد بن بشير وأم بنته فاطمة ← صفحة {pg('khidr')}، وسبوكة زوجة عباس بن طمبل ← صفحة {pg('ajaib')}. "
          f"كمال تزوج وداد بنت عبد المنعم ← صفحة {pg('monem1')}."),
     title="أسرة عبد الله بن الحاج محمد «حانجمت»")

# ================= الفصل الثامن: عجائب بنت محمد بشير وزوجها حسين بن طمبل
CUR[0] = "ajaib"
mark(by_id["1.4"]); mark(by_id["0.2"])
page("ajaib", '<div class="chapter-head">الفصل الثامن</div>' +
     family_grid(by_id["0.2.1"], ["ابن طمبل بن بشير"], cols=4, zoom=0.92) +
     note("عجائب بنت الجد محمد بشير، من زوجته الثانية كلتوم، تزوجت حسين بن طمبل بن بشير رحمهما الله، "
          "وهو ابن طمبل الوحيد، أمه من إرس، وتوفي في حياة أبيه. "
          f"أحمد تزوج فاطمة بنت دياب ← صفحة {pg('dyab')}. "
          "وطمبل تزوج فاطمة «قلة» بنت عبد الله «عبدون»، فأنجبت عباس واللقية وسعاد: "
          f"اللقية زوجة عبد الله بن الحاج محمد ← صفحة {pg('abdoun')}، وسعاد زوجة عبد المنعم بن محمد عثمان ← صفحة {pg('monem1')}، "
          "وعباس رحمه الله تزوج سبوكة بنت عبد الله. وقسيمة زوجة حسن بن دياب. "
          "وحسن تزوج فاطمة بنت علي بن عبد الدائم بن محمد بشير، ثم زكية حسين؛ "
          f"وبنته شريفة زوجة صلاح بن فضل ← صفحة {pg('ch3')}. "
          "وفاطمة تزوجت فرح أنقراوي، وابنها محمد تزوج سعيدة بنت أحمد."),
     title="فرع عجائب بنت محمد بشير وزوجها حسين بن طمبل")

# ================= الفصل التاسع: فرع عثمان
CUR[0] = "osman"
page("osman", '<div class="chapter-head">الفصل التاسع</div>' +
     family_grid(by_id["1.2"], ["ابن الجد محمد بشير، من زوجته الثانية كلتوم"], cols=5, zoom=0.95) +
     note("لعثمان رحمه الله زوجتان: آمنة فضل إسماعيل، من قبيلة محسية، أم خضر وحسن وتومة وزهرة، وزينب الملك طمبل، أم طمبل، "
          "وكانت زينب زوجة أخيه عبد الله «عبدون» قبله. "
          "خضر تزوج آسيا بنت شريفة بنت دياب، وابنه فوزي تزوج تهاني بنت حسين بن دياب. "
          f"وتومة زوجة حسين بن دياب الأولى ← صفحة {pg('husein')}. "
          "ولطمبل رحمه الله ثلاث زوجات: عائشة ساتي، وفاطمة مسيكين رحمها الله، وفتحية محمد حسن أحمد «تاتا»؛ وابنه طمبل سُمّي عليه لأنه وُلد بعد وفاته. "
          "صلاح تزوج كلتوم بنت حسين بن دياب، وحفصة رحمها الله زوجة مهدي بن فضل وأم أبنائه "
          f"← صفحة {pg('ch3')}."),
     title="فرع عثمان بن محمد بشير")

# ================= الفصل العاشر: بيانات جزئية من فروع أخرى
CUR[0] = "ch4"
def mini(pid, rows, z=1.2):
    return f'<div class="cell">{tree(li(node(by_id[pid], [E(by_id[pid]["notes"])] if pid == "1.15" else []), below=stack(rows)), z)}</div>'
cells = [
  mini("1.8", chip(by_id["1.8.3"], [E(by_id["1.8.3"]["notes"])]) +
              chip(by_id["1.8.1"], [spouse_txt(by_id["1.8.1"]), f"أبناؤه من دهابة ← صفحة {pg('dahaba')}"]) +
              chip(by_id["1.8.2"], [E(by_id["1.8.2"]["notes"])]) +
              chip(by_id["1.8.4"], [spouse_txt(by_id["1.8.4"]), kids_summary(by_id["1.8.4"])])),
  mini("1.13", chip(by_id["1.13.1"], ["أبناؤها: " + "، ".join(c["name"] for c in children("1.13.1"))]) +
               chip(by_id["1.13.1.1"], ["بنت تومة", kids_summary(by_id["1.13.1.1"])]) +
               chip(by_id["1.13.1.2"], ["بنت تومة", spouse_txt(by_id["1.13.1.2"]), f"← صفحة {pg('jara')}"]) +
               chip(by_id["1.13.2"], ["بنت دوشة"]) + chip(by_id["1.13.3"]) + chip(by_id["1.13.4"]), 1.0),
  mini("1.14", chip(by_id["1.14.1"], ["ابنها الوحيد", "ابنه عبد العاطي (ر)"])),
]
mark(by_id["1.14.1.1"])
for c in children("1.13.1"): mark(c)
for x in ["1.15"]: mark(by_id[x])
page("ch4", '<div class="chapter-head">الفصل العاشر</div><div class="grid2">' + "".join(cells) + '</div>' +
     note("هذه فروع لم تُجمع بياناتها بعد، وفيها ما عُرف حتى الآن من خلال الزيجات بين الفروع. "
          "محاسن بنت تومة بنت دوشة زوجة سر الختم بن جارة بنت بشير. "
          "فدلم تزوجت أحمد أنقراوي، وتوفيت هي وابنها عبد الله وحفيدها عبد العاطي، رحمهم الله. "
          "وإدريس بن محمد بشير زوجته عائشة أبكر. وعباس بن محمد بشير هاجر إلى مصر، وهو مفقود لا يُعرف عنه شيء."),
     title="من فروع أخرى (بيانات جزئية)")
# ================= الفصل الحادي عشر: إخوة محمد بشير وأخواته (من كراسة العائلة، نوفمبر ٢٠٢٦)
def fam_page(key, head_id, head_sub, refs, cols, zoom, notes_txt, title, chap=""):
    CUR[0] = key
    cards = ""
    for c in children(head_id):
        subs = [E(c["notes"]) if c["notes"] else "",
                "أمه " + E(c["group"].split(": ")[-1]) if ": " in c["group"] and not c["group"].startswith("الأم") else ""]
        if c["id"] in refs:
            subs.append(refs[c["id"]](c)); inner = ""
            for x in children(c["id"]): mark(x)
        else:
            inner = gchips(c)
        cards += f'<div class="card">{node(c, subs)}{inner}</div>'
    ch = f'<div class="chapter-head">{chap}</div>' if chap else ""
    page(key, ch + f'<div style="zoom:{zoom}"><div class="fam-top">{node(by_id[head_id], [head_sub], "head")}</div>'
         f'<div class="fgrid" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{cards}</div></div>' +
         note(notes_txt), title=title)

CUR[0] = "ch11"
SIBREF = {"0.4": "hakim", "0.3": "ahmad", "0.5": "abddaim", "0.8": "ali0",
          "0.6": "sisters", "0.7": "sisters", "0.9": "sisters", "0.10": "sisters"}
ov = ""
for c in children("0"):
    if c["id"] not in SIBREF: continue
    names = "، ".join(E(k["name"]) + (f' «{E(k["alias"])}»' if k["alias"] else "") for k in children(c["id"]))
    ov += chip(c, [spouse_txt(c), ("الأبناء: " + names) if names else "", f"← صفحة {pg(SIBREF[c['id']])}"], "big")
page("ch11", '<div class="chapter-head">الفصل الحادي عشر</div>' +
     f'<div style="zoom:1.12"><div class="fam-top">{node(by_id["0"], ["الجد الأكبر"], "head")}</div>'
     f'<div class="grid2">{ov}</div></div>' +
     note("هؤلاء إخوة محمد بشير وأخواته أبناء الجد الأكبر بشير، رحمهم الله. "
          "جُمعت بياناتهم من كراسة كتبها أحد أفراد العائلة بخط اليد، وراجعها عبد الهادي، وما زالت فيها أسئلة مفتوحة. "
          f"ومحمد بشير وشقيقه طمبل في الفصول السابقة، وذرية طمبل في الفصل الثامن ← صفحة {pg('ajaib')}."),
     title="إخوة محمد بشير وأخواته")

fam_page("hakim", "0.4", "ابن الجد بشير",
    {"0.4.5": lambda c: f"زوجة فضل بن محمد بشير وأم ابنه عبد الدائم ← صفحة {pg('ch3')}"}, 3, 1.15,
    "فدلم بنت حاكم زوجة عبد الله فضل، وابنها زبير تزوج عجائب بنت خاله علي. "
    "ومكة الدار زوجة سعيد بن فاطمة «أم النوراب» بنت بشير (ابن عمتها).",
    "فرع حاكم بن بشير")

fam_page("ahmad", "0.3", "ابن الجد بشير",
    {"0.3.1": lambda c: f"زوجة شريف بن محمد بشير، وأبناؤها ← صفحة {pg('sharif')}"}, 4, 1.15,
    "ليلى زوجة إبراهيم الحاج محمد شبل، وحسونة زوجة فضل أحمد، وابنها عبد الدائم مفقود.",
    "فرع أحمد بن بشير")

fam_page("abddaim", "0.5", "ابن الجد بشير · له زوجتان",
    {"0.5.1": lambda c: f"زوجتاه جارة عمر «جارة نفرين» وسعيدة الحاج · الأبناء: {ar(len(children(c['id'])))} ← صفحة {pg('abddaim2')}",
     "0.5.2": lambda c: f"زوج فاطمة ثم زينب بنتي خيري، وأبناؤه ← صفحة {pg('khairy')}",
     "0.5.7": lambda c: f"زوجة فضل بن محمد بشير وأم ابنه محمد، ثم زوجة يس علي · الأبناء: " + "، ".join(E(k["name"]) for k in children(c["id"]))},
    4, 1.0,
    "لعبد الدائم بن بشير رحمه الله زوجتان: الأولى من حامدنارتي واسمها غير معروف، أم عثمان وعلي وستنا؛ "
    "والثانية فاطمة «كلتوم»، أم علي ومحمد «بقارة» ومحمد أحمد وستنا. "
    "وفاطمة بنت عثمان أبناؤها عثمان ومحمد. ؟ اسم الزوجة الأولى، وزوج ستنا بنتها وأبناؤها.",
    "فرع عبد الدائم بن بشير", "الفصل الحادي عشر")

fam_page("abddaim2", "0.5.1", "ابن عبد الدائم بن بشير، من فاطمة «كلتوم»", {}, 4, 1.0,
    f"زوجته الأولى جارة عمر «جارة نفرين»، والثانية سعيدة الحاج. فاطمة بنته زوجة حسن بن حسين طمبل ← صفحة {pg('ajaib')}، "
    f"ومحمد زوج آمنة «آمنة الشيخ» بنت الحاج محمد ← صفحة {pg('abdoun')}، وعبد الدائم زوج سعيدة بقارة.",
    "أسرة علي بن عبد الدائم بن بشير")

fam_page("ali0", "0.8", "ابن الجد بشير", {}, 3, 1.15,
    "زوجة علي بن بشير فاطمة إدريس «كلتوم». ولابنه زبير زوجتان: جارة بخيت (؟ الاسم يحتاج تأكيداً)، وأخرى أم جارة. "
    "ونفيسة «شيرة» بنت زبير زوجة إبراهيم أبو شوك، وفاطمة بنته لها ابن اسمه بابكر. ومكة الزين بنت علي زوجة فضل فضل.",
    "فرع علي بن بشير")

CUR[0] = "sisters"
def mini2(pid, z=1.1):
    p = by_id[pid]
    rows = "".join(chip(c, [spouse_txt(c), E(c["notes"]) if c["notes"] else "",
                            kids_summary(c)]) for c in children(pid))
    return f'<div class="cell">{tree(li(node(p, []), below=stack(rows)), z)}</div>'
page("sisters", '<div class="grid2">' + mini2("0.6", 0.95) + mini2("0.7", 1.0) + mini2("0.9", 1.0) + mini2("0.10", 1.0) + '</div>' +
     note("فاطمة «أم النوراب» زوجة محمد صالح إدريس محمد أبو بكر، وابنها سعيد زوج مكة الدار بنت حاكم. "
          "آمنة «أم الدبلاب» زوجة فرح. نفرين تزوجت عمر أرقاوي ثم فنجري، وبنتها جارة من فنجري أم محمد علي إدريس، "
          f"زوج شريفة بنت دياب ← صفحة {pg('dyab')}. ودهابة زوجة نوري."),
     title="أسر فاطمة وآمنة ونفرين ودهابة بنات الجد بشير")

# الأزواج المذكورون نصاً
for pid, k in [("1.11.2", "amna"), ("1.9.2", "liba"), ("1.8.1", "dahaba"), ("1.11.3.6", "liba"),
               ("1.5.1", "ch2"), ("1.5.1.1", "monem2"), ("1.6.1.1.3", "monem1")]:
    page_of.setdefault(pid, k)

# ================= ١٤ الفهرس
CUR[0] = "index"
def short(p):
    if not p["father"] and not p["father_txt"] and p["mother"]:
        m = by_id[p["mother"]]
        return p["name"] + (" بنت " if p["gender"] == "أنثى" else " ابن ") + " ".join(full_name(m).split(" ")[:3])
    return " ".join(full_name(p).split(" ")[:5])
def key(p):
    n = p["name"]; return (n[2:] if n.startswith("ال") else n, full_name(p))
idx = sorted([p for p in people if p["id"] in page_of], key=key)
rowl = [f'<div class="ix"><span class="ixn">{E(short(p))}{" (ر)" if p["dead"] else ""}</span>'
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
<tr><td><div class="chip m dd">اسم <span class="sym">♂</span> <span class="dead">(ر)</span></div></td><td>متوفى، رحمه الله (المربع الرمادي و«ر»)</td></tr>
<tr><td class="big">★</td><td>سنة الميلاد</td></tr>
<tr><td><div class="chip u dashed">؟</div></td><td>معلومة ناقصة نرجو من يعرفها أن يخبرنا بها</td></tr>
<tr><td class="big">←</td><td>انظر صفحة أخرى في الكتاب</td></tr>
</table>"""
toc = [("الشجرة الكبرى: الجد الأكبر بشير وذريته", "root", False),
       ("الفصل الأول: فرع بشير بن محمد بشير", "ch1", False),
       ("أسرة جارة بنت بشير", "jara", True),
       ("أسرة آمنة بنت بشير", "amna", True), ("أسرة محمد بن بشير", "mhd", True),
       ("أسرة بشير بن محمد", "bashir", True), ("أسرة خضر بن محمد", "khidr", True),
       ("أسر الفاضل وعواطف وأحلام وعبد القادر", "others", True),
       ("أسرة ليبة بنت بشير", "liba", True), ("أسرة دهابة بنت بشير", "dahaba", True),
       ("أسرة علي بن بشير", "ali", True),
       ("الفصل الثاني: فرع محمد عثمان بن محمد بشير", "ch2", False),
       ("أسرة نعمات بنت محمد عثمان", "nemat", True),
       ("أسرة عبد المنعم بن محمد عثمان", "monem1", True),
       ("الفصل الثالث: فرع فضل بن محمد بشير", "ch3", False),
       ("الفصل الرابع: فرع شريف بن محمد بشير", "sharif", False),
       ("الفصل الخامس: فرع دياب بن محمد بشير", "dyab", False),
       ("أسرة حسين بن دياب", "husein", True),
       ("الفصل السادس: فرع خيري بن محمد بشير", "khairy", False),
       ("الفصل السابع: فرع عبد الله «عبدون» بن محمد بشير", "abdoun", False),
       ("أسرة عبد الله بن الحاج محمد «حانجمت»", "abdoun2", True),
       ("الفصل الثامن: فرع عجائب بنت محمد بشير وزوجها حسين بن طمبل", "ajaib", False),
       ("الفصل التاسع: فرع عثمان بن محمد بشير", "osman", False),
       ("الفصل العاشر: من فروع أخرى (بيانات جزئية)", "ch4", False),
       ("الفصل الحادي عشر: إخوة محمد بشير وأخواته", "ch11", False),
       ("فرع حاكم بن بشير", "hakim", True), ("فرع أحمد بن بشير", "ahmad", True),
       ("فرع عبد الدائم بن بشير", "abddaim", True), ("أسرة علي بن عبد الدائم", "abddaim2", True),
       ("فرع علي بن بشير", "ali0", True),
       ("أسر فاطمة وآمنة ونفرين ودهابة بنات بشير", "sisters", True),
       ("فهرس الأسماء", "index", False)]
_rows = [f'<tr><td class="{"ind" if i else ""}">{t}</td><td>{pg(k)}</td></tr>' for t, k, i in toc]
_h = (len(_rows) + 1) // 2
tr = "".join(_rows[:_h]) + '</table><table class="toc" style="flex:1">' + "".join(_rows[_h:])
page("intro", f"""
<p>هذا الكتاب محاولة لجمع ذرية الجد الأكبر <b>بشير</b>، وأكثرها من ذرية ابنه <b>محمد بشير</b>، في مكان واحد، حتى يعرف الأبناء والأحفاد أهلهم
وصلة كل واحد منهم بالآخر. ولأن العائلة كبيرة ومتشعبة، قُسّم الكتاب إلى فصول: لكل فرع من فروع العائلة فصل خاص به.</p>
<p>هذا هو <b>الإصدار الأول</b>، وفيه فروع <b>بشير</b> و<b>محمد عثمان</b> و<b>فضل</b> و<b>شريف</b> و<b>دياب</b> و<b>خيري</b> و<b>عبد الله</b> و<b>عجائب</b> و<b>عثمان</b> أبناء محمد بشير، ومعه ذرية <b>طمبل</b> شقيق محمد بشير، وما عُرف من فروع إدريس ودوشة وفدلم. وفي الفصل الحادي عشر فروع إخوة محمد بشير وأخواته: <b>حاكم</b> و<b>أحمد</b> و<b>عبد الدائم</b> و<b>علي</b>، و<b>فاطمة</b> و<b>آمنة</b> و<b>نفرين</b> و<b>دهابة</b>، جُمعت من كراسة كتبها أحد أفراد العائلة بخط اليد.
وستُضاف بقية الفروع في الإصدارات القادمة بإذن الله، إذ يصدر الكتاب مُحدَّثاً كل سنة.</p>
<h2>دليل الرموز</h2>{legend}
<h2>كيف تساهم؟</h2>
<p>إن وجدت خطأً أو اسماً ناقصاً، أو عندك بيانات فرعك، فأرسلها إلينا من صفحة «صحّح أو أضف» في موقع العائلة،
وسنضيفها في الإصدار القادم بإذن الله.</p>
<h2>محتويات الكتاب</h2><div style="display:flex;gap:16px;zoom:0.86;align-items:flex-start"><table class="toc" style="flex:1">{tr}</table></div>
""", title="مقدمة")

CSS = open("/home/claude/family/book.css").read()
body = "".join(pages[k] for k in ORDER)
open("/home/claude/family/book.html", "w").write(
    f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
    f'<title>شجرة عائلة البشيراب</title><style>{CSS}</style></head><body>{body}</body></html>')
print("pages", len(pages), "indexed", len(idx), "not shown:", missing_idx)

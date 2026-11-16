import sys
sys.path.insert(0, "/home/claude/family")
from data import people, children
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

# ترتيب شجري: كل أب قبل أبنائه
from data import by_id
order, seen = [], set()
def ready(p):
    return all(par in seen for par in (p["father"], p["mother"]) if par)
def walk(pid):
    order.append(by_id[pid]); seen.add(pid)
    for c in children(pid):
        if c["id"] not in seen and ready(c):
            walk(c["id"])
order.append(by_id["0"]); seen.add("0")
order.append(by_id["1"]); seen.add("1")
rk = children("1")
for c in [c for c in rk if c["id"] != "1.10"] + [by_id["1.10"]]:
    walk(c["id"])
for c in children("0"):          # طمبل وأحمد وحاكم، بعد ذرية محمد بشير
    if c["id"] not in seen: walk(c["id"])
assert len(order) == len(people)

wb = Workbook()
ws = wb.active
ws.title = "الأفراد"
ws.sheet_view.rightToLeft = True

hdr = ["الرقم", "الاسم", "الجنس", "رقم الأب", "رقم الأم", "اسم الأب (إن كان من خارج الشجرة)",
       "من أي زوجة", "الزوج / الزوجة", "متوفى", "سنة الميلاد", "سنة الوفاة",
       "أبناء لم تُسجَّل أسماؤهم", "ملاحظات", "الجيل (تلقائي)", "الاسم الكامل (تلقائي)"]
widths = [14, 16, 11, 14, 14, 22, 15, 30, 9, 11, 11, 30, 30, 11, 50]
F = "Arial"
thin = Side(style="thin", color="BFBFBF")
brd = Border(left=thin, right=thin, top=thin, bottom=thin)
hfill = PatternFill("solid", fgColor="1F4E5F")
autofill = PatternFill("solid", fgColor="EDEDED")
autohdr = PatternFill("solid", fgColor="5A6B70")

for c, (h, w) in enumerate(zip(hdr, widths), 1):
    cell = ws.cell(row=1, column=c, value=h)
    cell.font = Font(name=F, bold=True, color="FFFFFF", size=11)
    cell.fill = autohdr if c >= 14 else hfill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = brd
    ws.column_dimensions[cell.column_letter].width = w
ws.row_dimensions[1].height = 32

for r, p in enumerate(order, 2):
    vals = [p["id"], p["name"], p["gender"], p["father"] or None, p["mother"] or None,
            p["father_txt"] or None, p["group"] or None, p["spouse"] or None,
            "نعم" if p["dead"] else None, None, None, p["unknown"] or None, " · ".join(v for v in ([f"«{p['alias']}»"] if p.get("alias") else []) + [p["notes"]] if v) or None]
    for c, v in enumerate(vals, 1):
        cell = ws.cell(row=r, column=c, value=v)
        if c in (1, 4, 5):
            cell.number_format = "@"
    # الجيل: يبحث عن الأب أو الأم في الصفوف التي فوقه
    ws.cell(row=r, column=14, value=(
        f'=IF(D{r}<>"",INDEX($N$1:N{r-1},MATCH(D{r},$A$1:A{r-1},0))+1,'
        f'IF(E{r}<>"",INDEX($N$1:N{r-1},MATCH(E{r},$A$1:A{r-1},0))+1,1))'))
    ws.cell(row=r, column=15, value=(
        f'=IF(D{r}<>"",B{r}&" "&INDEX($O$1:O{r-1},MATCH(D{r},$A$1:A{r-1},0)),'
        f'IF(F{r}<>"",B{r}&" "&F{r},B{r}))'))
    for c in range(1, 16):
        cell = ws.cell(row=r, column=c)
        cell.font = Font(name=F, size=11, bold=(c == 2))
        cell.border = brd
        cell.alignment = Alignment(horizontal="center" if c not in (8, 12, 13, 15) else "right",
                                   vertical="center", wrap_text=(c in (8, 12, 13)))
        if c >= 14:
            cell.fill = autofill

last = len(order) + 1
dv = DataValidation(type="list", formula1='"ذكر,أنثى,غير معروف"', allow_blank=True)
ws.add_data_validation(dv)
dv.add("C2:C1000")
dv2 = DataValidation(type="list", formula1='"نعم"', allow_blank=True)
ws.add_data_validation(dv2); dv2.add("I2:I1000")
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A1:O{last}"

# ---- طريقة الإضافة
g = wb.create_sheet("طريقة الإضافة")
g.sheet_view.rightToLeft = True
g.column_dimensions["A"].width = 110
lines = [
    ("كيف تضيف شخصاً جديداً", True),
    ("1) اذهب إلى آخر صف في ورقة «الأفراد» وأضف صفاً جديداً تحت آخر شخص.", False),
    ("2) الرقم = رقم الأب أو الأم ثم نقطة ثم ترتيبه بين إخوته. مثال: أول ابن لأسامة (رقمه 1.10.1.1.1.1) يكون رقمه 1.10.1.1.1.1.1", False),
    ("3) اكتب رقم الأب في عمود «رقم الأب». إن كان الأب من خارج العائلة: اكتب رقم الأم في «رقم الأم» واسم الأب في «اسم الأب».", False),
    ("   إن كان الأب والأم كلاهما من العائلة فاكتب الرقمين معاً، ويجب أن يكون صفّا الأب والأم فوق صف الابن.", False),
    ("4) العمودان الرماديان «الجيل» و«الاسم الكامل» يُحسبان تلقائياً — انسخ الصيغة من الصف الذي فوقه ولا تكتب فيهما.", False),
    ("5) يجب أن يكون صف الأب أو الأم فوق صف الابن (وهذا يحدث تلقائياً عند الإضافة في الأسفل).", False),
    ("6) إن عرفت أن لشخص أبناء لكن لا تعرف أسماءهم، اكتب ذلك في عمود «أبناء لم تُسجَّل أسماؤهم» في صفه، مثل: بنتان وولد.", False),
    ("7) عمود «متوفى»: اختر «نعم» لمن توفي رحمه الله.", False),
    ("8) إن لم تعرف معلومة اتركها فارغة.", False),
    ("", False),
    ("الأعمدة", True),
    ("الأعمدة ذات العنوان الأزرق الداكن: تُملأ يدوياً. الأعمدة الرمادية: تلقائية.", False),
    ("«من أي زوجة»: لمن له أكثر من زوجة، مثل: الزوجة الأولى، الزوجة الثانية...", False),
    ("", False),
    ("رموز الكتاب", True),
    ("♂ ذكر    ♀ أنثى    ⚭ متزوج من    (ر) متوفى، رحمه الله    ★ سنة الميلاد    ؟ معلومة ناقصة", False),
    ("", False),
    ("الإصدارات", True),
    ("هذا الملف هو أصل البيانات. كل سنة يُحدَّث ثم يُخرج منه إصدار جديد من كتاب العائلة (PDF).", False),
    ("الإصدار الأول: نوفمبر 2026.", False),
    ("ملاحظة: الأزواج من فروع أخرى للعائلة (مثل محمد فضل وعبد الله إدريس ومحمد شريف) مسجلون في فروعهم، وترتيبهم بين إخوتهم مؤقت.", False),
]
for i, (t, b) in enumerate(lines, 1):
    c = g.cell(row=i, column=1, value=t)
    c.font = Font(name=F, size=13 if b else 11, bold=b, color="1F4E5F" if b else "000000")
    c.alignment = Alignment(horizontal="right", wrap_text=True)

wb.calculation.fullCalcOnLoad = True
out = "/home/claude/family/out/بيانات عائلة البشيراب.xlsx"
import os; os.makedirs(os.path.dirname(out), exist_ok=True)
wb.save(out)
print("saved", out, len(order))

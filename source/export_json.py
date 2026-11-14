import sys, json
sys.path.insert(0, "/home/claude/family")
from data import people, children, missing, CHANGELOG

# ملف الكتاب المنشور في جذر الموقع (اسم ثابت يُستبدل كل سنة) والاسم الذي يُحفظ به عند التنزيل
PDF = "bashirab-family-book.pdf"
PDF_NAME = "شجرة عائلة البشيراب - الإصدار الأول 2026.pdf"
# وجهة نموذج التصحيح في FormSubmit (الإيميل، أو الرمز البديل بعد التفعيل)
FORM_TO = "646148ff6d3244c29aacb496f58ddab4"

out = []
for p in people:
    q = {k: p[k] for k in ("id", "name", "gender", "father", "mother", "father_txt",
                            "group", "spouse", "notes", "dead", "unknown")}
    q["kids"] = [c["id"] for c in children(p["id"])]
    out.append(q)
data = {"people": out, "updated": CHANGELOG[0][0], "changes": CHANGELOG,
        "pdf": PDF, "pdfName": PDF_NAME, "formTo": FORM_TO}
tpl = open("/home/claude/family/site_template.html").read()
html = (tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False))
           .replace("__PDFNAME__", PDF_NAME).replace("__PDF__", PDF))
open("/home/claude/family/out/site.html", "w").write(html)
print("ok", len(out), len(html))

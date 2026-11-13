import sys, json
sys.path.insert(0, "/home/claude/family")
from data import people, children, missing

out = []
for p in people:
    q = {k: p[k] for k in ("id", "name", "gender", "father", "mother", "father_txt",
                            "group", "spouse", "notes", "dead", "unknown")}
    q["kids"] = [c["id"] for c in children(p["id"])]
    out.append(q)
data = {"people": out, "missing": missing, "updated": "١٣ نوفمبر ٢٠٢٦"}
tpl = open("/home/claude/family/site_template.html").read()
html = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False))
open("/home/claude/family/out/site.html", "w").write(html)
print("ok", len(out), len(html))

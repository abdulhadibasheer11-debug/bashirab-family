import sys, json; sys.path.insert(0, "/home/claude/family")
from data import people, children
P = {p["id"]: p for p in people}
def lineage(p, n=6):
    parts=[p["name"]]; q=p
    while q["father"] and q["father"] in P: q=P[q["father"]]; parts.append(q["name"])
    if not p["father"] and p["father_txt"]: parts.append(p["father_txt"])
    if not p["father"] and not p["father_txt"] and p["mother"] in P: return p["name"]+(" بنت " if p["gender"]=="أنثى" else " ابن ")+lineage(P[p["mother"]],n-1)
    return " ".join(parts[:n])
def label(p):
    s = p["name"] + (f" «{p['alias']}»" if p["alias"] else "") + (" (ر)" if p["dead"] else "")
    extra = []
    if p["spouse"]: extra.append(("زوجها: " if p["gender"]=="أنثى" else "زوجته: ") + p["spouse"])
    if p["notes"]: extra.append(p["notes"])
    return s + ("  —  " + "، ".join(extra) if extra else "")
def own_kids(pid):   # الأبناء يُذكرون مع الأب إن كان في الشجرة، وإلا مع الأم
    p = P[pid]
    return [k for k in children(pid) if k["father"] == pid or not (k["father"] and k["father"] in P)]
blocks = []; seen = set()
def family(pid, level):
    p = P[pid]; ks = own_kids(pid)
    if pid in seen: return
    seen.add(pid)
    if not ks and not p["unknown"]:
        other = [k for k in children(pid) if k not in ks]
        if other:
            dad = P[other[0]["father"]]
            blocks.append({"t":"h","lv":level,"x":"أسرة " + lineage(p) + (" (ر)" if p["dead"] else "")})
            blocks.append({"t":"p","x":f"أبناؤها مذكورون في أسرة زوجها {lineage(dad,4)}."})
        return
    blocks.append({"t":"h","lv":level,"x":"أسرة " + lineage(p) + (" «"+p["alias"]+"»" if p["alias"] else "") + (" (ر)" if p["dead"] else "")})
    if p["spouse"]: blocks.append({"t":"p","x":("زوجها: " if p["gender"]=="أنثى" else "زوجته: ") + p["spouse"]})
    grp = None
    for k in ks:
        if k["group"] and k["group"] != grp:
            grp = k["group"]; blocks.append({"t":"g","x":("من " + grp if not grp.startswith("الأم") else grp) + ("" if ":" in grp else ":")})
        blocks.append({"t":"k","x":label(k)})
    if p["unknown"]: blocks.append({"t":"p","x":"أبناء لم تُسجَّل أسماؤهم: " + p["unknown"] + "  ........"})
    for k in ks: family(k["id"], 1 if k["id"] == "1" else min(level+1, 3))
family("0", 1)
left = [p for p in people if p["id"] not in seen and children(p["id"])]
print("families", sum(b["t"]=="h" for b in blocks), "kids", sum(b["t"]=="k" for b in blocks), "unvisited-with-kids", [p["id"] for p in left][:20])
json.dump(blocks, open("/home/claude/word/blocks.json","w"), ensure_ascii=False)

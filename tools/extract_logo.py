"""One-off tool: splits the animated logo HTML (layers + CSS keyframes) into PNG files + logo_anim.json."""
import base64, json, re, sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
html = src.read_text(encoding="utf-8", errors="replace")
css = html[html.index("<style>"):html.index("</style>")]

def pct(v):
    return float(v.rstrip("%")) / 100.0

layers = {}
for m in re.finditer(r"\.([a-z0-9-]+)\s*\{([^}]*)\}", css):
    name, body = m.group(1), m.group(2)
    props = dict(p.strip().split(":", 1) for p in body.split(";") if ":" in p)
    if "left" in props and "width" in props:
        o = props.get("transform-origin", "50% 50%").split()
        anim = props.get("animation", "").strip()
        layers[name] = {"box": [pct(props["left"]), pct(props["top"]), pct(props["width"]), pct(props["height"])],
                        "origin": [pct(o[0]), pct(o[1])], "anim": anim}
kf = {}
for m in re.finditer(r"@keyframes\s+([a-z0-9-]+)\s*\{(.*?)\}\s*(?=@|\s*$|\n)", css, re.S):
    pass
for m in re.finditer(r"@keyframes ([a-z0-9-]+) \{ (.*) \}\n", css + "\n"):
    name, body = m.group(1), m.group(2)
    frames = []
    for fm in re.finditer(r"([0-9.%, ]+)\{ transform: ([^}]*?); \}", body):
        times = [float(t.strip().rstrip("%")) / 100.0 for t in fm.group(1).split(",") if t.strip()]
        tr = fm.group(2)
        rot = re.search(r"rotate\(([-0-9.]+)(?:deg)?\)", tr)
        sc = re.search(r"scale\(([-0-9.]+)\)", tr)
        scy = re.search(r"scaleY\(([-0-9.]+)\)", tr)
        for t in times:
            frames.append([t, float(rot.group(1)) if rot else 0.0, float(sc.group(1)) if sc else 1.0,
                           float(scy.group(1)) if scy else 1.0])
    frames.sort()
    kf[name] = frames
imgs = re.findall(r'<img class="([^"]+)" src="data:image/png;base64,([A-Za-z0-9+/=]+)"', html)
order = []
for i, (cls, b64) in enumerate(imgs):
    classes = cls.split()
    key = "base" if "base" in classes else classes[1]
    (out / f"{key}.png").write_bytes(base64.b64decode(b64))
    entry = {"name": key}
    if key != "base":
        lay = layers[key]
        a = lay["anim"]
        if not a and "eyelid" in classes:
            a = layers.get("eyelid", {}).get("anim", "") or "blink 4.5s infinite"
        entry.update(box=lay["box"], origin=lay["origin"])
        am = re.match(r"([a-z0-9-]+)\s+([0-9.]+)s\s+ease-in-out(?:\s+(\.?[0-9.]+)s)?\s+infinite", a) if a else None
        if "eyelid" in classes:
            am = re.match(r"([a-z0-9-]+)\s+([0-9.]+)s(?:\s+(\.?[0-9.]+)s)?", "blink 4.5s infinite")
        if am:
            entry["kf"], entry["dur"], entry["delay"] = am.group(1), float(am.group(2)), float(am.group(3) or 0)
    order.append(entry)
from PIL import Image
w, h = Image.open(out / "base.png").size
json.dump({"size": [w, h], "layers": order, "keyframes": kf}, open(out / "logo_anim.json", "w"), indent=1)
print(w, h, len(order), {k: len(v) for k, v in kf.items()})
print([ (e["name"], e.get("kf"), e.get("dur"), e.get("delay")) for e in order][:6])

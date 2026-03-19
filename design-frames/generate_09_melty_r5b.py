#!/usr/bin/env python3
"""
DESIGN FRAMES 09: MELTY R5b
KV（テキストなし）→ Pillow overlay
配置バグ修正 + Zen Maru Gothic フォント使用
"""
import requests, json, time, os, base64, sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    import subprocess
    result = subprocess.run(["bash", "-c", "source ~/.zshrc && echo $GOOGLE_API_KEY"], capture_output=True, text=True)
    API_KEY = result.stdout.strip()

if not API_KEY:
    print("GOOGLE_API_KEY not found"); sys.exit(1)

BASE_DIR = Path(__file__).parent
OUT = BASE_DIR / "banners_09_melty_r5b"
OUT.mkdir(exist_ok=True)

# Fonts
FONT_ZEN_MARU_BOLD = os.path.expanduser("~/Library/Fonts/ZenMaruGothic-Bold.ttf")
FONT_ZEN_MARU_MED = os.path.expanduser("~/Library/Fonts/ZenMaruGothic-Medium.ttf")
FONT_ZEN_MARU_REG = os.path.expanduser("~/Library/Fonts/ZenMaruGothic-Regular.ttf")
FONT_ZEN_KAKU_BOLD = os.path.expanduser("~/Library/Fonts/ZenKakuGothicNew-Bold.ttf")
FONT_MPLUS_BOLD = os.path.expanduser("~/Library/Fonts/MPLUSRounded1c-Bold.ttf")
FONT_MPLUS_XBOLD = os.path.expanduser("~/Library/Fonts/MPLUSRounded1c-ExtraBold.ttf")
IMG_SIZE = 1080


def generate_kv(prompt, filename, retries=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    for attempt in range(retries + 1):
        try:
            print(f"  KV gen: {filename} (attempt {attempt+1})")
            r = requests.post(url, json=payload, timeout=180)
            if r.status_code in (429, 503):
                time.sleep(25 * (attempt + 1)); continue
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}")
                if attempt < retries: time.sleep(15); continue
                return None
            data = r.json()
            for c in data.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    if "inlineData" in p:
                        img = base64.b64decode(p["inlineData"]["data"])
                        out_path = OUT / filename
                        with open(out_path, "wb") as f:
                            f.write(img)
                        print(f"  KV: {filename} ({len(img)/1024:.0f}KB)")
                        return str(out_path)
            if attempt < retries: time.sleep(10); continue
            return None
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries: time.sleep(15); continue
            return None
    return None


def overlay_text(kv_path, output_path, elements):
    """テキストオーバーレイ — 座標は画像サイズ比率で指定"""
    img = Image.open(kv_path).convert("RGBA")
    w, h = img.size

    txt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    for el in elements:
        text = el["text"]
        font_path = el.get("font", FONT_ZEN_MARU_BOLD)
        size = int(el.get("size", 48) * w / IMG_SIZE)  # Scale to actual image size

        try:
            font = ImageFont.truetype(font_path, size)
        except:
            font = ImageFont.truetype(FONT_ZEN_MARU_BOLD, size)

        # Position: ratios (0.0-1.0) of image dimensions
        px = el.get("x", 0.5)
        py = el.get("y", 0.5)
        x = int(px * w)
        y = int(py * h)
        anchor = el.get("anchor", "mm")
        color = el.get("color", (90, 62, 54, 255))

        # Shadow
        shadow = el.get("shadow", None)
        if shadow:
            sx = int(shadow.get("dx", 2) * w / IMG_SIZE)
            sy = int(shadow.get("dy", 2) * w / IMG_SIZE)
            sc = shadow.get("color", (0, 0, 0, 50))
            draw.text((x + sx, y + sy), text, font=font, fill=sc, anchor=anchor)

        # Stroke (outline)
        stroke_w = el.get("stroke_width", 0)
        stroke_c = el.get("stroke_color", (255, 255, 255, 200))

        if stroke_w > 0:
            draw.text((x, y), text, font=font, fill=color, anchor=anchor,
                      stroke_width=int(stroke_w * w / IMG_SIZE), stroke_fill=stroke_c)
        else:
            draw.text((x, y), text, font=font, fill=color, anchor=anchor)

    result = Image.alpha_composite(img, txt_layer)
    result = result.convert("RGB")
    result.save(output_path, quality=95)
    print(f"  Final: {Path(output_path).name}")
    return str(output_path)


# ============================================================
# KV（テキストなし）
# ============================================================

NO_TEXT = """
ABSOLUTELY NO TEXT IN THE IMAGE.
No letters, no words, no brand name, no watermarks, no captions, no logos.
The image must be purely visual — completely clean canvas.
"""

PALETTE = "Colors: Warm pink, peach, cream, gold accents. Mood: Dreamy, warm, feminine, sophisticated."

KVPS = [
    # A1 - Flat Lay
    {"kv": "kv_A1.png", "final": "melty_A1_flatlay.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nBird's eye flat lay of artisan sweets on white marble. Pastel macarons (pink, lavender, mint), chocolate bonbons with gold leaf, strawberry tart, raspberries. Rose petals, gold flakes. CENTER is clear (open space). Edges abundant. Warm dreamy overhead lighting. Professional food photography.\n{NO_TEXT}",
     "text": [
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 30, "x": 0.85, "y": 0.08, "anchor": "mt", "color": (160, 100, 80, 230)},
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 52, "x": 0.5, "y": 0.42, "anchor": "mm", "color": (75, 50, 40, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (255, 255, 255, 140)}},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 52, "x": 0.5, "y": 0.55, "anchor": "mm", "color": (230, 100, 120, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (255, 255, 255, 140)}},
     ]},

    # A2 - Chocolate
    {"kv": "kv_A2.png", "final": "melty_A2_chocolate.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nExtreme close-up of glossy melted chocolate poured over cream puffs/profiteroles. Rich viscous chocolate catching warm light. Steam visible. Warm pink/gold bokeh background. Bottom 35% is dark chocolate pool area. Professional food photography.\n{NO_TEXT}",
     "text": [
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 28, "x": 0.12, "y": 0.06, "anchor": "lt", "color": (255, 210, 170, 255)},
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 48, "x": 0.5, "y": 0.78, "anchor": "mm", "color": (255, 245, 235, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (30, 15, 5, 100)}},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 48, "x": 0.5, "y": 0.88, "anchor": "mm", "color": (255, 200, 170, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (30, 15, 5, 100)}},
     ]},

    # B1 - Macaron Cascade
    {"kv": "kv_B1.png", "final": "melty_B1_macaron.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nMacarons cascading diagonally from lower-left to upper-right. Pastel colors: pink, peach, lavender, mint. Some split showing ganache. Gold leaf, sugar crystals. Soft pink gradient background. Upper-left area CLEAR for text. Dynamic diagonal energy.\n{NO_TEXT}",
     "text": [
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 26, "x": 0.08, "y": 0.08, "anchor": "lt", "color": (170, 105, 85, 230)},
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 46, "x": 0.35, "y": 0.22, "anchor": "mm", "color": (75, 50, 40, 255),
          "shadow": {"dx": 1, "dy": 1, "color": (255, 235, 225, 180)}},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 42, "x": 0.38, "y": 0.32, "anchor": "mm", "color": (230, 100, 120, 255),
          "shadow": {"dx": 1, "dy": 1, "color": (255, 235, 225, 180)}},
     ]},

    # B2 - Gift Box
    {"kv": "kv_B2.png", "final": "melty_B2_giftbox.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nOverhead: feminine hands with pink nails opening a pink gift box. Half-open, revealing artisan chocolates and petit fours inside. Tissue paper, satin ribbon. Rose petals on cream table. Warm afternoon light. Bottom 25% is clean cream surface.\n{NO_TEXT}",
     "text": [
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 26, "x": 0.5, "y": 0.06, "anchor": "mt", "color": (180, 115, 95, 220)},
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 46, "x": 0.5, "y": 0.82, "anchor": "mm", "color": (75, 50, 40, 255),
          "shadow": {"dx": 1, "dy": 1, "color": (255, 245, 235, 160)}},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 46, "x": 0.5, "y": 0.92, "anchor": "mm", "color": (230, 100, 120, 255),
          "shadow": {"dx": 1, "dy": 1, "color": (255, 245, 235, 160)}},
     ]},

    # C1 - Woman
    {"kv": "kv_C1.png", "final": "melty_C1_woman.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nClose-up portrait of beautiful Japanese woman (mid-20s) holding pink macaron near lips. About to bite, eyes half-closed, gentle smile. Soft warm lighting, creamy bokeh. Cream knit sweater, pink nails. PHOTOREALISTIC beauty ad. Lower 30% has softer/lighter area.\n{NO_TEXT}",
     "text": [
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 32, "x": 0.5, "y": 0.07, "anchor": "mt", "color": (150, 90, 75, 240)},
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 48, "x": 0.5, "y": 0.80, "anchor": "mm", "color": (75, 50, 40, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (255, 255, 255, 160)}},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 48, "x": 0.5, "y": 0.91, "anchor": "mm", "color": (230, 100, 120, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (255, 255, 255, 160)}},
     ]},

    # C2 - Cozy
    {"kv": "kv_C2.png", "final": "melty_C2_cozy.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nDreamy kitchen bathed in golden hour. Woman's hands piping cream on tart. Flour on marble. Strawberries in ceramic bowl, steaming tea. Pink box with sweets open. Fairy lights bokeh. Warm golden glow. Upper 30% has soft bokeh area.\n{NO_TEXT}",
     "text": [
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 44, "x": 0.5, "y": 0.10, "anchor": "mm", "color": (255, 248, 240, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (50, 30, 20, 120)},
          "stroke_width": 1, "stroke_color": (255, 255, 255, 60)},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 44, "x": 0.5, "y": 0.20, "anchor": "mm", "color": (255, 220, 200, 255),
          "shadow": {"dx": 2, "dy": 2, "color": (50, 30, 20, 120)}},
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 22, "x": 0.92, "y": 0.95, "anchor": "rb", "color": (255, 230, 210, 180)},
     ]},

    # D1 - Minimal
    {"kv": "kv_D1.png", "final": "melty_D1_minimal.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nSingle perfect pink macaron on clean soft pink surface. Fashion editorial lighting — soft but dramatic. Macaron in LOWER-RIGHT quadrant (small). MASSIVE empty space upper-left and center. Incredible detail: shell, feet, cream. Few crumbs, gold leaf. Magazine-worthy minimalism.\n{NO_TEXT}",
     "text": [
         {"text": "がんばった日は、", "font": FONT_MPLUS_XBOLD, "size": 62, "x": 0.5, "y": 0.25, "anchor": "mm", "color": (70, 48, 38, 255)},
         {"text": "もうひとつ", "font": FONT_MPLUS_XBOLD, "size": 62, "x": 0.34, "y": 0.40, "anchor": "mm", "color": (230, 100, 120, 255)},
         {"text": "食べていい。", "font": FONT_MPLUS_XBOLD, "size": 62, "x": 0.72, "y": 0.40, "anchor": "mm", "color": (70, 48, 38, 255)},
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 24, "x": 0.92, "y": 0.93, "anchor": "rb", "color": (150, 100, 85, 200)},
     ]},

    # D2 - Strawberry
    {"kv": "kv_D2.png", "final": "melty_D2_strawberry.png",
     "prompt": f"Create a stunning 1080x1080 photograph. {PALETTE}\nSpectacular strawberry tart assembly — fresh strawberry placed on whipped cream on golden pastry. Powdered sugar in air catching warm light. Berries scattered. Peach/pink bokeh. Sharp food photography. Top 30% is soft bokeh for text.\n{NO_TEXT}",
     "text": [
         {"text": "MELTY", "font": FONT_ZEN_KAKU_BOLD, "size": 30, "x": 0.5, "y": 0.06, "anchor": "mt", "color": (170, 100, 80, 240)},
         {"text": "がんばった日は、", "font": FONT_ZEN_MARU_BOLD, "size": 48, "x": 0.5, "y": 0.15, "anchor": "mm", "color": (75, 50, 40, 255),
          "shadow": {"dx": 1, "dy": 1, "color": (255, 240, 230, 150)}},
         {"text": "もうひとつ食べていい。", "font": FONT_ZEN_MARU_BOLD, "size": 48, "x": 0.5, "y": 0.26, "anchor": "mm", "color": (230, 100, 120, 255),
          "shadow": {"dx": 1, "dy": 1, "color": (255, 240, 230, 150)}},
     ]},
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    concepts = {
        "A1": ("Luxurious Flat Lay", "マカロン×チョコ×花びら。宝箱。"),
        "A2": ("Liquid Chocolate", "とろけるチョコの至福。"),
        "B1": ("Macaron Cascade", "マカロンの虹が流れる。"),
        "B2": ("The Unboxing", "ご褒美を開ける瞬間。"),
        "C1": ("Bliss Portrait", "至福の一口前。"),
        "C2": ("Golden Hour", "日曜午後のゴールデンアワー。"),
        "D1": ("Minimal Editorial", "1個のマカロン。テキスト主役。"),
        "D2": ("Strawberry Fantasy", "いちごタルト完成の瞬間。"),
    }
    cards = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]
            cn, cd = concepts.get(key, (fname, ""))
            cards += f"""
            <div class="card">
                <div class="img-wrap"><img src="banners_09_melty_r5b/{fname}" onclick="openZoom(this.src)"></div>
                <div class="info"><span class="label">{key}</span><span class="title">{cn}</span><span class="desc">{cd}</span></div>
            </div>"""
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<title>MELTY R5b</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;700&family=Noto+Sans+JP:wght@300;400;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#fffaf5;color:#5a3e36;font-family:'Noto Sans JP',sans-serif;}}
.hero{{padding:60px 40px;text-align:center;}}
.hero h1{{font-family:'Zen Maru Gothic';font-size:52px;font-weight:700;color:#ff8a9e;letter-spacing:8px;}}
.hero p{{font-size:17px;margin-top:14px;font-weight:300;}}
.hero .meta{{display:flex;justify-content:center;gap:14px;margin-top:14px;}}
.hero .badge{{font-size:10px;padding:4px 14px;border-radius:20px;border:1px solid #ff8a9e44;color:#ff8a9e;letter-spacing:2px;}}
.grid{{max-width:1200px;margin:0 auto;padding:20px 24px 60px;display:grid;grid-template-columns:repeat(2,1fr);gap:24px;}}
.card{{background:#fff;border-radius:16px;overflow:hidden;border:1px solid #fce4ec;transition:all .2s;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 8px 30px rgba(255,138,158,.15);}}
.img-wrap{{aspect-ratio:1;overflow:hidden;background:#fff0e8;}}
.img-wrap img{{width:100%;height:100%;object-fit:cover;cursor:zoom-in;}}
.info{{padding:14px 18px;display:flex;flex-direction:column;gap:2px;}}
.label{{font-size:11px;color:#ff8a9e;letter-spacing:4px;font-weight:700;}}
.title{{font-size:13px;color:#5a3e36;}}
.desc{{font-size:10px;color:#b08878;}}
.zo{{display:none;position:fixed;inset:0;background:rgba(90,62,54,.92);z-index:1000;cursor:zoom-out;justify-content:center;align-items:center;}}
.zo.on{{display:flex;}}.zo img{{max-width:90%;max-height:90%;border-radius:12px;}}
.ft{{text-align:center;padding:30px;font-size:9px;letter-spacing:4px;color:#d4a090;}}
@media(max-width:768px){{.grid{{grid-template-columns:1fr;}}}}
</style></head><body>
<div class="hero"><h1>MELTY</h1><p>「がんばった日は、もうひとつ食べていい。」</p>
<div class="meta"><span class="badge">R5b</span><span class="badge">Zen Maru Gothic</span><span class="badge">KV + Pillow</span></div></div>
<div class="grid">{cards}</div>
<div class="zo" id="zo" onclick="this.classList.remove('on')"><img id="zi"></div>
<div class="ft">DESIGN FRAMES 09 MELTY R5b — {timestamp}</div>
<script>function openZoom(s){{document.getElementById('zi').src=s;document.getElementById('zo').classList.add('on');}}</script>
</body></html>"""
    p = BASE_DIR / "gallery_09_melty_r5b.html"
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return str(p)


if __name__ == "__main__":
    print("=" * 60)
    print("MELTY R5b — KV + Pillow (Zen Maru Gothic)")
    print("=" * 60)
    results = []
    for i, item in enumerate(KVPS):
        print(f"\n[{i+1}/{len(KVPS)}] {item['final']}")
        kv = generate_kv(item["prompt"], item["kv"])
        if not kv:
            results.append((item["final"], None))
            time.sleep(15); continue
        time.sleep(2)
        try:
            final = str(OUT / item["final"])
            overlay_text(kv, final, item["text"])
            results.append((item["final"], final))
        except Exception as e:
            print(f"  Overlay error: {e}")
            import traceback; traceback.print_exc()
            results.append((item["final"], None))
        time.sleep(8)

    print("\n" + "=" * 60)
    ok = sum(1 for _, p in results if p)
    for f, p in results:
        print(f"  [{'OK' if p else 'FAIL'}] {f}")
    print(f"\n{ok}/{len(results)}")
    if ok > 0:
        g = create_gallery(results)
        print(f"Gallery: {g}")
    print("=" * 60)

#!/usr/bin/env python3
"""
DESIGN FRAMES 09: MELTY R3
デザイン図鑑参照 + ナノバナナ式テキスト指示（階層・メリハリ・アウトライン）
"""
import requests, json, time, os, base64, sys
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    import subprocess
    result = subprocess.run(["bash", "-c", "source ~/.zshrc && echo $GOOGLE_API_KEY"], capture_output=True, text=True)
    API_KEY = result.stdout.strip()

if not API_KEY:
    print("GOOGLE_API_KEY not found"); sys.exit(1)

BASE_DIR = Path(__file__).parent
OUT = BASE_DIR / "banners_09_melty_r3"
OUT.mkdir(exist_ok=True)

# デザイン図鑑参照: テキスト品質が高いシャンプー広告
REF_IMAGE = "/Users/ayakakurogi/.claude/knowledge/design-refs/002a-beauty-shampoo.jpg"
# エディトリアルなデザイン参照
REF_EDITORIAL = "/Users/ayakakurogi/.claude/knowledge/design-refs/009a-editorial-marbling-makeup.jpg"


def load_image(path):
    path = Path(path)
    if not path.exists():
        print(f"  Not found: {path}")
        return None
    with open(path, "rb") as f:
        data = f.read()
    ext = path.suffix.lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}}


def generate_image(prompt, ref_images, filename, retries=3):
    parts = []
    for ref_path, instruction in ref_images:
        ref_data = load_image(ref_path)
        if ref_data:
            parts.append(ref_data)
            parts.append({"text": instruction})
    parts.append({"text": prompt})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    for attempt in range(retries + 1):
        try:
            print(f"  Generating: {filename} (attempt {attempt+1}/{retries+1})")
            r = requests.post(url, json=payload, timeout=180)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait); continue
            if r.status_code == 503:
                wait = 20 * (attempt + 1)
                print(f"  503, waiting {wait}s...")
                time.sleep(wait); continue
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}: {r.text[:300]}")
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
                        print(f"  Done: {out_path.name} ({len(img)/1024:.0f}KB)")
                        return str(out_path)
            print("  No image in response")
            if attempt < retries: time.sleep(10); continue
            return None
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries: time.sleep(15); continue
            return None
    return None


# ============================================================
# 参照画像指示
# ============================================================
REF_SHAMPOO_INSTRUCTION = """[DESIGN QUALITY REFERENCE]
Look at this Japanese beauty advertisement. Notice:
1. The Japanese text is PERFECTLY rendered — crisp, clean, professional
2. Text has HIERARCHY — large bold headline, medium sub-headline, small body
3. Text SIZE VARIATION creates visual rhythm and energy
4. The layout feels like a REAL professional Japanese Instagram ad
5. Warm pink/golden color scheme with feminine appeal

YOUR image should match this LEVEL OF QUALITY for Japanese text rendering.
YOUR image will be a SWEETS/PATISSERIE brand, not shampoo.
But learn from: text quality, layout sophistication, and professional polish.
"""

REF_EDITORIAL_INSTRUCTION = """[EDITORIAL DESIGN REFERENCE]
Look at this editorial layout design. Notice:
1. Bold, confident composition — DYNAMIC, not boring
2. Strong visual impact — makes you want to look closer
3. Grid-breaking creative layout
4. Multiple visual elements arranged with intention

YOUR image should have this level of VISUAL IMPACT and EXCITEMENT.
NOT this color scheme (yours is warm pink/peach). NOT this subject matter.
But learn from: the ENERGY, the CONFIDENCE, the IMPACT.
"""

# ============================================================
# ナノバナナ式テキスト指示
# ============================================================
TEXT_NANO_STYLE = """
TYPOGRAPHY (CRITICAL — must be PERFECTLY rendered, professional Japanese ad quality):

Main Copy — 2 lines, treated as HERO DESIGN ELEMENT:
  Line 1: 「がんばった日は、」
    - 「がんばった」= LARGEST text, warm brown, BOLD weight
    - 「日は、」= same size, slightly different shade for rhythm

  Line 2: 「もうひとつ食べていい。」
    - 「もうひとつ」= large, warm pink or coral accent color — this is the EMOTIONAL CORE
    - 「食べていい。」= same size as ひとつ, back to warm brown

  KEY WORD: もうひとつ (mo-u-hi-to-tsu = "one more")
  This word MUST be perfect. ひ then と then つ. NOT わっと. NOT わつ.

Brand: MELTY — elegant, smaller, positioned as logo element
  - Soft serif or elegant sans-serif
  - Pink or warm gold

TEXT STYLING:
- Font: Rounded gothic (soft sans-serif) for main copy — cute but professional
- Text has subtle warm shadow for depth (NOT harsh drop shadow)
- Dynamic SIZE VARIATION between lines — creates rhythm and energy
- Text feels like part of the design, NOT stamped on top
- Professional Japanese web advertisement quality

ONLY these 2 text elements. NO other text. NO watermarks. NO buttons.
"""

# ============================================================
# 8 Patterns — ワクワクするビジュアルに進化
# ============================================================

BRAND = """
BRAND: MELTY — Monthly reward sweets subscription for working women
Palette: #ff8a9e (warm pink), #ffc8a0 (peach), #fff0e8 (cream), #5a3e36 (warm brown), gold accents
Mood: Warm, rewarding, indulgent, dreamy but EXCITING. Like opening a gift.
Quality: Professional Japanese Instagram advertisement. Not amateur. POLISHED.
"""

P_A1 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — EXPLODING FLAT LAY:
Not a boring flat lay. An EXCITING one.
Bird's eye view but with MOVEMENT — macarons and petals seem to be floating/falling.
Pastel macarons (pink, lavender, mint, peach) scattered dynamically across marble.
Chocolate bonbons, strawberry slices, gold leaf FLOATING in the composition.
Rose petals caught mid-air. Powdered sugar dust catching light.
Warm, dreamy lighting. Pink/peach color grading.
Center has breathing room for text — but the edges are ABUNDANT with sweets.

The feeling: a treasure chest of sweets just burst open.

{TEXT_NANO_STYLE}

Text placement: Center of image. がんばった日は、on top line. もうひとつ食べていい。below.
MELTY at very top, small and elegant.
"""

P_A2 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — LIQUID CHOCOLATE POUR:
Extreme close-up of GLOSSY melted chocolate being poured.
The chocolate is like liquid gold — viscous, shiny, catching warm light.
Below: cream puffs or profiteroles drowning in chocolate.
Steam rises. Everything GLISTENS.
Background: warm bokeh in pinks and golds.
Lower 40% is dark chocolate = perfect text contrast area.

The feeling: pure indulgence. The moment before the first bite.

{TEXT_NANO_STYLE}

Text placement: Bottom area over dark chocolate. White/cream text with warm glow.
MELTY top-left in warm gold.
"""

P_B1 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — MACARON RAINBOW CASCADE:
Macarons cascading diagonally across the frame like a waterfall.
Each row a different pastel color: pink → peach → lavender → mint → cream.
Some macarons are split open showing colorful ganache filling.
Gold leaf and sugar crystals sparkling.
Soft pink gradient background.
The composition has ENERGY — diagonal flow, not static.

The feeling: abundance, joy, celebration of small luxuries.

{TEXT_NANO_STYLE}

Text placement: Upper-right area (macarons cascade from upper-left to lower-right, leaving space).
Dark brown text. MELTY top-left, small.
"""

P_B2 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — THE UNBOXING MOMENT:
Overhead shot: hands with pretty nails opening a pink subscription box.
The box lid is half-open, revealing perfectly arranged artisan sweets inside.
Tissue paper, a gold MELTY card, ribbon.
Rose petals on the table surface. Warm afternoon light.
The hands express ANTICIPATION — fingers just lifting the lid.

The feeling: the ritual of treating yourself. Self-love in a box.

{TEXT_NANO_STYLE}

Text placement: Below the box. Warm brown on cream background.
MELTY visible on the gold card inside the box AND small at top.
"""

P_C1 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — BLISS PORTRAIT:
Close-up portrait of a beautiful Japanese woman (mid-20s).
She's holding a pink macaron near her lips, about to take a bite.
Expression: eyes half-closed in anticipation, gentle smile. REAL emotion.
Soft warm lighting wrapping around her face. Creamy bokeh.
She wears a cream/beige knit. Her nails are pastel pink.
PHOTOREALISTIC — like a professional beauty advertisement.
Warm pink color grading over the whole image.

The feeling: that moment when you finally sit down after a long day.

{TEXT_NANO_STYLE}

Text placement: Lower third. Large, confident.
MELTY above her head, elegant.
"""

P_C2 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — GOLDEN HOUR KITCHEN:
A dreamy kitchen scene bathed in golden hour light.
A woman's hands piping cream onto a small tart. Flour dusted on the counter.
Fresh strawberries in a bowl. A cup of tea steaming nearby.
The MELTY subscription box is open on the counter with sweets inside.
Fairy lights strung in the background. WARM WARM WARM.
Everything has a golden glow. Shot with shallow depth of field.

The feeling: Sunday afternoon. No rush. Pure joy in the process.

{TEXT_NANO_STYLE}

Text placement: Overlaid on the dreamy bokeh area. Cream/white text.
MELTY small, lower-right corner.
"""

P_D1 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — ONE PERFECT MACARON (EDITORIAL):
A SINGLE perfect pink macaron on a minimalist pink surface.
But shot like a FASHION editorial — dramatic lighting, one strong shadow.
The macaron's texture is incredibly detailed — you can see the delicate shell, the feet, the cream filling.
Massive negative space — the macaron is small in frame, the text is the STAR.
A few artful crumbs. Maybe one gold leaf flake.
Clean, sophisticated, MAGAZINE-WORTHY.

The feeling: less is more. One perfect bite is all you need.

{TEXT_NANO_STYLE}

Text placement: LARGE — fills the negative space. Text IS the design.
がんばった日は、= huge, top area
もうひとつ食べていい。= huge, middle area
MELTY = small, bottom-right corner.
Dark charcoal or warm brown text.
"""

P_D2 = f"""Create a stunning 1080x1080 pixel square sweets advertisement.

{BRAND}

VISUAL CONCEPT — STRAWBERRY FANTASY:
A spectacular strawberry dessert — mille-feuille or tart — being assembled.
A fresh strawberry is being placed on top, FROZEN mid-action.
Whipped cream, golden pastry layers, powdered sugar floating in air.
More strawberries and berries scattered around.
Background: soft peach/pink bokeh with warm light.
Everything is SHARP and DELICIOUS — food photography at its best.

The feeling: the moment a masterpiece is completed.

{TEXT_NANO_STYLE}

Text placement: Top area, over the soft bokeh.
Dark text on light background. Bold, confident.
MELTY elegantly placed near the text.
"""

banners = [
    {"prompt": P_A1, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION), (REF_EDITORIAL, REF_EDITORIAL_INSTRUCTION)], "filename": "melty_A1_flatlay.png"},
    {"prompt": P_A2, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION)], "filename": "melty_A2_chocolate.png"},
    {"prompt": P_B1, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION), (REF_EDITORIAL, REF_EDITORIAL_INSTRUCTION)], "filename": "melty_B1_macaron.png"},
    {"prompt": P_B2, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION)], "filename": "melty_B2_giftbox.png"},
    {"prompt": P_C1, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION)], "filename": "melty_C1_woman.png"},
    {"prompt": P_C2, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION)], "filename": "melty_C2_cozy.png"},
    {"prompt": P_D1, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION), (REF_EDITORIAL, REF_EDITORIAL_INSTRUCTION)], "filename": "melty_D1_minimal.png"},
    {"prompt": P_D2, "refs": [(REF_IMAGE, REF_SHAMPOO_INSTRUCTION)], "filename": "melty_D2_strawberry.png"},
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    concepts = {
        "A1": ("Exploding Flat Lay", "弾けるフラットレイ。マカロンが浮遊する瞬間。"),
        "A2": ("Liquid Chocolate", "とろけるチョコの至福。極限のインダルジェンス。"),
        "B1": ("Macaron Cascade", "マカロンの虹が流れ落ちる。ダイナミック。"),
        "B2": ("The Unboxing", "サブスクBOXを開ける儀式。セルフラブ。"),
        "C1": ("Bliss Portrait", "一口前の至福。ビューティー広告級。"),
        "C2": ("Golden Hour Kitchen", "日曜午後のキッチン。ゴールデンアワー。"),
        "D1": ("One Perfect Macaron", "1個のマカロン×エディトリアル。テキスト主役。"),
        "D2": ("Strawberry Fantasy", "いちごの傑作が完成する瞬間。"),
    }
    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]
            cn, cd = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_09_melty_r3/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{cn}</div>
                    <div class="card-desc">{cd}</div>
                </div>
            </div>"""
    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>MELTY R3</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#fffaf5;color:#5a3e36;font-family:'Noto Sans JP',sans-serif;font-weight:300;}}
.hero{{padding:60px 40px 40px;text-align:center;}}
.hero h1{{font-size:48px;font-weight:700;letter-spacing:8px;color:#ff8a9e;}}
.hero p{{font-size:16px;color:#5a3e36;margin-top:16px;}}
.hero .meta{{display:flex;justify-content:center;gap:16px;margin-top:16px;font-size:10px;letter-spacing:2px;}}
.hero .badge{{padding:4px 12px;border-radius:20px;border:1px solid #ff8a9e44;color:#ff8a9e;}}
.grid{{max-width:1200px;margin:0 auto;padding:24px;display:grid;grid-template-columns:repeat(2,1fr);gap:24px;}}
.card{{background:#fff;border-radius:16px;overflow:hidden;border:1px solid #fce4ec;transition:transform 0.2s,box-shadow 0.2s;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 8px 32px rgba(255,138,158,0.15);}}
.card-img-wrap{{aspect-ratio:1;overflow:hidden;background:#fff0e8;}}
.card-img-wrap img{{width:100%;height:100%;object-fit:cover;cursor:zoom-in;}}
.card-info{{padding:16px 20px;}}
.card-label{{font-size:12px;color:#ff8a9e;letter-spacing:4px;font-weight:700;}}
.card-title{{font-size:14px;color:#5a3e36;margin-top:4px;}}
.card-desc{{font-size:11px;color:#b08878;margin-top:4px;}}
.zoom-overlay{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(90,62,54,0.9);z-index:1000;cursor:zoom-out;justify-content:center;align-items:center;}}
.zoom-overlay.active{{display:flex;}}
.zoom-overlay img{{max-width:90%;max-height:90%;border-radius:12px;}}
.footer{{text-align:center;padding:32px;font-size:9px;letter-spacing:4px;color:#d4a090;}}
@media(max-width:768px){{.grid{{grid-template-columns:1fr;}}}}
</style></head><body>
<div class="hero">
  <h1>MELTY</h1>
  <p>「がんばった日は、もうひとつ食べていい。」</p>
  <div class="meta"><span class="badge">R3</span><span class="badge">デザイン図鑑参照</span><span class="badge">ナノバナナ式テキスト</span></div>
</div>
<div class="grid">{cards_html}</div>
<div class="zoom-overlay" id="zo" onclick="closeZoom()"><img id="zi" src=""></div>
<div class="footer">DESIGN FRAMES 09 MELTY R3 — {timestamp}</div>
<script>
function openZoom(s){{document.getElementById('zi').src=s;document.getElementById('zo').classList.add('active');}}
function closeZoom(){{document.getElementById('zo').classList.remove('active');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeZoom();}});
</script></body></html>"""
    p = BASE_DIR / "gallery_09_melty_r3.html"
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return str(p)


if __name__ == "__main__":
    print("=" * 60)
    print("MELTY R3 — デザイン図鑑参照 + ナノバナナ式テキスト")
    print("=" * 60)
    results = []
    for i, b in enumerate(banners):
        print(f"\n[{i+1}/{len(banners)}] {b['filename']}")
        path = generate_image(b["prompt"], b["refs"], b["filename"])
        results.append((b["filename"], path))
        if path: time.sleep(8)
        else: time.sleep(15)
    print("\n" + "=" * 60)
    ok = sum(1 for _, p in results if p)
    for f, p in results:
        print(f"  [{'OK' if p else 'FAIL'}] {f}")
    print(f"\n{ok}/{len(results)} generated")
    if ok > 0:
        g = create_gallery(results)
        print(f"Gallery: {g}")
    print("=" * 60)

#!/usr/bin/env python3
"""
DESIGN FRAMES 09: MELTY R2
参照画像なし + テキスト指示シンプル化 + ひとつ強調
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
OUT = BASE_DIR / "banners_09_melty_r2"
OUT.mkdir(exist_ok=True)


def generate_image(prompt, filename, retries=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
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
# テキスト指示 — シンプル＆明確
# ============================================================
TEXT_RULES = """
=== TEXT RULES (CRITICAL — READ CAREFULLY) ===

This image must contain EXACTLY 2 text elements:

1. Brand name: MELTY
   - English, 5 letters: M-E-L-T-Y

2. Japanese catchcopy (MUST be written EXACTLY as shown):
   がんばった日は、もうひとつ食べていい。

   IMPORTANT — Read this carefully:
   Line 1: がんばった日は、
   Line 2: もうひとつ食べていい。

   The word もうひとつ means "one more" — it is NOT もうわっと or もうわつ.
   ひ = the hiragana character that looks like a curved stroke
   と = the hiragana character for "to"
   つ = the hiragana character for "tsu" (a curved U shape)

   VERIFY: Does your text say ひとつ (hi-to-tsu)? NOT わっと, NOT わつ, NOT わわつ.

Font style: Soft, rounded sans-serif (NOT serif/mincho). Cute but professional.
NO other text anywhere. NO watermarks. NO subtitles.
"""

BRAND_DNA = """
BRAND: MELTY — Monthly artisan sweets subscription
Colors: Warm pink (#ff8a9e), peach (#ffc8a0), cream (#fff0e8), light pink (#fce4ec)
Mood: Warm, rewarding, indulgent, dreamy. Sophisticated cute — like a Parisian patisserie.
Light: Soft, diffused, warm golden-hour. No harsh shadows.
"""

# ============================================================
# 8 Patterns — ビジュアルは前回良かったのでキープ、テキスト指示だけ変更
# ============================================================

def make_prompt(visual_desc):
    return f"""Create a 1080x1080 pixel square advertisement image.

{BRAND_DNA}

{visual_desc}

{TEXT_RULES}
"""

P_A1 = make_prompt("""
VISUAL — FLAT LAY:
Bird's eye view of artisan sweets on marble surface.
Pastel macarons (pink, lavender, mint), chocolate bonbons, strawberry tart slice.
Rose petals, gold leaf flakes, linen napkin scattered around.
Soft diffused overhead lighting. Dreamy warmth.
Center area slightly clear for text placement.
Text in warm brown color, centered.
"MELTY" at top in elegant lettering.
""")

P_A2 = make_prompt("""
VISUAL — CHOCOLATE DRIP:
Close-up of melted chocolate being poured over cream puffs.
Glossy, rich chocolate catching warm light. Dreamy pink bokeh background.
Lower portion darker for text contrast.
Text in white/cream over dark chocolate area at bottom.
"MELTY" at top in warm gold.
""")

P_B1 = make_prompt("""
VISUAL — MACARON TOWER:
Beautiful pyramid of pastel macarons — pink, peach, lavender, mint.
Shot slightly from below. Soft pink background.
Gold leaf details. Warm lighting.
Text on right side in dark brown. Soft rounded font.
"MELTY" top-left, small and elegant.
""")

P_B2 = make_prompt("""
VISUAL — GIFT BOX:
Pink gift box being opened, inside: artisan chocolates and petit fours.
Tissue paper, rose petals scattered. Pink/cream surface.
The feeling of unwrapping a reward for yourself.
Text below the box in elegant dark text.
"MELTY" at top or on the gift card.
""")

P_C1 = make_prompt("""
VISUAL — WOMAN ENJOYING SWEET:
Young Japanese woman (mid 20s) biting into a macaron.
Expression of pure bliss — eyes closed, slight smile.
Soft warm lighting. Creamy bokeh background.
Wearing cream sweater. Intimate, warm, natural (not posed).
PHOTOREALISTIC.
Text at bottom in warm brown. Large, readable.
"MELTY" above her.
""")

P_C2 = make_prompt("""
VISUAL — COZY EVENING:
Woman's hands holding warm cocoa cup with macaron on saucer.
Soft knit blanket visible. Fairy lights in bokeh background.
Small open subscription box with sweets nearby.
Warm, golden, intimate atmosphere.
Text overlaid in cream/white with subtle shadow for readability.
"MELTY" small, elegant.
""")

P_D1 = make_prompt("""
VISUAL — MINIMAL PINK:
ONE perfect pink macaron on clean pink surface.
Massive negative space. Minimalist, sophisticated.
A few crumbs artfully scattered. Soft shadow.
Text LARGE — a major design element filling the negative space.
Dark brown or charcoal text.
"MELTY" small, in corner.
""")

P_D2 = make_prompt("""
VISUAL — STRAWBERRY TART:
Close-up of strawberry tart being assembled.
Fresh strawberry being placed on whipped cream on golden pastry.
Powdered sugar in air catching warm light.
Pink/peach bokeh background.
Text at top in dark brown.
"MELTY" elegantly placed.
""")

banners = [
    (P_A1, "melty_A1_flatlay.png"),
    (P_A2, "melty_A2_chocolate.png"),
    (P_B1, "melty_B1_macaron.png"),
    (P_B2, "melty_B2_giftbox.png"),
    (P_C1, "melty_C1_woman.png"),
    (P_C2, "melty_C2_cozy.png"),
    (P_D1, "melty_D1_minimal.png"),
    (P_D2, "melty_D2_strawberry.png"),
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    concepts = {
        "A1": ("Flat Lay Paradise", "俯瞰撮り。マカロン×チョコ×バラの花びら。"),
        "A2": ("Chocolate Drip", "とろけるチョコレートの瞬間。温かさ。"),
        "B1": ("Macaron Tower", "パステルマカロンの山。豊かさと喜び。"),
        "B2": ("Gift Box Reveal", "自分へのご褒美を開ける瞬間。"),
        "C1": ("Sweet Moment", "マカロンを食べる至福の表情。"),
        "C2": ("Cozy Evening", "がんばった日の夜。ココアとスイーツ。"),
        "D1": ("Minimal Pink", "1つのマカロン×大きな余白。ミニマル。"),
        "D2": ("Strawberry Dream", "いちごタルトが完成する瞬間。粉糖。"),
    }
    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]
            cn, cd = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_09_melty_r2/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{cn}</div>
                    <div class="card-desc">{cd}</div>
                </div>
            </div>"""
    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>MELTY R2</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#fffaf5;color:#5a3e36;font-family:'Noto Sans JP',sans-serif;font-weight:300;}}
.hero{{padding:60px 40px 40px;text-align:center;}}
.hero h1{{font-size:48px;font-weight:700;letter-spacing:8px;color:#ff8a9e;}}
.hero p{{font-size:16px;color:#5a3e36;margin-top:16px;}}
.hero .meta{{display:flex;justify-content:center;gap:16px;margin-top:16px;font-size:10px;letter-spacing:2px;color:#b08878;}}
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
</style>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap" rel="stylesheet">
</head><body>
<div class="hero">
  <h1>MELTY</h1>
  <p>「がんばった日は、もうひとつ食べていい。」</p>
  <div class="meta"><span class="badge">R2</span><span class="badge">FEMALE</span><span class="badge">PLAYFUL</span></div>
</div>
<div class="grid">{cards_html}</div>
<div class="zoom-overlay" id="zo" onclick="closeZoom()"><img id="zi" src=""></div>
<div class="footer">DESIGN FRAMES 09 MELTY R2 — {timestamp}</div>
<script>
function openZoom(s){{document.getElementById('zi').src=s;document.getElementById('zo').classList.add('active');}}
function closeZoom(){{document.getElementById('zo').classList.remove('active');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeZoom();}});
</script></body></html>"""
    p = BASE_DIR / "gallery_09_melty_r2.html"
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return str(p)


if __name__ == "__main__":
    print("=" * 60)
    print("MELTY R2 — 参照画像なし + テキスト指示シンプル化")
    print("=" * 60)
    results = []
    for i, (prompt, fname) in enumerate(banners):
        print(f"\n[{i+1}/{len(banners)}] {fname}")
        path = generate_image(prompt, fname)
        results.append((fname, path))
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

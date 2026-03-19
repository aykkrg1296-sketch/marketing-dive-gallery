#!/usr/bin/env python3
"""
DESIGN FRAMES 09: MELTY — ご褒美スイーツサブスク
参照画像付き + ゴシック体 + 一文字指定（LUMIERE R4の学びを全反映）

Brand: MELTY
Industry: スイーツ / パティスリー
Target: FEMALE (20-30代)
Tone: PLAYFUL (かわいい × ご褒美感 × とろける)
Copy: がんばった日は、もうひとつ食べていい。
Palette: #ff8a9e / #ffc8a0 / #fff0e8 / #fce4ec / #fffaf5
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
    print("GOOGLE_API_KEY not found")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
OUT = BASE_DIR / "banners_09_melty"
OUT.mkdir(exist_ok=True)

# 参照画像: LUMIERE R4のテキスト精度が高かったもの
REF_IMAGE = str(BASE_DIR / "banners_01_lumiere_r4" / "lumiere_A1_ref.png")


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
            print(f"\n  Generating: {filename} (attempt {attempt+1}/{retries+1})")
            r = requests.post(url, json=payload, timeout=180)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if r.status_code == 503:
                wait = 20 * (attempt + 1)
                print(f"  503 high demand, waiting {wait}s...")
                time.sleep(wait)
                continue
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}: {r.text[:300]}")
                if attempt < retries:
                    time.sleep(15)
                    continue
                return None
            data = r.json()
            for c in data.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    if "inlineData" in p:
                        img = base64.b64decode(p["inlineData"]["data"])
                        out_path = OUT / filename
                        with open(out_path, "wb") as f:
                            f.write(img)
                        size_kb = len(img) / 1024
                        print(f"  Done: {out_path.name} ({size_kb:.0f}KB)")
                        return str(out_path)
            print(f"  No image in response")
            if attempt < retries:
                time.sleep(10)
                continue
            return None
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries:
                time.sleep(15)
                continue
            return None
    return None


# ============================================================
# 参照画像指示 — テキスト品質のみ参照
# ============================================================
REF_INSTRUCTION = """[TEXT QUALITY REFERENCE ONLY — DO NOT COPY THE VISUAL DESIGN]
This image shows the level of JAPANESE TEXT QUALITY I expect.
Notice how each Japanese character is perfectly formed, crisp, and readable.
YOUR image will have COMPLETELY DIFFERENT colors, mood, and subject matter.
But the TEXT must be rendered at THIS quality level or better.
The text in YOUR image will be different Japanese characters — but rendered just as perfectly.
DO NOT copy the dark/gold color scheme. DO NOT copy the woman's pose. ONLY learn from the text quality.
"""

# ============================================================
# テキスト精度ルール
# ============================================================
TEXT_PRECISION = """
=== TEXT RENDERING — CRITICAL ===

FONT: Rounded gothic / soft sans-serif. Think soft, friendly, slightly rounded edges.
NOT sharp corporate gothic — SOFT and CUTE but still clean and professional.

MAIN COPY — 16 characters:
がんばった日は、もうひとつ食べていい。

Character-by-character:
1. が (hiragana GA — か with ゛)
2. ん (hiragana N)
3. ば (hiragana BA — は with ゛)
4. っ (small TSU — smaller than regular つ)
5. た (hiragana TA)
6. 日 (kanji NICHI/HI = day — rectangle with horizontal line in middle)
7. は (hiragana HA — NOT ば, no dakuten)
8. 、(comma)
9. も (hiragana MO)
10. う (hiragana U)
11. ひ (hiragana HI)
12. と (hiragana TO)
13. つ (hiragana TSU — regular size, NOT small っ)
14. 食 (kanji TABE/SHOKU = eat — top is 人+一, bottom is 良-like shape)
15. べ (hiragana BE — へ with ゛)
16. て (hiragana TE)
17. い (hiragana I)
18. い (hiragana I — same character repeated)
19. 。(period)

CRITICAL:
- 日 = simple rectangle with one horizontal line inside (day)
- 食 = eat kanji — top part like a roof, bottom part
- っ (small tsu) must be SMALLER than regular つ
- ば has dakuten (゛), は does NOT

BRAND NAME: MELTY (English, 5 letters, all caps or lowercase)

ONLY 2 text elements in the entire image:
1. MELTY (brand name)
2. がんばった日は、もうひとつ食べていい。(main copy)
NO other text. NO watermarks. NO captions.
"""

# ============================================================
# ブランドDNA
# ============================================================
BRAND_DNA = """
BRAND: MELTY — Reward Sweets Subscription
A monthly subscription box of artisan sweets. Small luxuries for women who work hard.
The name evokes melting chocolate, melting stress away, melting into happiness.

VISUAL IDENTITY:
- Colors: Warm pinks (#ff8a9e), peach (#ffc8a0), cream (#fff0e8), light pink (#fce4ec), near-white (#fffaf5)
- Also allowed: chocolate brown, caramel gold, strawberry red accents
- Photography: Warm, soft-focus, dreamy. Like a pastel Instagram aesthetic but more polished.
- Food styling: Professional patisserie level. Macarons, chocolate bonbons, fruit tarts, cream puffs.
- Mood: Warm, rewarding, indulgent but not guilty. A hug in visual form.
- Light: Soft, diffused, warm golden-hour feel. No harsh shadows.
- NOT cheap-looking. NOT overly childish. Sophisticated cute. Like a high-end Parisian patisserie.
"""

# ============================================================
# 8 Patterns
# ============================================================

P_A1 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — FLAT LAY PARADISE:
- Bird's eye view (flat lay) of beautiful artisan sweets arranged on a marble surface
- Macarons in pastel colors (pink, lavender, mint, peach), chocolate bonbons, a slice of strawberry tart
- Scattered rose petals, gold leaf flakes, a linen napkin
- Soft diffused lighting from above. Dreamy, warm.
- Leave the CENTER area slightly clear for text

TEXT: Center of image:
がんばった日は、
もうひとつ食べていい。
Warm brown or dark pink text. Soft rounded gothic font. Large, readable.
Top or bottom: "MELTY" in elegant lettering.

{TEXT_PRECISION}
"""

P_A2 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — CHOCOLATE DRIP:
- Close-up of warm melted chocolate being poured over a stack of cream puffs
- The chocolate is glossy, rich, viscous — catching warm light
- Steam or warmth visible. Dreamy bokeh background in warm pinks.
- The image feels WARM — like being wrapped in a blanket
- Lower portion darker (chocolate) for text contrast

TEXT: Bottom area:
がんばった日は、
もうひとつ食べていい。
White or cream text. Soft rounded font. Over the darker chocolate area for contrast.
Top: "MELTY" in warm gold or cream.

{TEXT_PRECISION}
"""

P_B1 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — MACARON TOWER:
- A beautiful tower/pyramid of pastel macarons — pink, peach, lavender, mint
- Shot from slightly below, looking up — the tower feels abundant, joyful
- Soft pink background gradient
- Some macarons have their filling visible — cream, ganache, fruit
- Gold leaf details on some macarons
- Warm, soft lighting. Everything looks delicious.

TEXT: Right side, vertically:
がんばった日は、
もうひとつ食べていい。
Dark brown or warm pink text. Soft gothic.
Top-left: "MELTY" small, elegant.

{TEXT_PRECISION}
"""

P_B2 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — GIFT BOX REVEAL:
- A beautiful pink gift box (like a jewelry box) being opened
- Inside: perfectly arranged artisan chocolates and petit fours
- Tissue paper, a small gold "MELTY" card visible
- The box sits on a soft pink/cream surface
- Rose petals scattered around
- The feeling of UNWRAPPING a gift to yourself. Self-love.

TEXT: Below the box or overlaid:
がんばった日は、
もうひとつ食べていい。
Elegant dark text. Soft rounded font.
"MELTY" on the gift card in the box or at the top.

{TEXT_PRECISION}
"""

P_C1 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — WOMAN + SWEET MOMENT:
- A young Japanese woman (mid 20s) taking a bite of a macaron or chocolate
- Her expression: pure bliss. Eyes closed, slight smile. The moment of tasting something amazing.
- Soft warm lighting. Creamy bokeh background.
- She's wearing something soft — cream sweater or pale pink
- The image feels intimate, warm, real (not posed-looking)
- PHOTOREALISTIC but warm and dreamy

TEXT: Bottom or side:
がんばった日は、
もうひとつ食べていい。
Warm brown or dark pink. Soft rounded font. Large.
"MELTY" top area.

{TEXT_PRECISION}
"""

P_C2 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — COZY EVENING:
- A cozy scene: a woman's hands holding a warm cup of cocoa with a macaron on the saucer
- Soft knit blanket visible. Warm lighting like candles or fairy lights in background.
- A small open MELTY subscription box nearby with sweets inside
- The feeling of a peaceful evening at home after a long day
- Warm, golden, intimate

TEXT: Over the scene, positioned for readability:
がんばった日は、
もうひとつ食べていい。
Cream or white text with subtle shadow. Soft rounded font.
"MELTY" small, elegant.

{TEXT_PRECISION}
"""

P_D1 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — MINIMAL PINK:
- A SINGLE perfect macaron on a clean pink/cream surface
- Shot from the side, slightly above. The macaron is the star.
- Perfect form: smooth shell, visible filling, slight feet
- Pastel pink macaron on slightly different shade of pink surface
- MASSIVE negative space — minimalist, sophisticated
- A few crumbs artfully scattered
- Soft shadow. Clean. Elegant simplicity.

TEXT: Large, taking up the negative space:
がんばった日は、
もうひとつ食べていい。
Dark brown or charcoal text. Soft rounded gothic. LARGE — a major design element.
"MELTY" small, bottom or top corner.

{TEXT_PRECISION}
"""

P_D2 = f"""
Create a 1080x1080 pixel square sweets brand advertisement.

{BRAND_DNA}

VISUAL — STRAWBERRY DREAM:
- Close-up of a beautiful strawberry shortcake or tart being assembled
- Fresh strawberries, whipped cream, a golden pastry base
- One strawberry is being placed on top — captured mid-action
- Powdered sugar dusting in the air, catching warm light
- Background: soft pink/peach bokeh
- Everything looks DELICIOUS and dreamy

TEXT: Top area or side:
がんばった日は、
もうひとつ食べていい。
Dark text over lighter area. Soft rounded font.
"MELTY" elegantly placed.

{TEXT_PRECISION}
"""

# ============================================================
banners = [
    {"prompt": P_A1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_A1_flatlay.png"},
    {"prompt": P_A2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_A2_chocolate.png"},
    {"prompt": P_B1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_B1_macaron.png"},
    {"prompt": P_B2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_B2_giftbox.png"},
    {"prompt": P_C1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_C1_woman.png"},
    {"prompt": P_C2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_C2_cozy.png"},
    {"prompt": P_D1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_D1_minimal.png"},
    {"prompt": P_D2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "melty_D2_strawberry.png"},
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
                    <img src="banners_09_melty/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{cn}</div>
                    <div class="card-desc">{cd}</div>
                </div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>DESIGN FRAMES 09: MELTY</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&family=Noto+Sans+JP:wght@300;400;700&family=Zen+Maru+Gothic:wght@400;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#fffaf5;color:#5a3e36;font-family:'Noto Sans JP',sans-serif;font-weight:300;}}
.hero{{padding:80px 40px 60px;text-align:center;position:relative;}}
.hero::before{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 50% 80%,rgba(255,138,158,0.08) 0%,transparent 60%);}}
.hero-brand{{font-family:'Zen Maru Gothic',sans-serif;font-size:64px;font-weight:700;letter-spacing:8px;color:#ff8a9e;position:relative;}}
.hero-sub{{font-size:11px;letter-spacing:6px;color:#d4a090;margin-top:12px;}}
.hero-copy{{font-size:20px;font-weight:400;color:#5a3e36;margin-top:28px;letter-spacing:1px;position:relative;}}
.hero-divider{{width:60px;height:2px;background:linear-gradient(90deg,#ff8a9e,#ffc8a0);margin:24px auto 0;border-radius:1px;}}
.hero-meta{{display:flex;justify-content:center;gap:24px;margin-top:20px;font-size:10px;letter-spacing:2px;color:#b08878;}}
.hero-meta .badge{{padding:4px 12px;border-radius:20px;border:1px solid #ff8a9e44;color:#ff8a9e;}}
.palette-strip{{display:flex;height:6px;max-width:300px;margin:20px auto 0;border-radius:3px;overflow:hidden;}}
.palette-strip .sw{{flex:1;}}
.gallery{{max-width:1200px;margin:0 auto;padding:40px 24px 80px;}}
.section-title{{font-family:'Zen Maru Gothic',sans-serif;font-size:20px;color:#ff8a9e;letter-spacing:4px;margin-bottom:24px;padding-bottom:8px;border-bottom:2px solid #fce4ec;}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:24px;margin-bottom:48px;}}
.card{{background:#fff;border-radius:16px;overflow:hidden;border:1px solid #fce4ec;transition:transform 0.2s,box-shadow 0.2s;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 8px 32px rgba(255,138,158,0.15);}}
.card-img-wrap{{aspect-ratio:1;overflow:hidden;background:#fff0e8;}}
.card-img-wrap img{{width:100%;height:100%;object-fit:cover;cursor:zoom-in;transition:transform 0.3s;}}
.card-img-wrap img:hover{{transform:scale(1.02);}}
.card-info{{padding:16px 20px;}}
.card-label{{font-family:'Zen Maru Gothic',sans-serif;font-size:12px;color:#ff8a9e;letter-spacing:4px;font-weight:700;margin-bottom:4px;}}
.card-title{{font-size:14px;font-weight:400;color:#5a3e36;margin-bottom:6px;}}
.card-desc{{font-size:11px;color:#b08878;line-height:1.6;}}
.zoom-overlay{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(90,62,54,0.9);z-index:1000;cursor:zoom-out;justify-content:center;align-items:center;}}
.zoom-overlay.active{{display:flex;}}
.zoom-overlay img{{max-width:90%;max-height:90%;border-radius:12px;box-shadow:0 0 60px rgba(255,138,158,0.3);}}
.footer{{text-align:center;padding:32px;font-size:9px;letter-spacing:4px;color:#d4a090;border-top:2px solid #fce4ec;}}
@media(max-width:768px){{.grid{{grid-template-columns:1fr;}}.hero-brand{{font-size:36px;}}}}
</style></head><body>
<div class="hero">
  <div class="hero-brand">MELTY</div>
  <div class="hero-sub">Design Frames 09 — Reward Sweets Subscription</div>
  <div class="hero-copy">「がんばった日は、もうひとつ食べていい。」</div>
  <div class="hero-divider"></div>
  <div class="hero-meta">
    <span class="badge">FEMALE</span>
    <span class="badge">PLAYFUL</span>
    <span class="badge">SWEETS</span>
  </div>
  <div class="palette-strip">
    <div class="sw" style="background:#ff8a9e;"></div>
    <div class="sw" style="background:#ffc8a0;"></div>
    <div class="sw" style="background:#fff0e8;"></div>
    <div class="sw" style="background:#fce4ec;"></div>
    <div class="sw" style="background:#fffaf5;"></div>
  </div>
</div>
<div class="gallery">
  <div class="section-title">ALL PATTERNS</div>
  <div class="grid">{cards_html}</div>
</div>
<div class="zoom-overlay" id="zoomOverlay" onclick="closeZoom()"><img id="zoomImg" src="" alt="zoom"></div>
<div class="footer">DOCKING DESIGN SYSTEM — DESIGN FRAMES 09 MELTY — {timestamp}</div>
<script>
function openZoom(s){{document.getElementById('zoomImg').src=s;document.getElementById('zoomOverlay').classList.add('active');}}
function closeZoom(){{document.getElementById('zoomOverlay').classList.remove('active');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeZoom();}});
</script></body></html>"""

    gallery_path = BASE_DIR / "gallery_09_melty.html"
    with open(gallery_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nGallery: {gallery_path}")
    return str(gallery_path)


if __name__ == "__main__":
    print("=" * 60)
    print("DESIGN FRAMES 09: MELTY — ご褒美スイーツサブスク")
    print("Copy: がんばった日は、もうひとつ食べていい。")
    print("=" * 60)

    if not os.path.exists(REF_IMAGE):
        print(f"WARNING: Ref image not found: {REF_IMAGE}")

    results = []
    for i, b in enumerate(banners):
        print(f"\n[{i+1}/{len(banners)}] {b['filename']}")
        path = generate_image(b["prompt"], b["refs"], b["filename"])
        results.append((b["filename"], path))
        if path:
            time.sleep(8)
        else:
            time.sleep(15)

    print("\n" + "=" * 60)
    success = sum(1 for _, p in results if p)
    for fname, path in results:
        print(f"  [{'OK' if path else 'FAIL'}] {fname}")
    print(f"\n{success}/{len(results)} generated")

    if success > 0:
        gallery = create_gallery(results)
        print(f"Gallery: {gallery}")
    print("=" * 60)

#!/usr/bin/env python3
"""
DESIGN FRAMES 01: LUMIERE R2 — テキスト精度強化版
Gemini一発生成。テキストもデザインの一部。プロンプトのテキスト指示を超厳密に。

改善ポイント:
- テキスト要素を最小限に（3→2要素）
- 日本語テキストを一文字ずつ指定
- テキスト品質チェック指示を大幅強化
- ブランド名は英語のみ（AI得意）
- 日本語コピーは短く、大きく、明確に
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
OUT = BASE_DIR / "banners_01_lumiere_r2"
OUT.mkdir(exist_ok=True)


def generate_image(prompt, filename, retries=3):
    parts = [{"text": prompt}]
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
# テキスト精度強化ルール（全プロンプト共通）
# ============================================================
TEXT_PRECISION = """
=== TEXT RENDERING — CRITICAL QUALITY REQUIREMENTS ===

THE TEXT IS THE MOST IMPORTANT ELEMENT. If the text is wrong, the entire banner is worthless.

JAPANESE TEXT — CHARACTER-BY-CHARACTER VERIFICATION:
The main copy is: その肌、まだ目覚めていない。
Breaking it down character by character:
- そ (so) — hiragana
- の (no) — hiragana
- 肌 (hada/skin) — kanji: left radical 月, right side 几
- 、 — Japanese comma (touten)
- ま (ma) — hiragana
- だ (da) — hiragana
- 目 (me/eye) — kanji: rectangle with two horizontal lines inside
- 覚 (kaku/awaken) — kanji: top 学-like shape, bottom 見
- め (me) — hiragana
- て (te) — hiragana
- い (i) — hiragana
- な (na) — hiragana
- い (i) — hiragana
- 。 — Japanese period (kuten)

Total: 14 characters. Count them. Verify each one.

ADDITIONAL TEXT:
- Brand name: LUMIERE (7 English letters, all caps, can also use LUMIÈRE with accent)

TEXT QUALITY CHECKLIST (verify EVERY point):
✓ Every character is perfectly formed — no missing strokes, no merged characters
✓ 肌 has the correct radical 月 on the left — NOT 服 (which has different right side)
✓ 覚 is correctly written — NOT 党 or 寛 or similar characters
✓ No random characters or symbols appear anywhere
✓ Text is crisp, clean, high contrast against background
✓ Kerning (spacing between characters) is consistent and professional
✓ Text integrates beautifully with the visual design — it's part of the art, not slapped on top
"""

BRAND_DNA = """
=== BRAND: LUMIERE — Luxury Skincare D2C ===
A high-end Japanese skincare brand. "Light" in French.

VISUAL RULES:
- Colors: ONLY deep black (#0d0906), charcoal (#1a1a1a), rich gold (#d4a843), soft gold (#f5d78e), white (#ffffff)
- NO other colors. Black/gold/white only.
- PHOTOREALISTIC cinematic quality. NOT anime.
- Real Japanese woman, late 20s-early 30s. Flawless luminous skin.
- Mood: Quiet luxury. Like a VOGUE or ELLE advertisement.
- Every element intentional. Nothing cluttered.
"""

# ============================================================
# 8 Patterns — テキスト指示超厳密版
# ============================================================

PATTERN_A1 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — EXTREME CLOSE-UP:
- Extreme close-up of a Japanese woman's face — cheekbone to eyebrow area
- Her skin: poreless, luminous, golden sidelight creating dramatic chiaroscuro
- Tiny floating gold particles (gold leaf dust) catching light
- Her eye partially visible — half-closed, gold eyeshadow shimmer
- Left 40% is darker — reserved for text placement
- Right 60% is her illuminated face

TEXT DESIGN — THIS IS THE KEY:
- Top-left: "LUMIERE" in thin elegant serif, gold color (#d4a843), wide letter-spacing
  The text should feel like part of the luxury design — not stamped on
- Center-left area, positioned beautifully over the darker zone:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  White (#ffffff), elegant thin serif/mincho style
  The text should be LARGE enough to be a design element, not small footnote
  Each line on its own row with generous line-height

{TEXT_PRECISION}

ATMOSPHERE: Tom Ford perfume commercial. Silent. Intimate. Luxurious.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text. NO watermarks. NO subtitles. NO English translations.
"""

PATTERN_A2 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — AWAKENING MOMENT:
- Close-up of a Japanese woman's face (chin to forehead)
- Her eyes are JUST OPENING — lashes lifting, a sliver of iris visible
- Golden light pouring in from the right side — first morning light
- Her skin glows — light emerging FROM her pores
- Gold dust particles suspended in air around her face
- Left side: deep black. Right: golden warm light
- Bottom area darker — reserved for text

TEXT DESIGN:
- Top-right: "LUMIERE" in thin serif, gold (#d4a843)
- Bottom-left, positioned over dark area:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  White, elegant, large enough to be a bold design statement
  Think fashion magazine headline typography

{TEXT_PRECISION}

ATMOSPHERE: The exact moment between sleep and consciousness. Cinematic.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text anywhere.
"""

PATTERN_B1 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — GOLD DUST SILHOUETTE:
- Pure BLACK background — deep, velvety, absolute darkness
- A woman's SILHOUETTE (side profile, head and neck)
- Her outline is defined by GOLD DUST particles (#d4a843, #f5d78e)
- Gold particles trace her jawline, cheekbone, nose, forehead, flowing hair
- Some particles are dense along skin contour, others drift into darkness
- Inside silhouette: hints of her face — curve of lips, bridge of nose
- The gold dust is LUMINOUS — glows like fireflies
- Silhouette positioned slightly RIGHT, center-left clear for text

TEXT DESIGN — LARGE AND CENTRAL:
- Top-center: "LUMIERE" small, gold, wide letter-spacing, elegant
- CENTER of image (over the dark area left of silhouette):
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  PURE WHITE, elegant serif font, LARGE — this is the visual focal point along with the silhouette
  The text and the gold silhouette together create the composition

{TEXT_PRECISION}

ATMOSPHERE: Museum-quality art piece that happens to be an advertisement.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text.
"""

PATTERN_B2 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — GOLD PARTICLE FACE:
- Pure BLACK background
- A woman's face STRAIGHT ON — visible only through gold particles
- Thousands of tiny gold particles form a point cloud of her face
- Features recognizable but ethereal — eyes, nose, lips through particle cloud
- Particles denser at eyes and lips, sparser at edges
- Some particles stream upward like golden smoke
- Face positioned center-right and slightly lower
- Upper-left area clear for text

TEXT DESIGN:
- Top-left: "LUMIERE" in gold, thin elegant serif, wide spacing
- Left side, vertically stacked:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  White, refined serif, positioned to complement the particle face
  Large enough to be a major visual element

{TEXT_PRECISION}

ATMOSPHERE: Like looking at a constellation that forms a face. Hauntingly beautiful.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text.
"""

PATTERN_C1 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — PRODUCT HERO:
- A sleek minimal skincare bottle at center — black glass, gold cap
- Design: cylindrical or rectangular with rounded edges (Aesop meets Tom Ford)
- Sitting on a reflective black surface (polished obsidian)
- LIQUID GOLD flowing/dripping from above — viscous, luxurious
- Gold liquid pools around bottle base on reflective surface
- Behind: subtle bokeh of gold light particles in darkness
- Top area clear for text

TEXT DESIGN:
- Top area, centered:
  Line 1: その肌、まだ目覚めていない。
  White, elegant serif, medium-large, clean
- Below the main copy, centered:
  "LUMIERE" in gold (#d4a843), thin serif, wide letter-spacing

{TEXT_PRECISION}

ATMOSPHERE: Luxury product photography. Cinematic studio lighting.
Only 2 text elements: その肌、まだ目覚めていない。 + LUMIERE
NO other text. The product bottle can have minimal branding embossed on it.
"""

PATTERN_C2 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — SPLIT: MODEL + PRODUCT:
- LEFT 45%: Japanese woman's face in profile, looking right, chin lifted
  Rembrandt lighting. Luminous skin. Only face/neck visible, rest fades to black.
- RIGHT 45%: Sleek black skincare bottle with gold accents, floating
- CENTER: Gold particles connect woman and product — a golden thread of light
- Bottom area darker for text

TEXT DESIGN:
- Top-center: "LUMIERE" in gold, elegant, wide spacing
- Bottom, spanning full width:
  その肌、まだ目覚めていない。
  White, elegant serif, large
  Positioned so it anchors both halves together

{TEXT_PRECISION}

ATMOSPHERE: High-fashion editorial meets luxury product ad.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text.
"""

PATTERN_D1 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — EDITORIAL / THE GAZE:
- Stunning Japanese woman from shoulders up
- Looking DIRECTLY at viewer — confident, calm, magnetic
- Skin impossibly perfect — soft golden light from above
- Hair sleek, dark, pulled back — nothing distracts from SKIN
- Bare shoulders, collarbones visible
- Background: smooth gradient charcoal to black
- She's in the LOWER 60%. Upper 40% is dark empty space with subtle gold particle trail
- GENEROUS negative space above her — intentional, communicates quiet confidence

TEXT DESIGN — ULTRA-MINIMAL:
- Top-left: "LUMIERE" small, gold (#d4a843), thin, wide letter-spacing
- CENTER of upper empty space (above her head):
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  Large, white, elegant thin serif
  The text FLOATS in the dark space above her
  She looks up toward the words

{TEXT_PRECISION}

ATMOSPHERE: Full-page ad from Japanese VOGUE. Effortlessly luxurious.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text.
"""

PATTERN_D2 = f"""
Create a 1080x1080 pixel square luxury skincare advertisement image.

{BRAND_DNA}

COMPOSITION — EDITORIAL / THE TOUCH:
- Japanese woman in three-quarter view, elegant, serene
- Her right hand touching her left cheek — gentle, deliberate
- The gesture draws attention to her SKIN
- Her fingertips have gold shimmer — like she touched liquid gold
- Where fingertips meet cheek: tiny gold light particles emanate
- Rest fades into deep black shadow
- Only face, hand, and gold contact point illuminated
- Right side and bottom darker for text

TEXT DESIGN:
- Top area, centered: "LUMIERE" in gold, elegant serif, wide spacing, medium size
- Right side or bottom-right:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  White, refined serif, positioned to complement the composition

{TEXT_PRECISION}

ATMOSPHERE: Self-care as sacred act. Sensual but elegant.
Only 2 text elements: LUMIERE + その肌、まだ目覚めていない。
NO other text.
"""

# ============================================================
# 生成リスト
# ============================================================
banners = [
    {"prompt": PATTERN_A1, "filename": "lumiere_A1_closeup.png"},
    {"prompt": PATTERN_A2, "filename": "lumiere_A2_eyes.png"},
    {"prompt": PATTERN_B1, "filename": "lumiere_B1_silhouette.png"},
    {"prompt": PATTERN_B2, "filename": "lumiere_B2_particle.png"},
    {"prompt": PATTERN_C1, "filename": "lumiere_C1_product.png"},
    {"prompt": PATTERN_C2, "filename": "lumiere_C2_split.png"},
    {"prompt": PATTERN_D1, "filename": "lumiere_D1_editorial.png"},
    {"prompt": PATTERN_D2, "filename": "lumiere_D2_touch.png"},
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    concepts = {
        "A1": ("Close-up — Golden Awakening", "極限クローズアップ。肌の質感×ゴールドの光粒子。"),
        "A2": ("Close-up — Eyes Opening", "目覚めの瞬間。まぶたが開く瞬間の光。"),
        "B1": ("Silhouette — Gold Dust", "純黒背景にゴールドダストで描くシルエット。"),
        "B2": ("Silhouette — Particle Face", "ゴールド粒子で構成された正面顔。"),
        "C1": ("Product Hero — Liquid Gold", "プロダクトショット。流れる液体ゴールド。"),
        "C2": ("Product + Model — Split", "左:モデル / 右:プロダクト。ゴールド粒子が繋ぐ。"),
        "D1": ("Editorial — The Gaze", "VOGUEのような全面広告。余白×視線。"),
        "D2": ("Editorial — Touch", "肌に触れる指先からゴールドの光。"),
    }

    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]
            concept_name, concept_desc = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_01_lumiere_r2/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{concept_name}</div>
                    <div class="card-desc">{concept_desc}</div>
                </div>
            </div>
            """

    # v1との比較セクション
    v1_cards = ""
    v1_dir = BASE_DIR / "banners_01_lumiere"
    if v1_dir.exists():
        for f in sorted(v1_dir.glob("*.png")):
            key = f.stem.split("_")[1]
            v1_cards += f"""
            <div class="card v1">
                <div class="card-img-wrap">
                    <img src="banners_01_lumiere/{f.name}" alt="{f.name}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">v1 {key}</div>
                    <div class="card-title">{f.stem}</div>
                </div>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>DESIGN FRAMES 01: LUMIERE R2</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Noto+Sans+JP:wght@300;400;700&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  background: #0d0906;
  color: #e0d8cc;
  font-family: 'Noto Sans JP', sans-serif;
  font-weight: 300;
}}

.hero {{
  padding: 80px 40px 60px;
  text-align: center;
  position: relative;
}}
.hero::before {{
  content: '';
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 80%, rgba(212,168,67,0.08) 0%, transparent 60%);
}}
.hero-brand {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 64px; font-weight: 700; letter-spacing: 16px;
  color: #d4a843; position: relative;
}}
.hero-sub {{
  font-size: 11px; letter-spacing: 6px; color: #665a45;
  margin-top: 12px; text-transform: uppercase;
}}
.hero-copy {{
  font-size: 22px; font-weight: 400; color: #fff;
  margin-top: 28px; letter-spacing: 2px; position: relative;
}}
.hero-divider {{ width: 60px; height: 1px; background: #d4a843; margin: 24px auto 0; }}
.hero-meta {{
  display: flex; justify-content: center; gap: 24px;
  margin-top: 20px; font-size: 10px; letter-spacing: 2px; color: #555;
}}
.hero-meta .badge {{
  padding: 4px 12px; border-radius: 20px; border: 1px solid #d4a84333; color: #d4a843;
}}
.palette-strip {{ display: flex; height: 4px; max-width: 300px; margin: 20px auto 0; }}
.palette-strip .sw {{ flex: 1; }}

.gallery {{ max-width: 1200px; margin: 0 auto; padding: 40px 24px 80px; }}
.section-title {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 20px; color: #d4a843; letter-spacing: 4px;
  margin-bottom: 24px; padding-bottom: 8px; border-bottom: 1px solid #1a1810;
}}
.grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 48px; }}
.card {{
  background: #111008; border-radius: 12px; overflow: hidden;
  border: 1px solid #1a1810; transition: transform 0.2s, box-shadow 0.2s;
}}
.card:hover {{
  transform: translateY(-4px); box-shadow: 0 8px 32px rgba(212,168,67,0.1);
}}
.card.v1 {{ border-color: #2a2010; opacity: 0.7; }}
.card.v1:hover {{ opacity: 1; }}
.card-img-wrap {{ aspect-ratio: 1; overflow: hidden; background: #0a0806; }}
.card-img-wrap img {{
  width: 100%; height: 100%; object-fit: cover;
  cursor: zoom-in; transition: transform 0.3s;
}}
.card-img-wrap img:hover {{ transform: scale(1.02); }}
.card-info {{ padding: 16px 20px; }}
.card-label {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 12px; color: #d4a843; letter-spacing: 4px; font-weight: 600; margin-bottom: 4px;
}}
.card-title {{ font-size: 14px; font-weight: 400; color: #fff; margin-bottom: 6px; }}
.card-desc {{ font-size: 11px; color: #665a45; line-height: 1.6; }}

.zoom-overlay {{
  display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.95); z-index: 1000; cursor: zoom-out;
  justify-content: center; align-items: center;
}}
.zoom-overlay.active {{ display: flex; }}
.zoom-overlay img {{ max-width: 90%; max-height: 90%; border-radius: 8px; box-shadow: 0 0 60px rgba(212,168,67,0.2); }}

.footer {{
  text-align: center; padding: 32px; font-size: 9px; letter-spacing: 4px; color: #333;
  border-top: 1px solid #1a1810;
}}

@media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} .hero-brand {{ font-size: 36px; }} }}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-brand">LUMIERE</div>
  <div class="hero-sub">Design Frames 01 R2 — Text Precision Enhanced</div>
  <div class="hero-copy">「その肌、まだ目覚めていない。」</div>
  <div class="hero-divider"></div>
  <div class="hero-meta">
    <span class="badge">FEMALE</span>
    <span class="badge">HARD</span>
    <span class="badge">BEAUTY</span>
  </div>
  <div class="palette-strip">
    <div class="sw" style="background:#0d0906;"></div>
    <div class="sw" style="background:#1a1a1a;"></div>
    <div class="sw" style="background:#d4a843;"></div>
    <div class="sw" style="background:#f5d78e;"></div>
    <div class="sw" style="background:#ffffff;"></div>
  </div>
</div>

<div class="gallery">
  <div class="section-title">R2 — TEXT PRECISION ENHANCED</div>
  <div class="grid">{cards_html}</div>

  {"<div class='section-title'>COMPARE: v1 (previous)</div><div class='grid'>" + v1_cards + "</div>" if v1_cards else ""}
</div>

<div class="zoom-overlay" id="zoomOverlay" onclick="closeZoom()">
  <img id="zoomImg" src="" alt="zoom">
</div>

<div class="footer">DOCKING DESIGN SYSTEM — DESIGN FRAMES 01 R2 — GENERATED {timestamp}</div>

<script>
function openZoom(src) {{ document.getElementById('zoomImg').src = src; document.getElementById('zoomOverlay').classList.add('active'); }}
function closeZoom() {{ document.getElementById('zoomOverlay').classList.remove('active'); }}
document.addEventListener('keydown', e => {{ if(e.key === 'Escape') closeZoom(); }});
</script>
</body>
</html>"""

    gallery_path = BASE_DIR / "gallery_01_lumiere.html"
    with open(gallery_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nGallery: {gallery_path}")
    return str(gallery_path)


if __name__ == "__main__":
    print("=" * 60)
    print("DESIGN FRAMES 01: LUMIERE R2 — テキスト精度強化版")
    print("=" * 60)

    results = []
    for i, b in enumerate(banners):
        print(f"\n[{i+1}/{len(banners)}] {b['filename']}")
        path = generate_image(b["prompt"], b["filename"])
        results.append((b["filename"], path))
        if path:
            time.sleep(8)
        else:
            time.sleep(15)

    print("\n" + "=" * 60)
    print("RESULTS:")
    success = 0
    for fname, path in results:
        status = "OK" if path else "FAIL"
        print(f"  [{status}] {fname}")
        if path:
            success += 1
    print(f"\n{success}/{len(results)} generated")

    if success > 0:
        gallery = create_gallery(results)
        print(f"Gallery ready: {gallery}")

    print("=" * 60)

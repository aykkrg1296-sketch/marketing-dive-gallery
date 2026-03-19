#!/usr/bin/env python3
"""
DESIGN FRAMES 01: LUMIERE — 高級スキンケアD2C
架空ブランドバナー生成（Google Gemini API）

Brand: LUMIERE
Industry: 美容 / 高級スキンケア
Target: FEMALE (30代, 本物志向)
Tone: HARD (ラグジュアリー × ミニマル)
Copy: その肌、まだ目覚めていない。
Palette: #0d0906 / #1a1a1a / #d4a843 / #f5d78e / #ffffff

8 variations: 4 concepts × 2 variants each
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
OUT = BASE_DIR / "banners_01_lumiere"
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
# ブランド共通定義
# ============================================================
BRAND_DNA = """
=== BRAND: LUMIERE — Luxury Skincare D2C ===
A high-end Japanese skincare brand. The name means "light" in French.
The brand awakens dormant radiance hidden beneath the skin surface.

VISUAL IDENTITY:
- Color palette STRICTLY: Deep black (#0d0906), charcoal (#1a1a1a), rich gold (#d4a843), soft gold (#f5d78e), pure white (#ffffff)
- NO other colors. No pink, no blue, no green. ONLY black/gold/white spectrum.
- Typography: Ultra-clean, thin serif or elegant sans-serif. Minimal. High fashion editorial feel.
- Texture: Matte black surfaces, liquid gold, light particles like gold dust floating in darkness
- Photography style: Cinematic, dramatic lighting. Rembrandt or butterfly lighting on skin.
- Mood: Quiet luxury. Not loud. Not flashy. Like stepping into a dimly lit private salon.

ABSOLUTE RULES:
- This must look like a REAL luxury skincare advertisement you'd see in VOGUE or ELLE
- NOT anime, NOT illustration — PHOTOREALISTIC cinematic quality
- The woman should look like a real Japanese woman in her late 20s-early 30s
- Skin must look FLAWLESS — luminous, dewy, the kind of skin that makes you stare
- Every element must feel intentional. Nothing accidental. Nothing cluttered.
- Minimal text. Maximum impact.
"""

# ============================================================
# Pattern A: クローズアップ — 肌の質感 × ゴールドの光粒子
# ============================================================
PATTERN_A1 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN A1: EXTREME CLOSE-UP — Golden Awakening ===

COMPOSITION:
- EXTREME CLOSE-UP of a Japanese woman's face — we see from her cheekbone to just above her eyebrow
- Her skin is the STAR: poreless, luminous, lit from the side with warm golden light
- Tiny gold particles (like gold leaf dust) float across the image, catching light
- Her eye is partially visible — closed or half-closed, with gold eyeshadow shimmer
- The lighting creates a dramatic chiaroscuro: one side of her face lit by gold, the other fading into rich black

TEXT (positioned with extreme precision):
- Top-left corner, small elegant text: LUMIERE (thin serif, gold #d4a843, letter-spacing wide)
- Center-left, vertical Japanese text: その肌、(line break) まだ目覚めていない。
  - Font: Elegant, thin weight, pure white (#ffffff)
  - Size: Medium — not overwhelming, but clearly readable
  - Each character perfectly formed and kerned
- Bottom-right, very small: 目覚めの、スキンケア。(gold #f5d78e, thin)

ATMOSPHERE:
- Like a single frame from a perfume commercial directed by Tom Ford
- The gold particles look like the skin itself is releasing light
- Absolutely silent, intimate, luxurious
- Black negative space is as important as the lit areas

TEXT RULES:
- EXACTLY these 3 text elements: LUMIERE / その肌、まだ目覚めていない。 / 目覚めの、スキンケア。
- All text must be 100% perfectly rendered — crisp, clean, no blur, no distortion
- NO other text, NO watermarks, NO logos, NO labels
"""

PATTERN_A2 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN A2: CLOSE-UP VARIANT — Eyes Opening ===

COMPOSITION:
- Close-up of a Japanese woman's face — from chin to forehead
- Her eyes are JUST OPENING — lashes lifting, a sliver of iris visible
- The moment of "awakening" captured in a single frame
- Golden light pours in from the right side as if morning light hitting her face for the first time
- Her skin has an almost supernatural glow — like light is emerging FROM her pores
- Gold dust particles suspended in the air around her face
- Deep black background on the left side, melting into golden light on the right

TEXT:
- Top-right, small: LUMIERE (thin serif, gold #d4a843)
- Bottom half, left-aligned, horizontal Japanese text:
  その肌、
  まだ目覚めていない。
  (Pure white, elegant serif, generous line-height)
- Bottom-left small: 目覚めの、スキンケア。(gold #f5d78e)

ATMOSPHERE:
- The exact moment between sleep and consciousness
- Intimate, cinematic, breathtaking
- You can almost feel the warmth of the golden light

TEXT RULES:
- EXACTLY: LUMIERE / その肌、まだ目覚めていない。 / 目覚めの、スキンケア。
- Perfect Japanese characters. NO other text.
"""

# ============================================================
# Pattern B: シルエット × ゴールドダスト — アーティスティック
# ============================================================
PATTERN_B1 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN B1: SILHOUETTE — Gold Dust Revelation ===

COMPOSITION:
- Pure BLACK background — deep, velvety, absolute darkness
- A woman's SILHOUETTE (side profile, head and neck) — her outline is defined entirely by GOLD DUST
- The gold particles (#d4a843, #f5d78e) trace her jawline, cheekbone, nose bridge, forehead, flowing hair
- Some particles are dense along her skin contour, others drift away into the darkness like she's dissolving into gold
- Inside the silhouette: hints of her actual face visible — just the curve of her lips, the bridge of her nose
- The gold dust is LUMINOUS — it glows against the black like fireflies
- A few larger gold particles float freely in the surrounding darkness

TEXT:
- Center of image, large and bold: その肌、(line break) まだ目覚めていない。
  - Pure white (#ffffff), clean modern serif font
  - Positioned so it overlaps slightly with the silhouette — text and image integrated
  - Generous letter-spacing and line-height
- Top-center: LUMIERE (small, gold #d4a843, ultra-wide letter-spacing)
- Bottom-center: AWAKENING SKINCARE (tiny, gold #f5d78e, letter-spacing)

ATMOSPHERE:
- Museum-quality art piece that happens to be an advertisement
- The gold dust feels alive — like her beauty is literally radiating
- Elegant beyond words. Makes you stop scrolling immediately.

TEXT RULES:
- EXACTLY: LUMIERE / その肌、まだ目覚めていない。 / AWAKENING SKINCARE
- NO other text, NO watermarks
"""

PATTERN_B2 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN B2: SILHOUETTE VARIANT — Frontal Gold Explosion ===

COMPOSITION:
- Pure BLACK background
- A woman's face STRAIGHT ON — but only visible through gold particles
- Thousands of tiny gold particles (#d4a843) form a point cloud of her face — like a 3D scan made of gold dust
- Her features are recognizable but ethereal — you can see her eyes, nose, lips through the particle cloud
- The particles are denser at her key features (eyes, lips) and sparser at the edges
- Some particles stream upward from her head like golden smoke rising
- The effect: her face is MADE of light, of gold, of something otherworldly

TEXT:
- Left side, vertical stack:
  その肌、
  まだ
  目覚めていない。
  (White, thin elegant font, left-aligned)
- Top-left: LUMIERE (gold, small, wide spacing)
- Bottom: 目覚めの、スキンケア。(gold #f5d78e, centered, small)

ATMOSPHERE:
- Like looking at a constellation that forms a face
- Hauntingly beautiful. Not cold — warm, alive, glowing.

TEXT RULES:
- EXACTLY: LUMIERE / その肌、まだ目覚めていない。 / 目覚めの、スキンケア。
- NO other text
"""

# ============================================================
# Pattern C: プロダクト × 光の融合 — コマーシャル寄り
# ============================================================
PATTERN_C1 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN C1: PRODUCT HERO — Liquid Gold ===

COMPOSITION:
- A sleek, minimal skincare bottle/jar at center — black glass with a gold cap and subtle LUMIERE text on the bottle
- The bottle is sitting on a reflective black surface (like polished obsidian)
- LIQUID GOLD is flowing/dripping from above — viscous, luxurious, catching light
- The gold liquid pools around the base of the bottle on the reflective surface
- Behind the bottle: subtle bokeh of gold light particles in the darkness
- The bottle design: minimal, elegant, cylindrical or rectangular with rounded edges. Think Aesop meets Tom Ford.

TEXT:
- Top area, centered: その肌、まだ目覚めていない。
  (White, elegant serif, medium size, well-spaced)
- Below the main copy: LUMIERE (gold #d4a843, thin serif, wide letter-spacing)
- Bottom: 目覚めの、スキンケア。(gold #f5d78e, small)

ATMOSPHERE:
- A luxury product shot from a high-end beauty campaign
- The liquid gold represents the "awakening" — it's alive, moving, transforming
- The black surface reflection doubles the visual impact
- Cinematic product photography quality

TEXT RULES:
- EXACTLY: その肌、まだ目覚めていない。 / LUMIERE / 目覚めの、スキンケア。
- Text on the BOTTLE itself can say LUMIERE (this is part of the product design)
- NO other text or watermarks
"""

PATTERN_C2 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN C2: PRODUCT + MODEL — Split Composition ===

COMPOSITION:
- LEFT 45%: A Japanese woman's face in profile — looking right, chin slightly lifted
  - Dramatic Rembrandt lighting from the right
  - Her skin is absolutely luminous — lit by golden light
  - Only her face/neck visible, the rest fades into black
- RIGHT 45%: A sleek black skincare bottle with gold accents
  - Floating or placed on a dark surface
  - Gold particles connect the woman's face to the product — like a golden thread
- CENTER 10%: A thin vertical line of gold particles bridging the two halves

TEXT:
- Top-center spanning both halves: LUMIERE (gold, thin, wide spacing)
- Bottom-left under her chin: その肌、(white, elegant)
- Bottom-right under the product: まだ目覚めていない。(white, elegant)
  - The sentence is SPLIT across the two halves — connecting woman and product
- Very bottom, centered: 目覚めの、スキンケア。(gold #f5d78e, tiny)

ATMOSPHERE:
- High-fashion editorial meets luxury product advertisement
- The split composition creates a story: SHE is the proof that the product works
- The gold particles physically connecting her to the product = visual metaphor

TEXT RULES:
- EXACTLY: LUMIERE / その肌、まだ目覚めていない。 / 目覚めの、スキンケア。
- NO other text
"""

# ============================================================
# Pattern D: フルブリード × 余白 — ハイファッションエディトリアル
# ============================================================
PATTERN_D1 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN D1: EDITORIAL — The Gaze ===

COMPOSITION:
- A stunning Japanese woman photographed from the shoulders up
- She's looking DIRECTLY at the viewer — confident, calm, magnetic
- Her skin is impossibly perfect — soft golden light from above creates gentle shadows
- Her hair is sleek, dark, pulled back — nothing distracts from her SKIN
- She wears minimal or no visible clothing — bare shoulders, collarbones visible
- Background: a smooth gradient from deep charcoal (#1a1a1a) to black (#0d0906)
- GENEROUS negative space above and around her — she doesn't fill the frame
- A single gold light particle trail falls diagonally across the upper portion of the image

TEXT (ultra-minimal):
- Top-left corner: LUMIERE (gold #d4a843, thin uppercase, small, wide letter-spacing)
- Dead center of image (over the negative space above her head):
  その肌、
  まだ目覚めていない。
  (Large, white, elegant thin serif. Each line centered. Generous line-height.)
  The text floats in the dark space above her — she looks up toward the words
- Bottom-right, very small: 目覚めの、スキンケア。(gold #f5d78e)

ATMOSPHERE:
- A full-page ad from Japanese VOGUE
- The amount of empty space is INTENTIONAL — it communicates quiet confidence
- Her gaze is the anchor. The text is the message. Everything else is darkness and gold dust.
- Not trying too hard. Effortlessly luxurious.

TEXT RULES:
- EXACTLY: LUMIERE / その肌、まだ目覚めていない。 / 目覚めの、スキンケア。
- NO other text, NO watermarks
"""

PATTERN_D2 = f"""
Create a 1080x1080 pixel square luxury skincare banner advertisement.

{BRAND_DNA}

=== PATTERN D2: EDITORIAL VARIANT — Touch ===

COMPOSITION:
- A Japanese woman in three-quarter view — elegant, serene
- Her right hand is touching her left cheek — a gentle, deliberate touch
- The gesture draws attention to her SKIN — the way light plays across her fingers and cheek
- Her fingers have a subtle gold shimmer — as if she just touched liquid gold
- Where her fingertips meet her cheek: tiny gold light particles emanate from the contact point
- The rest of her fades into deep black shadow
- Only her face, hand, and the gold contact point are illuminated

TEXT:
- Top area, centered: LUMIERE (gold #d4a843, elegant, wide spacing)
- Right side, vertical or angled to follow the composition:
  その肌、
  まだ目覚めていない。
  (White, refined serif, medium-large)
- Bottom, small centered: 目覚めの、スキンケア。(gold #f5d78e)

ATMOSPHERE:
- The intimacy of skincare ritual — touching your own face
- The gold particles at the contact point = the moment of "awakening"
- Sensual but not sexual. Elegant. Self-care as a sacred act.
- Tom Ford Beauty meets Shiseido prestige line

TEXT RULES:
- EXACTLY: LUMIERE / その肌、まだ目覚めていない。 / 目覚めの、スキンケア。
- NO other text
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
        "A1": ("Close-up — Golden Awakening", "極限クローズアップ。肌の質感×ゴールドの光粒子。シアロスクーロ照明。"),
        "A2": ("Close-up — Eyes Opening", "目覚めの瞬間。まぶたが開く瞬間の光。ゴールドダスト浮遊。"),
        "B1": ("Silhouette — Gold Dust", "純黒背景にゴールドダストで描くシルエット。アート×広告の融合。"),
        "B2": ("Silhouette — Particle Face", "ゴールド粒子で構成された正面顔。星座のような美しさ。"),
        "C1": ("Product Hero — Liquid Gold", "プロダクトショット。流れる液体ゴールド。反射面の高級感。"),
        "C2": ("Product + Model — Split", "左:モデル / 右:プロダクト。ゴールド粒子が両者を繋ぐ。"),
        "D1": ("Editorial — The Gaze", "VOGUEのような全面広告。余白×視線×ミニマルテキスト。"),
        "D2": ("Editorial — Touch", "肌に触れる指先からゴールドの光が生まれる瞬間。"),
    }

    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]  # A1, A2, B1, etc.
            concept_name, concept_desc = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_01_lumiere/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{concept_name}</div>
                    <div class="card-desc">{concept_desc}</div>
                </div>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>DESIGN FRAMES 01: LUMIERE</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Noto+Sans+JP:wght@300;400;700&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  background: #0d0906;
  color: #e0d8cc;
  font-family: 'Noto Sans JP', sans-serif;
  font-weight: 300;
}}

/* Hero */
.hero {{
  padding: 80px 40px 60px;
  text-align: center;
  position: relative;
  overflow: hidden;
}}
.hero::before {{
  content: '';
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 80%, rgba(212,168,67,0.08) 0%, transparent 60%);
}}
.hero-brand {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 64px; font-weight: 700; letter-spacing: 16px;
  color: #d4a843;
  position: relative;
}}
.hero-sub {{
  font-size: 11px; letter-spacing: 6px; color: #665a45;
  margin-top: 12px; text-transform: uppercase;
}}
.hero-copy {{
  font-size: 22px; font-weight: 400; color: #fff;
  margin-top: 28px; letter-spacing: 2px;
  position: relative;
}}
.hero-divider {{
  width: 60px; height: 1px; background: #d4a843; margin: 24px auto 0;
}}
.hero-meta {{
  display: flex; justify-content: center; gap: 24px;
  margin-top: 20px; font-size: 10px; letter-spacing: 2px; color: #555;
}}
.hero-meta .badge {{
  padding: 4px 12px; border-radius: 20px; border: 1px solid #d4a84333;
  color: #d4a843;
}}

/* Palette strip */
.palette-strip {{
  display: flex; height: 4px; max-width: 300px; margin: 20px auto 0;
}}
.palette-strip .sw {{ flex: 1; }}

/* Grid */
.gallery {{
  max-width: 1200px; margin: 0 auto; padding: 40px 24px 80px;
}}
.grid {{
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;
}}
.card {{
  background: #111008;
  border-radius: 12px; overflow: hidden;
  border: 1px solid #1a1810;
  transition: transform 0.2s, box-shadow 0.2s;
}}
.card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(212,168,67,0.1);
}}
.card-img-wrap {{
  aspect-ratio: 1;
  overflow: hidden;
  background: #0a0806;
}}
.card-img-wrap img {{
  width: 100%; height: 100%; object-fit: cover;
  cursor: zoom-in;
  transition: transform 0.3s;
}}
.card-img-wrap img:hover {{ transform: scale(1.02); }}
.card-info {{
  padding: 16px 20px;
}}
.card-label {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 12px; color: #d4a843; letter-spacing: 4px; font-weight: 600;
  margin-bottom: 4px;
}}
.card-title {{
  font-size: 14px; font-weight: 400; color: #fff;
  margin-bottom: 6px;
}}
.card-desc {{
  font-size: 11px; color: #665a45; line-height: 1.6;
}}

/* Zoom overlay */
.zoom-overlay {{
  display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.95); z-index: 1000; cursor: zoom-out;
  justify-content: center; align-items: center;
}}
.zoom-overlay.active {{ display: flex; }}
.zoom-overlay img {{
  max-width: 90%; max-height: 90%; border-radius: 8px;
  box-shadow: 0 0 60px rgba(212,168,67,0.2);
}}

/* Footer */
.footer {{
  text-align: center; padding: 32px;
  font-size: 9px; letter-spacing: 4px; color: #333;
  border-top: 1px solid #1a1810;
}}

@media (max-width: 768px) {{
  .grid {{ grid-template-columns: 1fr; }}
  .hero-brand {{ font-size: 36px; }}
}}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-brand">LUMIERE</div>
  <div class="hero-sub">Design Frames 01 — Luxury Skincare D2C</div>
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
  <div class="grid">
    {cards_html}
  </div>
</div>

<div class="zoom-overlay" id="zoomOverlay" onclick="closeZoom()">
  <img id="zoomImg" src="" alt="zoom">
</div>

<div class="footer">
  DOCKING DESIGN SYSTEM — DESIGN FRAMES 01 — GENERATED {timestamp}
</div>

<script>
function openZoom(src) {{
  document.getElementById('zoomImg').src = src;
  document.getElementById('zoomOverlay').classList.add('active');
}}
function closeZoom() {{
  document.getElementById('zoomOverlay').classList.remove('active');
}}
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
    print("DESIGN FRAMES 01: LUMIERE — 高級スキンケアD2C")
    print("Copy: その肌、まだ目覚めていない。")
    print("Palette: Black × Gold × White")
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

#!/usr/bin/env python3
"""
DESIGN FRAMES 01: LUMIERE R3 — ゴシック体テスト
仮説: 明朝体が日本語テキスト精度低下の原因
→ ゴシック体（bold sans-serif）に変更してテキスト精度を検証

まず最も出来が良かった4パターン（A2, D1, D2, C1）で検証
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
OUT = BASE_DIR / "banners_01_lumiere_r3"
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
# テキスト精度ルール — ゴシック体版
# ============================================================
TEXT_PRECISION_GOTHIC = """
=== TEXT RENDERING — CRITICAL ===

THE TEXT MUST BE PERFECTLY ACCURATE. Every character matters.

FONT STYLE: Modern GOTHIC (sans-serif), BOLD weight.
Like Helvetica Neue Bold or Hiragino Kaku Gothic Bold.
Clean, uniform stroke width, no serifs, no decorative elements on the characters.
This is NOT mincho/serif — it's GOTHIC/sans-serif with thick uniform strokes.

MAIN COPY — 14 characters total:
その肌、まだ目覚めていない。

Character-by-character:
1. そ (hiragana SO)
2. の (hiragana NO)
3. 肌 (kanji HADA = skin — LEFT side is 月, RIGHT side is 几)
4. 、(comma)
5. ま (hiragana MA — looks like: horizontal stroke on top, then body)
6. だ (hiragana DA — looks like た with ゛)
7. 目 (kanji ME = eye — a rectangle with 2 horizontal lines inside)
8. 覚 (kanji KAKU = awaken — top part similar to 学, bottom part is 見)
9. め (hiragana ME)
10. て (hiragana TE)
11. い (hiragana I — two curved strokes)
12. な (hiragana NA)
13. い (hiragana I — same as #11)
14. 。(period)

CRITICAL CHARACTERS TO GET RIGHT:
- 肌 (skin): The RIGHT side is 几 (NOT the right side of 服 which is different)
- 覚 (awaken): Top is like ツ+冖, bottom is 見. NOT 党, NOT 寛, NOT 竟
- ま (MA): NOT み (MI) — ま has a horizontal top stroke, み does not
- だ (DA): NOT な (NA) — だ is た with dakuten marks ゛

BRAND NAME: LUMIERE (English, all caps, clean sans-serif)

ZERO TOLERANCE:
- NO wrong characters
- NO extra text anywhere
- NO watermarks, labels, or captions
- ONLY these 2 text elements exist in the image
"""

BRAND_DNA = """
BRAND: LUMIERE — Luxury Skincare D2C
Colors: ONLY black (#0d0906), charcoal (#1a1a1a), gold (#d4a843), soft gold (#f5d78e), white
PHOTOREALISTIC cinematic quality. Real Japanese woman, late 20s-30s. Flawless skin.
Mood: Quiet luxury. VOGUE advertisement quality.
"""

# ============================================================
# 4 best patterns × 2 variants = 8 banners
# ============================================================

# A2: 目覚め — R2で最もテキスト精度が高かった
PATTERN_A2a = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Close-up of Japanese woman's face (chin to forehead). Eyes just opening — lashes lifting. Golden light from right side. Her skin glows supernaturally. Gold dust particles floating. Left side deep black, right golden light. Bottom area darker.

TEXT PLACEMENT:
- Top-right corner: LUMIERE (clean bold sans-serif, gold #d4a843, wide letter-spacing)
- Bottom-left, over dark area, TWO LINES:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif font. White color. Large size — a major design element.

{TEXT_PRECISION_GOTHIC}
"""

PATTERN_A2b = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Close-up of Japanese woman — half her face visible, other half in shadow. Eyes half-open, catching golden light. Dramatic split lighting. Gold particles around her. Deep black on one side.

TEXT PLACEMENT:
- Top-left: LUMIERE (bold sans-serif, gold #d4a843)
- Center, over the dark half of the image:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif. White. Large, impactful.

{TEXT_PRECISION_GOTHIC}
"""

# D1: エディトリアル — 構図が最も広告らしかった
PATTERN_D1a = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Stunning Japanese woman from shoulders up. Looking DIRECTLY at viewer — confident, calm. Skin impossibly perfect with soft golden light from above. Hair sleek, dark, pulled back. Bare shoulders. Background: charcoal to black gradient. She's in LOWER 60% of frame. Upper 40% is dark empty space with subtle gold particles.

TEXT PLACEMENT:
- Top-left: LUMIERE (small, bold sans-serif, gold #d4a843, wide spacing)
- CENTER of upper dark empty space (above her head):
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif. Pure white. Large — floating in the darkness above her.
  She looks up toward the text.

{TEXT_PRECISION_GOTHIC}
"""

PATTERN_D1b = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Japanese woman from shoulders up, slightly angled. Chin slightly lifted, confident expression. Golden light from upper-right creates beautiful shadows on her collarbones and neck. Minimal makeup, natural beauty. Background pure black. She occupies the lower-right portion. Upper-left is empty dark space.

TEXT PLACEMENT:
- Bottom-right, small: LUMIERE (bold sans-serif, gold #d4a843)
- Upper-left area (large, floating in dark space):
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif. White. Big and bold.

{TEXT_PRECISION_GOTHIC}
"""

# D2: タッチ — R2で最もテキスト精度が高かった
PATTERN_D2a = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Japanese woman in three-quarter view. Her hand touching her cheek — gentle, deliberate gesture. Fingertips have gold shimmer. Where fingers meet cheek: tiny gold light particles emanate. Rest fades to deep black shadow. Only face, hand, and gold contact point illuminated.

TEXT PLACEMENT:
- Top center: LUMIERE (bold sans-serif, gold #d4a843, medium size, wide spacing)
- Right side, vertically:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif. White. Clean and modern.

{TEXT_PRECISION_GOTHIC}
"""

PATTERN_D2b = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Japanese woman, eyes closed peacefully, both hands gently cupping her own face. Her skin radiates golden warmth from within. Gold dust particles drift upward from where her palms touch her cheeks. Background: absolute black. Only her face and hands are lit.

TEXT PLACEMENT:
- Top: LUMIERE (bold sans-serif, gold, centered, wide spacing)
- Bottom area, centered:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif. White. Large. Anchoring the composition.

{TEXT_PRECISION_GOTHIC}
"""

# C1: プロダクト — ビジュアル完成度が高かった
PATTERN_C1a = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: Sleek minimal black glass skincare bottle with gold cap, center of image. On reflective black obsidian surface. Liquid gold flowing/dripping from above, pooling around base. Gold bokeh particles behind. Cinematic product photography.

TEXT PLACEMENT:
- Top area, centered:
  その肌、まだ目覚めていない。
  ONE LINE. BOLD GOTHIC sans-serif. White. Clean.
- Below main text: LUMIERE (gold #d4a843, bold sans-serif, wide spacing)

{TEXT_PRECISION_GOTHIC}
"""

PATTERN_C1b = f"""
Create a 1080x1080 pixel square luxury skincare advertisement.

{BRAND_DNA}

VISUAL: A luxury skincare dropper bottle — black glass, gold dropper. A single golden drop falling from the dropper tip. The drop catches light brilliantly. Below: reflective black surface. Background: deep black with scattered gold particles. Dramatic spotlight on the bottle.

TEXT PLACEMENT:
- Bottom area, centered:
  Line 1: その肌、
  Line 2: まだ目覚めていない。
  BOLD GOTHIC sans-serif. White. Large.
- Top: LUMIERE (gold, bold sans-serif, centered)

{TEXT_PRECISION_GOTHIC}
"""

# ============================================================
banners = [
    {"prompt": PATTERN_A2a, "filename": "lumiere_A2a_gothic.png"},
    {"prompt": PATTERN_A2b, "filename": "lumiere_A2b_gothic.png"},
    {"prompt": PATTERN_D1a, "filename": "lumiere_D1a_gothic.png"},
    {"prompt": PATTERN_D1b, "filename": "lumiere_D1b_gothic.png"},
    {"prompt": PATTERN_D2a, "filename": "lumiere_D2a_gothic.png"},
    {"prompt": PATTERN_D2b, "filename": "lumiere_D2b_gothic.png"},
    {"prompt": PATTERN_C1a, "filename": "lumiere_C1a_gothic.png"},
    {"prompt": PATTERN_C1b, "filename": "lumiere_C1b_gothic.png"},
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    concepts = {
        "A2a": ("Close-up — Awakening (Gothic)", "目覚めの瞬間 × ゴシック体テスト"),
        "A2b": ("Close-up — Split Light (Gothic)", "スプリットライティング × ゴシック体"),
        "D1a": ("Editorial — Gaze Up (Gothic)", "見上げる構図 × 余白テキスト × ゴシック"),
        "D1b": ("Editorial — Confident (Gothic)", "自信の表情 × 左上テキスト × ゴシック"),
        "D2a": ("Touch — Side (Gothic)", "肌に触れるジェスチャー × ゴシック"),
        "D2b": ("Touch — Eyes Closed (Gothic)", "瞑想的な美 × 両手 × ゴシック"),
        "C1a": ("Product — Gold Flow (Gothic)", "液体ゴールド × プロダクト × ゴシック"),
        "C1b": ("Product — Dropper (Gothic)", "ドロッパーボトル × 一滴の金 × ゴシック"),
    }

    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.replace("lumiere_", "").replace("_gothic.png", "")
            concept_name, concept_desc = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_01_lumiere_r3/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{concept_name}</div>
                    <div class="card-desc">{concept_desc}</div>
                </div>
            </div>
            """

    # R2比較
    r2_cards = ""
    r2_dir = BASE_DIR / "banners_01_lumiere_r2"
    if r2_dir.exists():
        for name in ["lumiere_A2_eyes.png", "lumiere_D1_editorial.png", "lumiere_D2_touch.png", "lumiere_C1_product.png"]:
            p = r2_dir / name
            if p.exists():
                key = name.replace("lumiere_", "").replace(".png", "")
                r2_cards += f"""
                <div class="card r2">
                    <div class="card-img-wrap">
                        <img src="banners_01_lumiere_r2/{name}" alt="{name}" onclick="openZoom(this.src)">
                    </div>
                    <div class="card-info">
                        <div class="card-label">R2 {key} (明朝体)</div>
                    </div>
                </div>
                """

    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>LUMIERE R3 — Gothic Font Test</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;700&family=Noto+Sans+JP:wght@300;400;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d0906;color:#e0d8cc;font-family:'Noto Sans JP',sans-serif;font-weight:300;}}
.hero{{padding:80px 40px 60px;text-align:center;}}
.hero-brand{{font-family:'Cormorant Garamond',serif;font-size:64px;font-weight:700;letter-spacing:16px;color:#d4a843;}}
.hero-sub{{font-size:11px;letter-spacing:6px;color:#665a45;margin-top:12px;}}
.hero-copy{{font-size:22px;color:#fff;margin-top:28px;letter-spacing:2px;}}
.hero-divider{{width:60px;height:1px;background:#d4a843;margin:24px auto 0;}}
.hero-hypothesis{{max-width:600px;margin:20px auto 0;padding:16px 24px;border:1px solid #d4a84333;border-radius:8px;font-size:12px;color:#888;line-height:1.8;}}
.hero-hypothesis strong{{color:#d4a843;}}
.gallery{{max-width:1200px;margin:0 auto;padding:40px 24px 80px;}}
.section-title{{font-family:'Cormorant Garamond',serif;font-size:20px;color:#d4a843;letter-spacing:4px;margin-bottom:24px;padding-bottom:8px;border-bottom:1px solid #1a1810;}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:24px;margin-bottom:48px;}}
.card{{background:#111008;border-radius:12px;overflow:hidden;border:1px solid #1a1810;transition:transform 0.2s,box-shadow 0.2s;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 8px 32px rgba(212,168,67,0.1);}}
.card.r2{{border-color:#2a2010;opacity:0.6;}}.card.r2:hover{{opacity:1;}}
.card-img-wrap{{aspect-ratio:1;overflow:hidden;background:#0a0806;}}
.card-img-wrap img{{width:100%;height:100%;object-fit:cover;cursor:zoom-in;transition:transform 0.3s;}}
.card-img-wrap img:hover{{transform:scale(1.02);}}
.card-info{{padding:16px 20px;}}
.card-label{{font-family:'Cormorant Garamond',serif;font-size:12px;color:#d4a843;letter-spacing:4px;font-weight:600;margin-bottom:4px;}}
.card-title{{font-size:14px;color:#fff;margin-bottom:6px;}}
.card-desc{{font-size:11px;color:#665a45;line-height:1.6;}}
.zoom-overlay{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);z-index:1000;cursor:zoom-out;justify-content:center;align-items:center;}}
.zoom-overlay.active{{display:flex;}}
.zoom-overlay img{{max-width:90%;max-height:90%;border-radius:8px;box-shadow:0 0 60px rgba(212,168,67,0.2);}}
.footer{{text-align:center;padding:32px;font-size:9px;letter-spacing:4px;color:#333;border-top:1px solid #1a1810;}}
@media(max-width:768px){{.grid{{grid-template-columns:1fr;}}.hero-brand{{font-size:36px;}}}}
</style></head><body>
<div class="hero">
  <div class="hero-brand">LUMIERE</div>
  <div class="hero-sub">R3 — Gothic Font Hypothesis Test</div>
  <div class="hero-copy">「その肌、まだ目覚めていない。」</div>
  <div class="hero-divider"></div>
  <div class="hero-hypothesis">
    <strong>仮説:</strong> 明朝体（セリフ）のはね・はらい・太さ変化がAI画像生成のテキスト精度を下げている<br>
    <strong>検証:</strong> ゴシック体（ボールドサンセリフ）に変更して同じ構図で再生成
  </div>
</div>
<div class="gallery">
  <div class="section-title">R3 — GOTHIC SANS-SERIF</div>
  <div class="grid">{cards_html}</div>
  {"<div class='section-title'>COMPARE: R2 MINCHO (SERIF)</div><div class='grid'>" + r2_cards + "</div>" if r2_cards else ""}
</div>
<div class="zoom-overlay" id="zoomOverlay" onclick="closeZoom()"><img id="zoomImg" src="" alt="zoom"></div>
<div class="footer">LUMIERE R3 GOTHIC TEST — {timestamp}</div>
<script>
function openZoom(s){{document.getElementById('zoomImg').src=s;document.getElementById('zoomOverlay').classList.add('active');}}
function closeZoom(){{document.getElementById('zoomOverlay').classList.remove('active');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeZoom();}});
</script></body></html>"""

    gallery_path = BASE_DIR / "gallery_01_lumiere.html"
    with open(gallery_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nGallery: {gallery_path}")
    return str(gallery_path)


if __name__ == "__main__":
    print("=" * 60)
    print("LUMIERE R3 — GOTHIC FONT HYPOTHESIS TEST")
    print("仮説: 明朝体 → ゴシック体でテキスト精度UP？")
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
    success = sum(1 for _, p in results if p)
    for fname, path in results:
        print(f"  [{'OK' if path else 'FAIL'}] {fname}")
    print(f"\n{success}/{len(results)} generated")

    if success > 0:
        gallery = create_gallery(results)
        print(f"Gallery: {gallery}")
    print("=" * 60)

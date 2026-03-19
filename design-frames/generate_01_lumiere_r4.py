#!/usr/bin/env python3
"""
DESIGN FRAMES 01: LUMIERE R4 — 参照画像テスト
仮説: テキスト精度が高い画像を参照として渡すとテキスト品質が上がる

R3のD2b（最もテキスト精度が高かった）を参照画像として全パターンに渡す
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
OUT = BASE_DIR / "banners_01_lumiere_r4"
OUT.mkdir(exist_ok=True)

# 参照画像: R3で最もテキスト精度が高かったD2b
REF_IMAGE = str(BASE_DIR / "banners_01_lumiere_r3" / "lumiere_D2b_gothic.png")


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
# 参照画像指示
# ============================================================
REF_INSTRUCTION = """[TEXT QUALITY REFERENCE — MATCH THIS LEVEL]
This reference image shows the CORRECT Japanese text rendering quality.
The text reads: その肌、まだ目覚めていない。
Study how each character is perfectly formed:
- その = hiragana so + no
- 肌 = kanji for skin (月 + 几)
- まだ = hiragana ma + da
- 目覚めていない = me + kaku(awaken) + me + te + i + na + i
- LUMIERE = English brand name

Your generated image MUST match this text quality:
- Same character accuracy
- Same crisp, clean rendering
- Same readable Japanese text
The VISUAL DESIGN will be different — but the TEXT QUALITY must be equal or better.
"""


BRAND_DNA = """
BRAND: LUMIERE — Luxury Skincare D2C
Colors: ONLY black (#0d0906), charcoal (#1a1a1a), gold (#d4a843), soft gold (#f5d78e), white
PHOTOREALISTIC cinematic quality. Real Japanese woman, late 20s-30s. Flawless skin.
Mood: Quiet luxury. VOGUE advertisement quality.
"""

TEXT_RULES = """
TEXT REQUIREMENTS:
- ONLY 2 text elements in the entire image:
  1. LUMIERE (English, bold sans-serif)
  2. その肌、まだ目覚めていない。(Japanese, bold gothic/sans-serif)
- Match the text quality of the reference image EXACTLY
- Every character must be perfectly formed
- NO other text, NO watermarks, NO captions
"""

# ============================================================
# 8 Patterns with reference image
# ============================================================

P_A1 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Extreme close-up of Japanese woman's face — cheekbone to eyebrow. Skin lit by golden sidelight. Gold particles floating. Dramatic chiaroscuro. Left 40% darker for text.

TEXT: Top-left "LUMIERE" gold. Center-left over dark area, two lines:
その肌、
まだ目覚めていない。
White, bold sans-serif. Large.

{TEXT_RULES}
"""

P_A2 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Close-up Japanese woman, eyes just opening. Golden light from right. Skin glows. Gold dust particles. Bottom-left area darker.

TEXT: Top-right "LUMIERE" gold. Bottom-left:
その肌、
まだ目覚めていない。
White, bold sans-serif. Large.

{TEXT_RULES}
"""

P_B1 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Pure black background. Woman's side-profile silhouette made of gold dust particles. Particles trace jawline, nose, hair. Some drift into darkness. Silhouette on right side.

TEXT: Top-center "LUMIERE" gold small. Center-left area:
その肌、
まだ目覚めていない。
White, bold sans-serif. Large — a major visual element.

{TEXT_RULES}
"""

P_B2 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Pure black background. Woman's face made of thousands of gold particles — a point cloud face. Features visible but ethereal. Face center-right.

TEXT: Top-left "LUMIERE" gold. Left side:
その肌、
まだ目覚めていない。
White, bold sans-serif.

{TEXT_RULES}
"""

P_C1 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Sleek black glass skincare bottle, gold cap. On reflective black surface. Liquid gold flowing from above, pooling around base. Gold bokeh behind.

TEXT: Top area centered:
その肌、まだ目覚めていない。
White, bold sans-serif. One line.
Below: "LUMIERE" gold, centered.

{TEXT_RULES}
"""

P_C2 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Split — LEFT: Japanese woman's profile, golden skin. RIGHT: Black skincare bottle with gold accents. CENTER: Gold particle thread connecting them.

TEXT: Top-center "LUMIERE" gold. Bottom spanning full width:
その肌、まだ目覚めていない。
White, bold sans-serif.

{TEXT_RULES}
"""

P_D1 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Japanese woman from shoulders up looking directly at viewer. Perfect skin, golden light from above. Hair pulled back. She's in lower 60%. Upper 40% is dark empty space with subtle gold particles.

TEXT: Top-left "LUMIERE" gold small. Center of upper dark space:
その肌、
まだ目覚めていない。
White, bold sans-serif. Large. Floating above her.

{TEXT_RULES}
"""

P_D2 = f"""
Create a 1080x1080 luxury skincare ad. {BRAND_DNA}

VISUAL: Japanese woman touching her cheek with one hand. Gold shimmer on fingertips. Gold particles emanate from contact point. Deep black shadows. Only face and hand illuminated.

TEXT: Top "LUMIERE" gold centered. Right side:
その肌、
まだ目覚めていない。
White, bold sans-serif.

{TEXT_RULES}
"""

# ============================================================
# 生成リスト — 全バナーに参照画像を付与
# ============================================================
banners = [
    {"prompt": P_A1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_A1_ref.png"},
    {"prompt": P_A2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_A2_ref.png"},
    {"prompt": P_B1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_B1_ref.png"},
    {"prompt": P_B2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_B2_ref.png"},
    {"prompt": P_C1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_C1_ref.png"},
    {"prompt": P_C2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_C2_ref.png"},
    {"prompt": P_D1, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_D1_ref.png"},
    {"prompt": P_D2, "refs": [(REF_IMAGE, REF_INSTRUCTION)], "filename": "lumiere_D2_ref.png"},
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    concepts = {
        "A1": ("Close-up — Golden Awakening", "クローズアップ + 参照画像テスト"),
        "A2": ("Close-up — Eyes Opening", "目覚め + 参照画像テスト"),
        "B1": ("Silhouette — Gold Dust", "シルエット + 参照画像テスト"),
        "B2": ("Particle Face", "パーティクル + 参照画像テスト"),
        "C1": ("Product Hero", "プロダクト + 参照画像テスト"),
        "C2": ("Product + Model Split", "スプリット + 参照画像テスト"),
        "D1": ("Editorial — The Gaze", "エディトリアル + 参照画像テスト"),
        "D2": ("Editorial — Touch", "タッチ + 参照画像テスト"),
    }

    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]
            cn, cd = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_01_lumiere_r4/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{cn}</div>
                    <div class="card-desc">{cd}</div>
                </div>
            </div>"""

    # Reference image card
    ref_card = f"""
    <div class="card ref">
        <div class="card-img-wrap">
            <img src="banners_01_lumiere_r3/lumiere_D2b_gothic.png" alt="reference" onclick="openZoom(this.src)">
        </div>
        <div class="card-info">
            <div class="card-label">REF</div>
            <div class="card-title">R3 D2b — 参照画像として使用</div>
            <div class="card-desc">テキスト精度が最も高かった画像を全パターンの参照として使用</div>
        </div>
    </div>"""

    # R3 comparison
    r3_cards = ""
    r3_dir = BASE_DIR / "banners_01_lumiere_r3"
    if r3_dir.exists():
        for f in sorted(r3_dir.glob("*.png")):
            key = f.stem.split("_")[1]
            r3_cards += f"""
            <div class="card prev">
                <div class="card-img-wrap"><img src="banners_01_lumiere_r3/{f.name}" onclick="openZoom(this.src)"></div>
                <div class="card-info"><div class="card-label">R3 {key}</div></div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>LUMIERE R4 — Reference Image Test</title>
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
.card.ref{{border-color:#d4a84366;}}
.card.prev{{border-color:#2a2010;opacity:0.6;}}.card.prev:hover{{opacity:1;}}
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
  <div class="hero-sub">R4 — Reference Image Hypothesis Test</div>
  <div class="hero-copy">「その肌、まだ目覚めていない。」</div>
  <div class="hero-divider"></div>
  <div class="hero-hypothesis">
    <strong>仮説:</strong> テキスト精度が高い画像を参照として渡すと、AIが正確なテキスト描画を学んで他のパターンでも精度が上がる<br>
    <strong>参照画像:</strong> R3 D2b（テキスト精度◎）を全パターンに参照として添付
  </div>
</div>
<div class="gallery">
  <div class="section-title">REFERENCE IMAGE USED</div>
  <div class="grid">{ref_card}</div>

  <div class="section-title">R4 — WITH REFERENCE IMAGE</div>
  <div class="grid">{cards_html}</div>

  {"<div class='section-title'>COMPARE: R3 (NO REFERENCE)</div><div class='grid'>" + r3_cards + "</div>" if r3_cards else ""}
</div>
<div class="zoom-overlay" id="zoomOverlay" onclick="closeZoom()"><img id="zoomImg" src="" alt="zoom"></div>
<div class="footer">LUMIERE R4 REF TEST — {timestamp}</div>
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
    print("LUMIERE R4 — REFERENCE IMAGE TEST")
    print(f"参照画像: {REF_IMAGE}")
    print("=" * 60)

    if not os.path.exists(REF_IMAGE):
        print(f"ERROR: Reference image not found: {REF_IMAGE}")
        sys.exit(1)

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

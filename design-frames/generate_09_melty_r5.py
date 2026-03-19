#!/usr/bin/env python3
"""
DESIGN FRAMES 09: MELTY R5
Gemini KV（テキストなし）生成 → Pillow正確テキストオーバーレイ
フォント: ヒラギノ丸ゴ ProN W4（丸ゴシック = MELTYの世界観にピッタリ）
"""
import requests, json, time, os, base64, sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    import subprocess
    result = subprocess.run(["bash", "-c", "source ~/.zshrc && echo $GOOGLE_API_KEY"], capture_output=True, text=True)
    API_KEY = result.stdout.strip()

if not API_KEY:
    print("GOOGLE_API_KEY not found"); sys.exit(1)

BASE_DIR = Path(__file__).parent
OUT = BASE_DIR / "banners_09_melty_r5"
OUT.mkdir(exist_ok=True)

# Fonts
FONT_MARU = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
FONT_KAKU_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_KAKU_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_KAKU_W8 = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"


def generate_kv(prompt, filename, retries=3):
    """Gemini API でテキストなしKV画像を生成"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    for attempt in range(retries + 1):
        try:
            print(f"  Generating KV: {filename} (attempt {attempt+1})")
            r = requests.post(url, json=payload, timeout=180)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait); continue
            if r.status_code == 503:
                time.sleep(20 * (attempt + 1)); continue
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
                        print(f"  KV saved: {filename} ({len(img)/1024:.0f}KB)")
                        return str(out_path)
            if attempt < retries: time.sleep(10); continue
            return None
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries: time.sleep(15); continue
            return None
    return None


def add_text_overlay(kv_path, output_path, layout):
    """Pillowでテキストオーバーレイ"""
    img = Image.open(kv_path).convert("RGBA")
    w, h = img.size

    # テキストレイヤー
    txt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    for element in layout:
        text = element["text"]
        font_path = element.get("font", FONT_MARU)
        size = element.get("size", 48)
        color = element.get("color", (90, 62, 54, 255))  # warm brown
        pos = element.get("pos", (w // 2, h // 2))
        anchor = element.get("anchor", "mm")
        shadow = element.get("shadow", None)
        outline = element.get("outline", None)

        try:
            font = ImageFont.truetype(font_path, size)
        except:
            font = ImageFont.truetype(FONT_KAKU_W6, size)

        x, y = pos

        # Shadow
        if shadow:
            s_offset = shadow.get("offset", (3, 3))
            s_color = shadow.get("color", (0, 0, 0, 60))
            s_blur = shadow.get("blur", 0)
            draw.text((x + s_offset[0], y + s_offset[1]), text, font=font, fill=s_color, anchor=anchor)

        # Outline (stroke)
        if outline:
            o_width = outline.get("width", 2)
            o_color = outline.get("color", (255, 255, 255, 200))
            draw.text((x, y), text, font=font, fill=o_color, anchor=anchor,
                      stroke_width=o_width, stroke_fill=o_color)

        # Main text
        draw.text((x, y), text, font=font, fill=color, anchor=anchor)

    result = Image.alpha_composite(img, txt_layer)
    result = result.convert("RGB")
    result.save(output_path, quality=95)
    print(f"  Overlay done: {Path(output_path).name}")
    return output_path


# ============================================================
# KVプロンプト（テキストなし = ビジュアル全振り）
# ============================================================

BRAND_VISUAL = """
BRAND: MELTY — Luxury monthly sweets subscription
Colors: Warm pink, peach, cream, touches of gold
Mood: Dreamy, warm, indulgent, feminine, sophisticated
Light: Soft, diffused, warm golden-hour quality

ABSOLUTELY NO TEXT IN THE IMAGE.
No letters, no words, no brand name, no watermarks, no captions.
The image must be purely visual — a clean canvas for text overlay later.
"""

KV_PROMPTS = [
    {
        "filename_kv": "kv_A1_flatlay.png",
        "filename_final": "melty_A1_flatlay.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — LUXURIOUS FLAT LAY:
Bird's eye view of artisan sweets on white marble surface.
Pastel macarons (pink, lavender, mint, peach) arranged in a loose circle.
Chocolate bonbons with gold leaf. Strawberry tart slice. Fresh raspberries.
Rose petals scattered. Gold leaf flakes catching light.
Linen napkin in corner. A few pistachio crumbs.
CENTER of frame is mostly CLEAR (for text overlay later).
Warm, soft, dreamy overhead lighting. Professional food photography.
""",
        "layout": [
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 36, "color": (180, 110, 90, 255),
             "pos": ("center", 80), "anchor": "mt",
             "shadow": {"offset": (1, 1), "color": (255, 255, 255, 120)}},
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 56, "color": (90, 62, 54, 255),
             "pos": ("center", -60), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (255, 255, 255, 160)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 56, "color": (255, 120, 140, 255),
             "pos": ("center", 20), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (255, 255, 255, 160)}},
        ]
    },
    {
        "filename_kv": "kv_A2_chocolate.png",
        "filename_final": "melty_A2_chocolate.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — LIQUID CHOCOLATE POUR:
Extreme close-up of glossy melted chocolate being poured over cream puffs.
Rich, viscous chocolate catching warm light. Glistening surface.
Steam or warmth visible. Below: golden profiteroles drowning in chocolate.
Background: warm out-of-focus bokeh in pink and gold tones.
BOTTOM 30% of frame should be dark chocolate area (for text contrast).
Professional food photography, warm color grading.
""",
        "layout": [
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 32, "color": (255, 220, 180, 255),
             "pos": (80, 60), "anchor": "lt"},
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 52, "color": (255, 250, 240, 255),
             "pos": ("center", 100), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (40, 20, 10, 120)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 52, "color": (255, 200, 180, 255),
             "pos": ("center", 60), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (40, 20, 10, 120)}},
        ]
    },
    {
        "filename_kv": "kv_B2_giftbox.png",
        "filename_final": "melty_B2_giftbox.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — THE UNBOXING MOMENT:
Overhead shot: feminine hands with pastel pink nails opening a pink gift box.
Box lid half-open revealing perfectly arranged artisan chocolates and petit fours.
Tissue paper peeking out. Satin ribbon. A small gold card inside the box.
Rose petals scattered on the cream-colored table surface.
Warm afternoon sunlight from the side. Shallow depth of field.
BOTTOM 25% should be relatively clear (cream table surface for text).
""",
        "layout": [
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 28, "color": (200, 130, 110, 220),
             "pos": ("center", 40), "anchor": "mt"},
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 48, "color": (90, 62, 54, 255),
             "pos": ("center", 80), "anchor": "mm",
             "shadow": {"offset": (1, 1), "color": (255, 240, 230, 180)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 48, "color": (255, 120, 140, 255),
             "pos": ("center", 40), "anchor": "mm",
             "shadow": {"offset": (1, 1), "color": (255, 240, 230, 180)}},
        ]
    },
    {
        "filename_kv": "kv_C1_woman.png",
        "filename_final": "melty_C1_woman.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — BLISS PORTRAIT:
Close-up portrait of a beautiful Japanese woman (mid-20s).
She holds a pink macaron near her lips, about to bite. Eyes half-closed, gentle smile.
Soft warm lighting wrapping her face. Creamy bokeh background.
Cream/beige knit sweater. Pastel pink nails.
PHOTOREALISTIC — professional beauty advertisement quality.
Warm pink color grading. LOWER 30% should have space for text.
""",
        "layout": [
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 36, "color": (160, 100, 80, 255),
             "pos": ("center", 60), "anchor": "mt"},
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 50, "color": (90, 62, 54, 255),
             "pos": ("center", 80), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (255, 255, 255, 180)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 50, "color": (255, 120, 140, 255),
             "pos": ("center", 40), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (255, 255, 255, 180)}},
        ]
    },
    {
        "filename_kv": "kv_D1_minimal.png",
        "filename_final": "melty_D1_minimal.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — ONE PERFECT MACARON:
Single perfect pink macaron on a clean soft pink surface.
Shot like a fashion editorial — elegant, dramatic but soft lighting.
The macaron sits in the LOWER-RIGHT area of the frame (small in frame).
MASSIVE negative space — upper-left and center are EMPTY pink/cream gradient.
Incredible detail: smooth shell, visible feet, cream filling peeking out.
A few artful crumbs. Maybe one gold leaf flake.
Soft, elegant shadow. Clean, sophisticated, magazine-worthy minimalism.
""",
        "layout": [
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 64, "color": (80, 55, 45, 255),
             "pos": ("center", -100), "anchor": "mm"},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 64, "color": (80, 55, 45, 255),
             "pos": ("center", -20), "anchor": "mm"},
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 28, "color": (160, 110, 90, 220),
             "pos": (-60, -40), "anchor": "rb"},
        ]
    },
    {
        "filename_kv": "kv_B1_macaron.png",
        "filename_final": "melty_B1_macaron.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — MACARON RAINBOW CASCADE:
Macarons cascading diagonally from upper-left to lower-right like a waterfall.
Each row a different pastel: pink, peach, lavender, mint, cream.
Some split open showing colorful ganache filling.
Gold leaf and sugar crystals sparkling. Soft pink gradient background.
The composition has diagonal ENERGY and FLOW.
UPPER-RIGHT corner should have space for text overlay.
""",
        "layout": [
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 30, "color": (180, 110, 90, 255),
             "pos": (80, 80), "anchor": "lt"},
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 48, "color": (90, 62, 54, 255),
             "pos": (-120, -180), "anchor": "rm",
             "shadow": {"offset": (1, 1), "color": (255, 240, 235, 200)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 44, "color": (255, 120, 140, 255),
             "pos": (-120, -120), "anchor": "rm",
             "shadow": {"offset": (1, 1), "color": (255, 240, 235, 200)}},
        ]
    },
    {
        "filename_kv": "kv_C2_cozy.png",
        "filename_final": "melty_C2_cozy.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — GOLDEN HOUR COZY:
Dreamy kitchen scene bathed in golden hour light.
Woman's hands piping cream onto a small tart on a wooden cutting board.
Flour dusted on marble counter. Fresh strawberries in ceramic bowl.
Cup of tea steaming. A pink subscription box open with sweets visible.
Fairy lights blurred in background. Everything has WARM golden glow.
Shot with shallow depth of field. Professional, editorial quality.
UPPER area should have some soft bokeh space for text.
""",
        "layout": [
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 46, "color": (255, 250, 240, 255),
             "pos": ("center", -180), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (60, 40, 30, 140)},
             "outline": {"width": 1, "color": (255, 255, 255, 80)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 46, "color": (255, 240, 220, 255),
             "pos": ("center", -120), "anchor": "mm",
             "shadow": {"offset": (2, 2), "color": (60, 40, 30, 140)}},
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 24, "color": (255, 240, 220, 200),
             "pos": (-60, -40), "anchor": "rb"},
        ]
    },
    {
        "filename_kv": "kv_D2_strawberry.png",
        "filename_final": "melty_D2_strawberry.png",
        "prompt": f"""Create a stunning 1080x1080 pixel square photograph.

{BRAND_VISUAL}

VISUAL — STRAWBERRY FANTASY:
Spectacular strawberry tart being assembled — a fresh strawberry being placed on top.
Whipped cream, golden pastry layers. Powdered sugar floating in warm light.
More berries and fruit scattered artfully. Professional patisserie setting.
Soft peach/pink bokeh background with warm afternoon light.
SHARP, delicious food photography at its finest.
TOP 30% should be soft bokeh area for text placement.
""",
        "layout": [
            {"text": "MELTY", "font": FONT_KAKU_W3, "size": 34, "color": (180, 100, 80, 255),
             "pos": ("center", 50), "anchor": "mt"},
            {"text": "がんばった日は、", "font": FONT_MARU, "size": 50, "color": (90, 62, 54, 255),
             "pos": ("center", -180), "anchor": "mm",
             "shadow": {"offset": (1, 1), "color": (255, 240, 230, 160)}},
            {"text": "もうひとつ食べていい。", "font": FONT_MARU, "size": 50, "color": (255, 120, 140, 255),
             "pos": ("center", -120), "anchor": "mm",
             "shadow": {"offset": (1, 1), "color": (255, 240, 230, 160)}},
        ]
    },
]


def resolve_pos(pos, img_w, img_h):
    """Resolve position tuples with 'center' and negative values"""
    x, y = pos
    if x == "center":
        x = img_w // 2
    elif x < 0:
        x = img_w + x
    if y == "center":
        y = img_h // 2
    elif y < 0:
        y = img_h + y
    return (x, y)


def add_text_overlay(kv_path, output_path, layout):
    img = Image.open(kv_path).convert("RGBA")
    w, h = img.size
    txt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)

    for element in layout:
        text = element["text"]
        font_path = element.get("font", FONT_MARU)
        size = element.get("size", 48)
        color = element.get("color", (90, 62, 54, 255))
        pos = resolve_pos(element.get("pos", ("center", "center")), w, h)
        anchor = element.get("anchor", "mm")
        shadow = element.get("shadow", None)
        outline = element.get("outline", None)

        try:
            font = ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"  Font error: {e}, falling back")
            font = ImageFont.truetype(FONT_KAKU_W6, size)

        x, y = pos

        if shadow:
            s_off = shadow.get("offset", (2, 2))
            s_col = shadow.get("color", (0, 0, 0, 60))
            draw.text((x + s_off[0], y + s_off[1]), text, font=font, fill=s_col, anchor=anchor)

        if outline:
            o_w = outline.get("width", 2)
            o_c = outline.get("color", (255, 255, 255, 200))
            draw.text((x, y), text, font=font, fill=color, anchor=anchor,
                      stroke_width=o_w, stroke_fill=o_c)
        else:
            draw.text((x, y), text, font=font, fill=color, anchor=anchor)

    result = Image.alpha_composite(img, txt_layer)
    result = result.convert("RGB")
    result.save(output_path, quality=95)
    print(f"  Final: {Path(output_path).name}")
    return str(output_path)


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    concepts = {
        "A1": ("Luxurious Flat Lay", "マカロン×チョコ×花びら。宝箱のよう。"),
        "A2": ("Liquid Chocolate", "とろけるチョコの至福。"),
        "B1": ("Macaron Cascade", "マカロンの虹が流れる。"),
        "B2": ("The Unboxing", "自分へのご褒美を開ける瞬間。"),
        "C1": ("Bliss Portrait", "至福の一口前。"),
        "C2": ("Golden Hour Kitchen", "日曜午後のゴールデンアワー。"),
        "D1": ("One Perfect Macaron", "ミニマル×エディトリアル。テキスト主役。"),
        "D2": ("Strawberry Fantasy", "いちごの傑作完成の瞬間。"),
    }
    cards_html = ""
    for fname, path in results:
        if path:
            key = fname.split("_")[1]
            cn, cd = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_09_melty_r5/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{cn}</div>
                    <div class="card-desc">{cd}</div>
                </div>
            </div>"""
    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>MELTY R5 (KV + Pillow)</title>
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
  <div class="meta"><span class="badge">R5</span><span class="badge">KV + Pillow Overlay</span><span class="badge">100% Accurate Text</span></div>
</div>
<div class="grid">{cards_html}</div>
<div class="zoom-overlay" id="zo" onclick="closeZoom()"><img id="zi" src=""></div>
<div class="footer">DESIGN FRAMES 09 MELTY R5 — {timestamp}</div>
<script>
function openZoom(s){{document.getElementById('zi').src=s;document.getElementById('zo').classList.add('active');}}
function closeZoom(){{document.getElementById('zo').classList.remove('active');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeZoom();}});
</script></body></html>"""
    p = BASE_DIR / "gallery_09_melty_r5.html"
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return str(p)


if __name__ == "__main__":
    print("=" * 60)
    print("MELTY R5 — KV + Pillow Overlay")
    print("=" * 60)

    results = []
    for i, item in enumerate(KV_PROMPTS):
        print(f"\n[{i+1}/{len(KV_PROMPTS)}] {item['filename_final']}")

        # Step 1: Generate KV (no text)
        kv_path = generate_kv(item["prompt"], item["filename_kv"])
        if not kv_path:
            results.append((item["filename_final"], None))
            time.sleep(15)
            continue

        time.sleep(2)

        # Step 2: Add text overlay
        final_path = str(OUT / item["filename_final"])
        try:
            add_text_overlay(kv_path, final_path, item["layout"])
            results.append((item["filename_final"], final_path))
        except Exception as e:
            print(f"  Overlay error: {e}")
            results.append((item["filename_final"], None))

        time.sleep(8)

    print("\n" + "=" * 60)
    ok = sum(1 for _, p in results if p)
    for f, p in results:
        print(f"  [{'OK' if p else 'FAIL'}] {f}")
    print(f"\n{ok}/{len(results)} generated")
    if ok > 0:
        g = create_gallery(results)
        print(f"Gallery: {g}")
    print("=" * 60)

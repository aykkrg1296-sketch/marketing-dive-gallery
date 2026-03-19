#!/usr/bin/env python3
"""
DESIGN FRAMES 01: LUMIERE v2 — KV生成 + Pillowテキストオーバーレイ
テキストはAI任せにしない。プログラマティックに100%正確に載せる。

Step 1: Gemini APIでKV背景（テキストなし）を生成
Step 2: Pillowで日本語テキストを正確にオーバーレイ
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
    print("GOOGLE_API_KEY not found")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
KV_DIR = BASE_DIR / "kv_01_lumiere"
OUT = BASE_DIR / "banners_01_lumiere_v2"
KV_DIR.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

# ============================================================
# フォント定義
# ============================================================
FONT_GOTHIC_W9 = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"
FONT_GOTHIC_W6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_GOTHIC_W3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_GOTHIC_W1 = "/System/Library/Fonts/ヒラギノ角ゴシック W1.ttc"
FONT_MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
FONT_DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
FONT_FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
FONT_BODONI = "/System/Library/Fonts/Supplemental/Bodoni 72.ttc"


def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception as e:
        print(f"  Font load error: {path} index={index}: {e}")
        return ImageFont.truetype(path, size)


# ============================================================
# Gemini API — KV画像生成（テキストなし）
# ============================================================
def generate_kv(prompt, filename, retries=3):
    parts = [{"text": prompt}]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }

    for attempt in range(retries + 1):
        try:
            print(f"\n  Generating KV: {filename} (attempt {attempt+1}/{retries+1})")
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
                        out_path = KV_DIR / filename
                        with open(out_path, "wb") as f:
                            f.write(img)
                        size_kb = len(img) / 1024
                        print(f"  KV Done: {out_path.name} ({size_kb:.0f}KB)")
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
# テキストオーバーレイ共通関数
# ============================================================
def draw_text_with_shadow(draw, xy, text, font, fill, shadow_color=(0,0,0,160), shadow_offset=3, shadow_blur=None):
    """テキスト + シャドウ描画"""
    x, y = xy
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)


def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def add_dark_gradient(img, direction="bottom", opacity=0.5, height_ratio=0.5):
    """画像の指定方向に暗いグラデーションを追加"""
    w, h = img.size
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    grad_h = int(h * height_ratio)
    if direction == "bottom":
        for i in range(grad_h):
            progress = i / grad_h
            alpha = int(255 * opacity * progress)
            y = h - grad_h + i
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    elif direction == "top":
        for i in range(grad_h):
            progress = 1 - (i / grad_h)
            alpha = int(255 * opacity * progress)
            draw.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))
    elif direction == "left":
        grad_w = int(w * height_ratio)
        for i in range(grad_w):
            progress = 1 - (i / grad_w)
            alpha = int(255 * opacity * progress)
            draw.line([(i, 0), (i, h)], fill=(0, 0, 0, alpha))
    elif direction == "full":
        for i in range(h):
            alpha = int(255 * opacity * 0.6)
            draw.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img.convert('RGBA'), overlay)


# ============================================================
# KVプロンプト（テキストなし）
# ============================================================
NO_TEXT_RULE = "\n\nCRITICAL: Generate the image with ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO NUMBERS, NO LOGOS, NO WATERMARKS. Pure visual only. The image must contain ZERO text of any kind."

BRAND_VISUAL = """
VISUAL IDENTITY for LUMIERE (luxury skincare brand):
- Color palette STRICTLY: Deep black (#0d0906), charcoal (#1a1a1a), rich gold (#d4a843), soft gold (#f5d78e), pure white
- NO other colors. No pink, no blue, no green. ONLY black/gold/white spectrum.
- Photography: Cinematic, dramatic lighting. Rembrandt or butterfly lighting.
- Mood: Quiet luxury. Not loud. Not flashy. Like a dimly lit private salon.
- PHOTOREALISTIC cinematic quality. NOT anime, NOT illustration.
- The woman should look like a real Japanese woman in her late 20s-early 30s.
- Skin must look FLAWLESS — luminous, dewy, the kind of skin that makes you stare.
"""

KV_A1 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

EXTREME CLOSE-UP of a Japanese woman's face — we see from her cheekbone to just above her eyebrow.
Her skin is the STAR: poreless, luminous, lit from the side with warm golden light.
Tiny gold particles (like gold leaf dust) float across the image, catching light.
Her eye is partially visible — closed or half-closed, with gold eyeshadow shimmer.
The lighting creates a dramatic chiaroscuro: one side of her face lit by gold, the other fading into rich black.
The gold particles look like the skin itself is releasing light.
Like a single frame from a perfume commercial directed by Tom Ford.
Keep the LEFT SIDE (roughly 40%) relatively dark/clear for text placement.
{NO_TEXT_RULE}
"""

KV_A2 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

Close-up of a Japanese woman's face — from chin to forehead.
Her eyes are JUST OPENING — lashes lifting, a sliver of iris visible.
The moment of "awakening" captured in a single frame.
Golden light pours in from the right side as if morning light hitting her face for the first time.
Her skin has an almost supernatural glow — like light is emerging FROM her pores.
Gold dust particles suspended in the air around her face.
Deep black background on the left side, melting into golden light on the right.
The exact moment between sleep and consciousness. Intimate, cinematic, breathtaking.
Keep the BOTTOM-LEFT area relatively dark for text placement.
{NO_TEXT_RULE}
"""

KV_B1 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

Pure BLACK background — deep, velvety, absolute darkness.
A woman's SILHOUETTE (side profile, head and neck) — her outline is defined entirely by GOLD DUST particles.
The gold particles (#d4a843, #f5d78e) trace her jawline, cheekbone, nose bridge, forehead, flowing hair.
Some particles are dense along her skin contour, others drift away into the darkness like she's dissolving into gold.
Inside the silhouette: hints of her actual face visible — just the curve of her lips, the bridge of her nose.
The gold dust is LUMINOUS — it glows against the black like fireflies.
A few larger gold particles float freely in the surrounding darkness.
Museum-quality art piece. The gold dust feels alive — like her beauty is literally radiating.
Position the silhouette slightly to the RIGHT, leaving the center-left area clear for text.
{NO_TEXT_RULE}
"""

KV_B2 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

Pure BLACK background.
A woman's face STRAIGHT ON — but only visible through gold particles.
Thousands of tiny gold particles (#d4a843) form a point cloud of her face — like a 3D scan made of gold dust.
Her features are recognizable but ethereal — you can see her eyes, nose, lips through the particle cloud.
The particles are denser at her key features (eyes, lips) and sparser at the edges.
Some particles stream upward from her head like golden smoke rising.
Her face is MADE of light, of gold, of something otherworldly.
Like looking at a constellation that forms a face. Hauntingly beautiful.
Position her face slightly lower and to the right, leaving the upper-left area for text.
{NO_TEXT_RULE}
"""

KV_C1 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

A sleek, minimal skincare bottle/jar at center — black glass with a gold cap.
The bottle design: minimal, elegant, cylindrical or rectangular with rounded edges. Think Aesop meets Tom Ford.
The bottle is sitting on a reflective black surface (like polished obsidian).
LIQUID GOLD is flowing/dripping from above — viscous, luxurious, catching light.
The gold liquid pools around the base of the bottle on the reflective surface.
Behind the bottle: subtle bokeh of gold light particles in the darkness.
Cinematic product photography quality.
Keep the TOP AREA clear for text placement.
{NO_TEXT_RULE}
"""

KV_C2 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

Split composition:
LEFT 45%: A Japanese woman's face in profile — looking right, chin slightly lifted.
Dramatic Rembrandt lighting from the right. Her skin is absolutely luminous — lit by golden light.
Only her face/neck visible, the rest fades into black.
RIGHT 45%: A sleek black skincare bottle with gold accents, floating or placed on a dark surface.
CENTER: Gold particles connect the woman's face to the product — like a golden thread or bridge of light particles.
High-fashion editorial meets luxury product advertisement.
The split creates a story: SHE is the proof that the product works.
Keep BOTTOM area clear for text.
{NO_TEXT_RULE}
"""

KV_D1 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

A stunning Japanese woman photographed from the shoulders up.
She's looking DIRECTLY at the viewer — confident, calm, magnetic.
Her skin is impossibly perfect — soft golden light from above creates gentle shadows.
Her hair is sleek, dark, pulled back — nothing distracts from her SKIN.
Bare shoulders, collarbones visible.
Background: smooth gradient from deep charcoal (#1a1a1a) to black (#0d0906).
GENEROUS negative space above her — she's positioned in the LOWER 60% of the frame.
The upper 40% is dark empty space. A single subtle trail of gold light particles diagonally across the top.
A full-page ad composition from Japanese VOGUE. Effortlessly luxurious.
{NO_TEXT_RULE}
"""

KV_D2 = f"""
Create a 1080x1080 pixel square image. {BRAND_VISUAL}

A Japanese woman in three-quarter view — elegant, serene.
Her right hand is touching her left cheek — a gentle, deliberate touch.
The gesture draws attention to her SKIN — the way light plays across her fingers and cheek.
Her fingers have a subtle gold shimmer — as if she just touched liquid gold.
Where her fingertips meet her cheek: tiny gold light particles emanate from the contact point.
The rest of her fades into deep black shadow.
Only her face, hand, and the gold contact point are illuminated.
The intimacy of skincare ritual — touching your own face.
Sensual but not sexual. Elegant. Self-care as a sacred act.
Keep the RIGHT SIDE and BOTTOM relatively dark for text.
{NO_TEXT_RULE}
"""


# ============================================================
# テキストオーバーレイ設計
# ============================================================
def overlay_A1(kv_path, out_path):
    """A1: クローズアップ — 左側にテキスト"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))
    img = add_dark_gradient(img, "left", opacity=0.4, height_ratio=0.5)

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-left
    font_brand = load_font(FONT_DIDOT, 28)
    draw_text_with_shadow(draw, (60, 50), "LUMIÈRE", font_brand, fill=(212, 168, 67, 255), shadow_offset=2)

    # メインコピー — 左寄り、縦方向中央
    font_main = load_font(FONT_MINCHO, 52)
    draw_text_with_shadow(draw, (60, 380), "その肌、", font_main, fill=(255, 255, 255, 255), shadow_offset=3)
    draw_text_with_shadow(draw, (60, 450), "まだ目覚めていない。", font_main, fill=(255, 255, 255, 255), shadow_offset=3)

    # サブコピー — bottom-right
    font_sub = load_font(FONT_MINCHO, 22)
    draw_text_with_shadow(draw, (750, 980), "目覚めの、スキンケア。", font_sub, fill=(245, 215, 142, 230), shadow_offset=2)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_A2(kv_path, out_path):
    """A2: 目覚め — 左下にテキスト"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))
    img = add_dark_gradient(img, "bottom", opacity=0.6, height_ratio=0.5)

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-right
    font_brand = load_font(FONT_DIDOT, 26)
    draw_text_with_shadow(draw, (860, 50), "LUMIÈRE", font_brand, fill=(212, 168, 67, 255), shadow_offset=2)

    # メインコピー — 左下
    font_main = load_font(FONT_MINCHO, 56)
    draw_text_with_shadow(draw, (50, 800), "その肌、", font_main, fill=(255, 255, 255, 255), shadow_offset=3)
    font_main2 = load_font(FONT_MINCHO, 48)
    draw_text_with_shadow(draw, (50, 875), "まだ目覚めていない。", font_main2, fill=(255, 255, 255, 255), shadow_offset=3)

    # サブコピー
    font_sub = load_font(FONT_MINCHO, 20)
    draw_text_with_shadow(draw, (50, 950), "目覚めの、スキンケア。", font_sub, fill=(245, 215, 142, 230), shadow_offset=2)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_B1(kv_path, out_path):
    """B1: シルエット — 中央にテキスト、テキストが主役"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-center
    font_brand = load_font(FONT_DIDOT, 24)
    tw, _ = get_text_size(draw, "LUMIÈRE", font_brand)
    draw_text_with_shadow(draw, ((1080 - tw) // 2, 60), "LUMIÈRE", font_brand, fill=(212, 168, 67, 255), shadow_offset=1)

    # メインコピー — center
    font_main = load_font(FONT_MINCHO, 58)
    line1 = "その肌、"
    line2 = "まだ目覚めていない。"
    tw1, _ = get_text_size(draw, line1, font_main)
    tw2, _ = get_text_size(draw, line2, font_main)
    draw_text_with_shadow(draw, ((1080 - tw1) // 2, 440), line1, font_main, fill=(255, 255, 255, 255), shadow_offset=2)
    draw_text_with_shadow(draw, ((1080 - tw2) // 2, 520), line2, font_main, fill=(255, 255, 255, 255), shadow_offset=2)

    # サブコピー — bottom-center
    font_sub = load_font(FONT_DIDOT, 16)
    sub = "AWAKENING SKINCARE"
    tw_sub, _ = get_text_size(draw, sub, font_sub)
    draw_text_with_shadow(draw, ((1080 - tw_sub) // 2, 960), sub, font_sub, fill=(245, 215, 142, 200), shadow_offset=1)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_B2(kv_path, out_path):
    """B2: パーティクル — 左に縦書き風テキスト"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))
    img = add_dark_gradient(img, "left", opacity=0.3, height_ratio=0.4)

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-left
    font_brand = load_font(FONT_DIDOT, 24)
    draw_text_with_shadow(draw, (50, 55), "LUMIÈRE", font_brand, fill=(212, 168, 67, 255), shadow_offset=1)

    # メインコピー — left side, stacked
    font_main = load_font(FONT_MINCHO, 48)
    draw_text_with_shadow(draw, (50, 340), "その肌、", font_main, fill=(255, 255, 255, 255), shadow_offset=2)
    draw_text_with_shadow(draw, (50, 410), "まだ", font_main, fill=(255, 255, 255, 255), shadow_offset=2)
    draw_text_with_shadow(draw, (50, 480), "目覚めていない。", font_main, fill=(255, 255, 255, 255), shadow_offset=2)

    # サブコピー — bottom
    font_sub = load_font(FONT_MINCHO, 20)
    sub = "目覚めの、スキンケア。"
    tw_sub, _ = get_text_size(draw, sub, font_sub)
    draw_text_with_shadow(draw, ((1080 - tw_sub) // 2, 960), sub, font_sub, fill=(245, 215, 142, 200), shadow_offset=1)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_C1(kv_path, out_path):
    """C1: プロダクト — 上部にテキスト"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))
    img = add_dark_gradient(img, "top", opacity=0.4, height_ratio=0.35)

    draw = ImageDraw.Draw(img)

    # メインコピー — 上部、centered
    font_main = load_font(FONT_MINCHO, 48)
    line = "その肌、まだ目覚めていない。"
    tw, _ = get_text_size(draw, line, font_main)
    draw_text_with_shadow(draw, ((1080 - tw) // 2, 80), line, font_main, fill=(255, 255, 255, 255), shadow_offset=3)

    # LUMIERE — center below main copy
    font_brand = load_font(FONT_DIDOT, 32)
    brand = "LUMIÈRE"
    tw_b, _ = get_text_size(draw, brand, font_brand)
    draw_text_with_shadow(draw, ((1080 - tw_b) // 2, 155), brand, font_brand, fill=(212, 168, 67, 255), shadow_offset=2)

    # サブコピー — bottom
    font_sub = load_font(FONT_MINCHO, 22)
    sub = "目覚めの、スキンケア。"
    tw_sub, _ = get_text_size(draw, sub, font_sub)
    draw_text_with_shadow(draw, ((1080 - tw_sub) // 2, 970), sub, font_sub, fill=(245, 215, 142, 230), shadow_offset=2)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_C2(kv_path, out_path):
    """C2: スプリット — テキスト分割配置"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))
    img = add_dark_gradient(img, "bottom", opacity=0.5, height_ratio=0.35)

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-center
    font_brand = load_font(FONT_DIDOT, 28)
    brand = "LUMIÈRE"
    tw_b, _ = get_text_size(draw, brand, font_brand)
    draw_text_with_shadow(draw, ((1080 - tw_b) // 2, 45), brand, font_brand, fill=(212, 168, 67, 255), shadow_offset=2)

    # メインコピー — split across halves
    font_main = load_font(FONT_MINCHO, 46)
    draw_text_with_shadow(draw, (60, 870), "その肌、", font_main, fill=(255, 255, 255, 255), shadow_offset=3)
    draw_text_with_shadow(draw, (540, 870), "まだ目覚めていない。", font_main, fill=(255, 255, 255, 255), shadow_offset=3)

    # サブコピー — very bottom, centered
    font_sub = load_font(FONT_MINCHO, 18)
    sub = "目覚めの、スキンケア。"
    tw_sub, _ = get_text_size(draw, sub, font_sub)
    draw_text_with_shadow(draw, ((1080 - tw_sub) // 2, 950), sub, font_sub, fill=(245, 215, 142, 200), shadow_offset=1)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_D1(kv_path, out_path):
    """D1: エディトリアル — 余白の上に大きくテキスト"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-left
    font_brand = load_font(FONT_DIDOT, 24)
    draw_text_with_shadow(draw, (55, 50), "LUMIÈRE", font_brand, fill=(212, 168, 67, 255), shadow_offset=1)

    # メインコピー — dead center upper area (over negative space)
    font_main = load_font(FONT_MINCHO, 54)
    line1 = "その肌、"
    line2 = "まだ目覚めていない。"
    tw1, _ = get_text_size(draw, line1, font_main)
    tw2, _ = get_text_size(draw, line2, font_main)
    draw_text_with_shadow(draw, ((1080 - tw1) // 2, 240), line1, font_main, fill=(255, 255, 255, 255), shadow_offset=2)
    draw_text_with_shadow(draw, ((1080 - tw2) // 2, 315), line2, font_main, fill=(255, 255, 255, 255), shadow_offset=2)

    # サブコピー — bottom-right
    font_sub = load_font(FONT_MINCHO, 18)
    draw_text_with_shadow(draw, (820, 1010), "目覚めの、スキンケア。", font_sub, fill=(245, 215, 142, 200), shadow_offset=1)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


def overlay_D2(kv_path, out_path):
    """D2: タッチ — 右側にテキスト"""
    img = Image.open(kv_path).convert('RGBA').resize((1080, 1080))
    img = add_dark_gradient(img, "bottom", opacity=0.4, height_ratio=0.35)

    draw = ImageDraw.Draw(img)

    # LUMIERE — top-center
    font_brand = load_font(FONT_DIDOT, 30)
    brand = "LUMIÈRE"
    tw_b, _ = get_text_size(draw, brand, font_brand)
    draw_text_with_shadow(draw, ((1080 - tw_b) // 2, 50), brand, font_brand, fill=(212, 168, 67, 255), shadow_offset=2)

    # メインコピー — right side
    font_main = load_font(FONT_MINCHO, 46)
    draw_text_with_shadow(draw, (580, 750), "その肌、", font_main, fill=(255, 255, 255, 255), shadow_offset=3)
    font_main2 = load_font(FONT_MINCHO, 38)
    draw_text_with_shadow(draw, (580, 820), "まだ目覚めて", font_main2, fill=(255, 255, 255, 255), shadow_offset=3)
    draw_text_with_shadow(draw, (580, 875), "いない。", font_main2, fill=(255, 255, 255, 255), shadow_offset=3)

    # サブコピー — bottom, centered
    font_sub = load_font(FONT_MINCHO, 20)
    sub = "目覚めの、スキンケア。"
    tw_sub, _ = get_text_size(draw, sub, font_sub)
    draw_text_with_shadow(draw, ((1080 - tw_sub) // 2, 980), sub, font_sub, fill=(245, 215, 142, 200), shadow_offset=1)

    img.convert('RGB').save(out_path, quality=95)
    print(f"  Overlay done: {Path(out_path).name}")


# ============================================================
# 生成リスト
# ============================================================
banners = [
    {"kv_prompt": KV_A1, "kv_file": "kv_A1_closeup.png", "out_file": "lumiere_A1_closeup.png", "overlay": overlay_A1},
    {"kv_prompt": KV_A2, "kv_file": "kv_A2_eyes.png", "out_file": "lumiere_A2_eyes.png", "overlay": overlay_A2},
    {"kv_prompt": KV_B1, "kv_file": "kv_B1_silhouette.png", "out_file": "lumiere_B1_silhouette.png", "overlay": overlay_B1},
    {"kv_prompt": KV_B2, "kv_file": "kv_B2_particle.png", "out_file": "lumiere_B2_particle.png", "overlay": overlay_B2},
    {"kv_prompt": KV_C1, "kv_file": "kv_C1_product.png", "out_file": "lumiere_C1_product.png", "overlay": overlay_C1},
    {"kv_prompt": KV_C2, "kv_file": "kv_C2_split.png", "out_file": "lumiere_C2_split.png", "overlay": overlay_C2},
    {"kv_prompt": KV_D1, "kv_file": "kv_D1_editorial.png", "out_file": "lumiere_D1_editorial.png", "overlay": overlay_D1},
    {"kv_prompt": KV_D2, "kv_file": "kv_D2_touch.png", "out_file": "lumiere_D2_touch.png", "overlay": overlay_D2},
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
            key = fname.split("_")[1]
            concept_name, concept_desc = concepts.get(key, (fname, ""))
            cards_html += f"""
            <div class="card">
                <div class="card-img-wrap">
                    <img src="banners_01_lumiere_v2/{fname}" alt="{fname}" onclick="openZoom(this.src)">
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
<title>DESIGN FRAMES 01: LUMIERE v2</title>
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
.palette-strip {{
  display: flex; height: 4px; max-width: 300px; margin: 20px auto 0;
}}
.palette-strip .sw {{ flex: 1; }}

.gallery {{
  max-width: 1200px; margin: 0 auto; padding: 40px 24px 80px;
}}
.section-note {{
  text-align: center; font-size: 12px; color: #665a45; margin-bottom: 32px;
  letter-spacing: 1px;
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
  <div class="section-note">KV Background (Gemini API) + Text Overlay (Pillow) — 100% Accurate Typography</div>
  <div class="grid">
    {cards_html}
  </div>
</div>

<div class="zoom-overlay" id="zoomOverlay" onclick="closeZoom()">
  <img id="zoomImg" src="" alt="zoom">
</div>

<div class="footer">
  DOCKING DESIGN SYSTEM — DESIGN FRAMES 01 v2 — GENERATED {timestamp}
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
    print("DESIGN FRAMES 01: LUMIERE v2")
    print("KV生成 (Gemini) + テキストオーバーレイ (Pillow)")
    print("Copy: その肌、まだ目覚めていない。")
    print("=" * 60)

    results = []
    for i, b in enumerate(banners):
        print(f"\n{'='*40}")
        print(f"[{i+1}/{len(banners)}] {b['out_file']}")

        # Step 1: KV生成
        kv_path = str(KV_DIR / b["kv_file"])
        if os.path.exists(kv_path):
            print(f"  KV exists, skipping generation: {b['kv_file']}")
        else:
            kv_path = generate_kv(b["kv_prompt"], b["kv_file"])

        if kv_path and os.path.exists(kv_path):
            # Step 2: テキストオーバーレイ
            out_path = str(OUT / b["out_file"])
            try:
                b["overlay"](kv_path, out_path)
                results.append((b["out_file"], out_path))
            except Exception as e:
                print(f"  Overlay error: {e}")
                import traceback
                traceback.print_exc()
                results.append((b["out_file"], None))
        else:
            results.append((b["out_file"], None))

        time.sleep(8)

    print("\n" + "=" * 60)
    print("RESULTS:")
    success = 0
    for fname, path in results:
        status = "OK" if path else "FAIL"
        print(f"  [{status}] {fname}")
        if path:
            success += 1
    print(f"\n{success}/{len(results)} completed")

    if success > 0:
        gallery = create_gallery(results)
        print(f"Gallery ready: {gallery}")

    print("=" * 60)

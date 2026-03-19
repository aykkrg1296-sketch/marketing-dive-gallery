#!/usr/bin/env python3
"""
DESIGN FRAMES 09: MELTY R4
PiAPI nano-banana-pro — テキスト精度が高い実績あり
ビジュアルはR1のベストをベースに、テキスト指示はナノバナナ式
"""
import requests, json, time, os, sys
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("PIAPI_API_KEY", "")
if not API_KEY:
    import subprocess
    result = subprocess.run(["bash", "-c", "source ~/.zshrc && echo $PIAPI_API_KEY"], capture_output=True, text=True)
    API_KEY = result.stdout.strip()

if not API_KEY:
    print("PIAPI_API_KEY not found"); sys.exit(1)

BASE_DIR = Path(__file__).parent
OUT = BASE_DIR / "banners_09_melty_r4"
OUT.mkdir(exist_ok=True)

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "DesignFrames/1.0"
}


def generate(prompt, filename, retries=2):
    payload = {
        "model": "gemini",
        "task_type": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "1:1"
        }
    }

    for attempt in range(retries + 1):
        try:
            print(f"\n  Requesting: {filename} (attempt {attempt+1})")
            r = requests.post("https://api.piapi.ai/api/v1/task",
                              headers=HEADERS, json=payload, timeout=30)
            r.raise_for_status()
            task = r.json()
            task_id = task["data"]["task_id"]
            print(f"  Task ID: {task_id}")

            for poll_attempt in range(90):
                time.sleep(5)
                poll = requests.get(f"https://api.piapi.ai/api/v1/task/{task_id}",
                                   headers=HEADERS, timeout=15)
                poll.raise_for_status()
                data = poll.json()["data"]
                status = data.get("status", "")

                if status == "completed":
                    urls = data.get("output", {}).get("image_urls", [])
                    if urls:
                        img_data = requests.get(urls[0], timeout=30).content
                        out_path = OUT / filename
                        with open(out_path, "wb") as f:
                            f.write(img_data)
                        print(f"  Done: {filename} ({len(img_data)/1024:.0f}KB)")
                        return str(out_path)
                    print("  No image URLs")
                    break
                elif status == "failed":
                    err = data.get("error", {})
                    print(f"  Failed: {err}")
                    break
                else:
                    if poll_attempt % 6 == 0:
                        print(f"  Waiting... {status} ({poll_attempt * 5}s)")

            if attempt < retries:
                print(f"  Retrying...")
                time.sleep(10)
                continue
            return None
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries:
                time.sleep(10)
                continue
            return None
    return None


# ============================================================
# MELTY ブランドDNA + テキスト指示
# ============================================================

BRAND_AND_TEXT = """
BRAND: MELTY — A monthly luxury sweets subscription box for hardworking women.
Style: Warm, feminine, dreamy, professional. Like a Parisian patisserie ad on Instagram.
Colors: Warm pink (#ff8a9e), peach (#ffc8a0), cream (#fff0e8), chocolate brown (#5a3e36).

TYPOGRAPHY (CRITICAL — must be PERFECTLY rendered):
Main Japanese copy in 2 lines:
  「がんばった日は、」 — warm brown, BOLD, large
  「もうひとつ食べていい。」 — pink accent on もうひとつ, warm brown for rest

  IMPORTANT: The word is もうひとつ (one more) = も・う・ひ・と・つ
  Font: Rounded gothic (soft sans-serif). Cute but professional.
  Dynamic SIZE VARIATION between elements. Text has subtle shadow for depth.

Brand name: MELTY — elegant, in English.

ONLY these 2 text elements. NO other text, watermarks, buttons, or captions.
"""

# ============================================================
# 8 Patterns
# ============================================================

banners = [
    {
        "filename": "melty_A1_flatlay.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — EXPLODING FLAT LAY:
Bird's eye view of artisan sweets scattered dynamically across white marble.
Pastel macarons (pink, lavender, mint, peach), chocolate bonbons, strawberry tart.
Rose petals, gold leaf flakes floating. Powdered sugar catching light.
Center area clear for text. Edges ABUNDANT with beautiful sweets.
Warm, dreamy lighting. The feeling: a treasure chest of sweets burst open.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_A2_chocolate.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — LIQUID CHOCOLATE POUR:
Extreme close-up of glossy melted chocolate poured over cream puffs.
Chocolate is viscous, shiny, catching warm light. Steam rising.
Warm pink/gold bokeh background.
Bottom 40% dark chocolate for text contrast (white/cream text there).
Pure indulgence. The moment before the first bite.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_B1_macaron.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — MACARON RAINBOW CASCADE:
Macarons cascading diagonally like a waterfall.
Each row different pastel: pink, peach, lavender, mint, cream.
Some split open showing colorful ganache filling.
Gold leaf and sugar crystals sparkling. Pink gradient background.
Diagonal flow with ENERGY. Abundance, joy.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_B2_giftbox.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — THE UNBOXING MOMENT:
Overhead: feminine hands with pretty nails opening a pink subscription box.
Box half-open, revealing perfectly arranged artisan sweets inside.
Tissue paper, gold MELTY card, ribbon. Rose petals on table.
Warm afternoon light. ANTICIPATION — fingers lifting the lid.
The ritual of treating yourself. Self-love in a box.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_C1_woman.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — BLISS PORTRAIT:
Close-up of beautiful Japanese woman (mid-20s) holding pink macaron near lips.
About to take a bite. Eyes half-closed, gentle smile. REAL emotion, not posed.
Soft warm lighting. Creamy bokeh background. Cream knit sweater.
PHOTOREALISTIC like a professional Japanese beauty ad.
Warm pink color grading. That moment after a long day.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_C2_cozy.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — GOLDEN HOUR COZY:
Dreamy kitchen scene bathed in golden hour light.
Woman's hands piping cream onto a tart. Flour dusted on counter.
Fresh strawberries, cup of tea steaming. MELTY box open with sweets.
Fairy lights in background. WARM golden glow everywhere.
Sunday afternoon. No rush. Pure joy.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_D1_minimal.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — ONE PERFECT MACARON (EDITORIAL):
Single perfect pink macaron on minimalist pink surface.
Shot like fashion editorial — dramatic but soft lighting, elegant shadow.
Incredible detail: shell texture, feet, cream filling visible.
MASSIVE negative space. Text is the STAR, filling the empty space.
A few artful crumbs. Gold leaf flake. Magazine-worthy minimalism.
Text large, dark charcoal. MELTY small in corner.

Professional Japanese Instagram advertisement quality."""
    },
    {
        "filename": "melty_D2_strawberry.png",
        "prompt": f"""Design a stunning 1080x1080 pixel square Japanese sweets advertisement.

{BRAND_AND_TEXT}

VISUAL — STRAWBERRY FANTASY:
Spectacular strawberry tart being assembled.
Fresh strawberry placed on top — FROZEN mid-action.
Whipped cream, golden pastry, powdered sugar floating in air.
Berries scattered around. Soft peach/pink bokeh with warm light.
SHARP food photography. The moment a masterpiece is completed.

Professional Japanese Instagram advertisement quality."""
    },
]


def create_gallery(results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    concepts = {
        "A1": ("Exploding Flat Lay", "弾けるフラットレイ。宝箱が開いた瞬間。"),
        "A2": ("Liquid Chocolate", "とろけるチョコの至福。"),
        "B1": ("Macaron Cascade", "マカロンの虹が流れ落ちる。"),
        "B2": ("The Unboxing", "サブスクBOXを開ける儀式。"),
        "C1": ("Bliss Portrait", "一口前の至福。"),
        "C2": ("Golden Hour Kitchen", "日曜午後のキッチン。"),
        "D1": ("One Perfect Macaron", "1個×エディトリアル。テキスト主役。"),
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
                    <img src="banners_09_melty_r4/{fname}" alt="{fname}" onclick="openZoom(this.src)">
                </div>
                <div class="card-info">
                    <div class="card-label">{key}</div>
                    <div class="card-title">{cn}</div>
                    <div class="card-desc">{cd}</div>
                </div>
            </div>"""
    html = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>MELTY R4 (PiAPI)</title>
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
  <div class="meta"><span class="badge">R4</span><span class="badge">PiAPI nano-banana-pro</span><span class="badge">FEMALE / PLAYFUL</span></div>
</div>
<div class="grid">{cards_html}</div>
<div class="zoom-overlay" id="zo" onclick="closeZoom()"><img id="zi" src=""></div>
<div class="footer">DESIGN FRAMES 09 MELTY R4 — {timestamp}</div>
<script>
function openZoom(s){{document.getElementById('zi').src=s;document.getElementById('zo').classList.add('active');}}
function closeZoom(){{document.getElementById('zo').classList.remove('active');}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeZoom();}});
</script></body></html>"""
    p = BASE_DIR / "gallery_09_melty_r4.html"
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return str(p)


if __name__ == "__main__":
    print("=" * 60)
    print("MELTY R4 — PiAPI nano-banana-pro")
    print("=" * 60)
    results = []
    for i, b in enumerate(banners):
        print(f"\n[{i+1}/{len(banners)}] {b['filename']}")
        path = generate(b["prompt"], b["filename"])
        results.append((b["filename"], path))
        if path:
            time.sleep(3)
        else:
            time.sleep(5)
    print("\n" + "=" * 60)
    ok = sum(1 for _, p in results if p)
    for f, p in results:
        print(f"  [{'OK' if p else 'FAIL'}] {f}")
    print(f"\n{ok}/{len(results)} generated")
    if ok > 0:
        g = create_gallery(results)
        print(f"Gallery: {g}")
    print("=" * 60)

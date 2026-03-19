#!/usr/bin/env python3
"""
MARKETING DIVE — 20 Banner Generation Script
Based on ぎいちゃん's design references:
  Group A (1-5): 青ポスター系 — Bold typography, blue×white×black
  Group B (6-10): ペルソナ3R RPG UI系 — Blue gradient, menu-style, bold katakana
  Group C (11-15): コラージュ・グリッド系 — Grid textures, collage, dynamic
  Group D (16-20): 深海ファンタジー × タイポグラフィ系 — Deep sea + aggressive typo
"""

import urllib.request, json, os, time, subprocess, sys

def _load_env(var):
    if not os.environ.get(var):
        try:
            r = subprocess.run(['zsh', '-i', '-c', f'echo ${var}'],
                             capture_output=True, text=True, timeout=5)
            v = r.stdout.strip()
            if v:
                os.environ[var] = v
        except:
            pass

_load_env('PIAPI_API_KEY')
API_KEY = os.environ.get('PIAPI_API_KEY', '')
if not API_KEY:
    print("ERROR: PIAPI_API_KEY not found")
    sys.exit(1)

BASE_URL = "https://api.piapi.ai/api/v1"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KV_DIR = os.path.join(SCRIPT_DIR, "kv")
SPEC_DIR = os.path.join(SCRIPT_DIR, "specs")
os.makedirs(KV_DIR, exist_ok=True)
os.makedirs(SPEC_DIR, exist_ok=True)

# === 20 Banner Specs ===
# Colors: primary=#1058C4, secondary=#67CAFF, accent=#FF6600, warm=#FFC61C
# Concept: 招待状 (Invitation), Deep Sea × RPG
# N1: 30s male, ENFP, corporate, restless creative energy

BANNER_SPECS = [
    # ===== Group A: 青ポスター系 (Blue Poster Style) =====
    {
        "index": 1,
        "group": "A_blue_poster",
        "hook": "歓迎フック",
        "headline": "あなたを、迎えにきた",
        "gaze": "中央集中",
        "hypothesis": "Prague School的な青ベタ×白文字の大胆タイポで、感情直撃の歓迎メッセージを中央に配置",
        "prompt": (
            "A bold graphic poster design for a Japanese marketing aptitude test. "
            "Solid royal blue background (#1058C4) filling the entire canvas. "
            "Large bold white Japanese typography centered on the blue background, taking up 60% of the frame. "
            "Minimalist composition with only blue and white colors. "
            "Clean sans-serif Japanese font. No images, pure typographic poster design. "
            "The text reads: あなたを、迎えにきた. "
            "Small white subtext at bottom: 無料で適性を診断する. "
            "Professional, modern, high contrast. Square format 1:1 aspect ratio. "
            "Style reference: Prague School of Design posters, Swiss typography."
        )
    },
    {
        "index": 2,
        "group": "A_blue_poster",
        "hook": "適性フック",
        "headline": "あなたの才能、招待します",
        "gaze": "Z型",
        "hypothesis": "青×黒×白の3色構成で、テキストがフレームからはみ出すダイナミックタイポ",
        "prompt": (
            "A striking typographic poster. Split composition: left half deep black, right half vivid royal blue (#1058C4). "
            "Giant white Japanese text spanning across both halves, letters partially cropped at edges. "
            "The text reads: あなたの才能、招待します. "
            "Text is so large it bleeds off the frame edges — bold, confident, dynamic. "
            "Small golden (#FFC61C) accent line separating the two halves. "
            "Minimal, only 3 colors: black, royal blue, white. "
            "Bottom right: small white button-like element with text 無料で適性を診断する. "
            "Square 1:1 format. Clean modern design, no illustrations."
        )
    },
    {
        "index": 3,
        "group": "A_blue_poster",
        "hook": "面白さフック",
        "headline": "面白いほうへ、おいで",
        "gaze": "対角線",
        "hypothesis": "ドットパターン×青で軽さとポップさを両立、冒険心を刺激",
        "prompt": (
            "A playful yet sophisticated poster design. White background with subtle blue dot pattern (halftone effect). "
            "Diagonal composition with large blue (#1058C4) Japanese text placed at a dynamic angle across the canvas. "
            "The text reads: 面白いほうへ、おいで. "
            "Blue dots of varying sizes scattered organically. Some dots are light cyan (#67CAFF), some deep blue. "
            "A small orange (#FF6600) arrow pointing diagonally, adding energy. "
            "Bottom area: clean white space with small text 無料で適性を診断する. "
            "Feels light, fun, inviting. Square 1:1 format. Japanese graphic design aesthetic."
        )
    },
    {
        "index": 4,
        "group": "A_blue_poster",
        "hook": "共感フック",
        "headline": "その発想力、持て余してない？",
        "gaze": "F型",
        "hypothesis": "青×写真コラージュ切り裂き風で、N1の痛みに共感するビジュアル",
        "prompt": (
            "A dramatic graphic design. The canvas is split diagonally — top-left is solid royal blue (#1058C4), "
            "bottom-right shows a moody photograph of a businessman's silhouette staring at a city skyline at dusk. "
            "The diagonal cut is sharp and bold, like torn paper. "
            "Large white Japanese text overlaid across both sections: その発想力、持て余してない？ "
            "The text bridges the blue and photo sections. "
            "Small cyan (#67CAFF) subtitle near bottom. "
            "CTA button in orange (#FF6600) at bottom right: 無料で適性を診断する. "
            "Square 1:1 format. Modern, editorial feel like Une Saison Graphique poster."
        )
    },
    {
        "index": 5,
        "group": "A_blue_poster",
        "hook": "歓迎フック",
        "headline": "マーケの世界への招待状",
        "gaze": "中央集中",
        "hypothesis": "漆黒×単一光源の招待状ビジュアルで、コンセプトを直球で伝達",
        "prompt": (
            "A dramatic dark poster. Black background with a single glowing invitation envelope in the center, "
            "emitting soft blue-white light (#67CAFF glow). The envelope appears to float in darkness. "
            "Above the envelope: large bold white Japanese text マーケの世界への招待状. "
            "Golden (#FFC61C) light rays emanating from the envelope opening. "
            "Minimalist composition, generous negative space. "
            "Small white text at bottom: 無料で適性を診断する. "
            "Cinematic lighting, mysterious, inviting. Square 1:1 format. "
            "Style: dark luxury, like a movie poster."
        )
    },

    # ===== Group B: ペルソナ3R RPG UI系 =====
    {
        "index": 6,
        "group": "B_persona3r_rpg",
        "hook": "面白さフック",
        "headline": "面白いほうへ、おいで",
        "gaze": "中央集中",
        "hypothesis": "ペルソナ3R的メニューUI構成で、RPG世界観を全面に出して没入感を演出",
        "prompt": (
            "A Japanese RPG-style menu interface design. Deep blue gradient background resembling underwater depths. "
            "Menu items arranged diagonally from top-left to bottom-right in bold Japanese text: "
            "DIVE / SKILL / TEST / RESULT — styled like Persona 3 Reload menu. "
            "The selected item 'DIVE' is highlighted in bright cyan (#67CAFF) and larger. "
            "Small character silhouette on the right side. "
            "Blue light particles floating upward like underwater bubbles. "
            "Top area: 面白いほうへ、おいで in stylized white text. "
            "Bottom: golden (#FFC61C) UI bar with 無料で適性を診断する. "
            "Square 1:1 format. Anime/game UI aesthetic, polished and professional."
        )
    },
    {
        "index": 7,
        "group": "B_persona3r_rpg",
        "hook": "適性フック",
        "headline": "あなたの才能、招待します",
        "gaze": "対角線",
        "hypothesis": "カタカナ大胆表示でスキル発動演出 — 適性テストをRPGスキルに見立てる",
        "prompt": (
            "A dramatic RPG skill activation screen. Dark blue-black background with intense blue light radiating from center. "
            "Giant bold katakana テキセイ (aptitude) filling 70% of the frame with outline/stroke treatment. "
            "Behind the text: a human figure with arms outstretched, silhouetted against blue light. "
            "Blue ice crystal effects emanating from the figure's feet upward. "
            "Smaller white text overlay: あなたの才能、招待します. "
            "Vertical green equalizer bars on the left edge (digital/tech feel). "
            "Bottom: UI-style bar with 無料で適性を診断する. "
            "Square 1:1 format. Persona 3 Reload battle scene aesthetic."
        )
    },
    {
        "index": 8,
        "group": "B_persona3r_rpg",
        "hook": "歓迎フック",
        "headline": "あなたを、迎えにきた",
        "gaze": "Z型",
        "hypothesis": "キャラクター顔アップ×全身2レイヤーで、迎えに来た存在を演出",
        "prompt": (
            "A stylish RPG character reveal screen. Blue-purple gradient background like deep ocean. "
            "Background layer: large faded close-up of a mysterious character's face looking directly at viewer. "
            "Foreground layer: full-body silhouette of the same character extending a hand toward the viewer. "
            "Dramatic blue lighting from behind the character creating a halo effect. "
            "Bold white Japanese text at top: あなたを、迎えにきた. "
            "Style reference: Persona 3 Reload's dual-layer character presentation. "
            "Glowing blue particles floating in the air. "
            "Bottom UI bar with 無料で適性を診断する in a clean button. "
            "Square 1:1 format. Anime-influenced, cinematic, atmospheric."
        )
    },
    {
        "index": 9,
        "group": "B_persona3r_rpg",
        "hook": "共感フック",
        "headline": "その発想力、持て余してない？",
        "gaze": "F型",
        "hypothesis": "RPGステータス画面風で、N1の眠れるスキルを可視化して共感を狙う",
        "prompt": (
            "An RPG character status screen design. Dark blue (#1058C4) background with subtle grid lines. "
            "Left side: character stats displayed as vertical bars — 発想力: MAX (golden bar), 実行力: LOW (dim bar), "
            "マーケ適性: ??? (pulsing blue). "
            "Right side: silhouette of a businessman looking at a glowing screen. "
            "Center: bold white Japanese text その発想力、持て余してない？ "
            "Blue accent lines and UI elements framing the composition. "
            "Bottom: clean button 無料で適性を診断する with orange (#FF6600) highlight. "
            "Square 1:1 format. Game UI aesthetic, data visualization meets RPG."
        )
    },
    {
        "index": 10,
        "group": "B_persona3r_rpg",
        "hook": "面白さフック",
        "headline": "最高に面白い入口",
        "gaze": "中央集中",
        "hypothesis": "RPGダンジョン入口演出で、冒険の始まりを視覚化",
        "prompt": (
            "A mysterious RPG dungeon entrance scene. Dark underwater cave with a massive ornate door in the center, "
            "glowing with golden (#FFC61C) light seeping through the cracks. "
            "Deep blue ocean water surrounding the door, with bioluminescent particles floating. "
            "The door has intricate patterns suggesting ancient knowledge and marketing symbols. "
            "Above the door: bold white Japanese text 最高に面白い入口. "
            "Atmospheric fog and blue light rays streaming through the water. "
            "Bottom: 無料で適性を診断する as a glowing UI element. "
            "Square 1:1 format. Fantasy RPG meets deep sea. Mysterious, inviting, adventurous."
        )
    },

    # ===== Group C: コラージュ・グリッド系 =====
    {
        "index": 11,
        "group": "C_collage_grid",
        "hook": "歓迎フック",
        "headline": "あなたを、迎えにきた",
        "gaze": "Z型",
        "hypothesis": "方眼紙グリッド×はみ出し要素で、クリエイティブなエネルギーを表現",
        "prompt": (
            "A creative collage-style design on a subtle graph paper grid background. "
            "Light blue grid lines visible underneath. "
            "Large Japanese text あなたを、迎えにきた placed at an angle, breaking out of the grid. "
            "Photo cutout of a hand reaching forward, placed over the grid at a dynamic angle. "
            "Blue (#1058C4) geometric shapes overlapping with the text. "
            "Some elements deliberately extend beyond the frame edges. "
            "Scattered small circles in cyan (#67CAFF) as decorative dots. "
            "Bottom right: orange (#FF6600) CTA button 無料で適性を診断する. "
            "Square 1:1 format. Editorial, dynamic, grid-breaking energy."
        )
    },
    {
        "index": 12,
        "group": "C_collage_grid",
        "hook": "適性フック",
        "headline": "あなたの才能、招待します",
        "gaze": "対角線",
        "hypothesis": "写真×テキストの大胆な重ね合わせで、コラージュ的な招待状表現",
        "prompt": (
            "A bold collage composition. A photograph of ocean waves diagonally placed from top-left to center. "
            "Over the photo: large bold blue (#1058C4) Japanese text overlapping into the white space: "
            "あなたの才能、招待します. "
            "Text and photo are not separated — they interweave. "
            "White brush stroke splash effect behind part of the headline. "
            "Scattered cut-out elements: an envelope, a compass, abstract blue shapes. "
            "Multiple layers creating depth. "
            "Small detail text in a different orientation (vertical). "
            "CTA at bottom: 無料で適性を診断する in clean sans-serif. "
            "Square 1:1 format. Magazine editorial collage style."
        )
    },
    {
        "index": 13,
        "group": "C_collage_grid",
        "hook": "共感フック",
        "headline": "その発想力、持て余してない？",
        "gaze": "F型",
        "hypothesis": "サイバー/テクノ要素×グリッドで、データ×テクノロジーの適性テスト感を演出",
        "prompt": (
            "A tech-forward design with blue (#1058C4) wireframe 3D globe in the background. "
            "Cyber grid lines covering the canvas in perspective, converging to a vanishing point. "
            "Spec-sheet style small text scattered around edges (like technical specifications). "
            "Center: bold white Japanese text その発想力、持て余してない？ "
            "Blue and cyan (#67CAFF) data visualization elements: bar charts, node connections. "
            "Wireframe torus shape floating to the right. "
            "The overall feel is analytical yet inviting. "
            "Bottom: clean CTA 無料で適性を診断する with orange accent. "
            "Square 1:1 format. Cyberpunk meets professional assessment tool."
        )
    },
    {
        "index": 14,
        "group": "C_collage_grid",
        "hook": "面白さフック",
        "headline": "面白いほうへ、おいで",
        "gaze": "中央集中",
        "hypothesis": "複数素材の切り抜き重ねで、ワクワクする冒険の雰囲気を作る",
        "prompt": (
            "A vibrant collage with multiple layered cut-out elements. "
            "Center: a person silhouette diving downward (as if diving into the sea). "
            "Layered around: cut-out photos of a laptop, a lightbulb, a graph trending up, ocean waves. "
            "All elements overlap and interact, creating visual depth. "
            "Background: gradient from white (top) to deep blue (#1058C4, bottom). "
            "Large bold text 面白いほうへ、おいで in mixed sizes — 面白い is biggest. "
            "Star sparkle decorations (★) near the text — small, elegant. "
            "Bottom: 無料で適性を診断する in clean design. "
            "Square 1:1 format. Energetic, optimistic, adventure-calling."
        )
    },
    {
        "index": 15,
        "group": "C_collage_grid",
        "hook": "歓迎フック",
        "headline": "マーケの世界への招待状",
        "gaze": "Z型",
        "hypothesis": "縦書き×横書きミックスの日本語タイポで、和×モダンの招待状感を演出",
        "prompt": (
            "A sophisticated Japanese design mixing vertical and horizontal text. "
            "Left side: vertical Japanese text マーケの世界への in elegant thin font. "
            "Center-right: horizontal bold text 招待状 in large blue (#1058C4) characters. "
            "Background: white with subtle blue watercolor-like gradient at bottom. "
            "A delicate golden (#FFC61C) line connecting the vertical and horizontal text. "
            "Small English text 'MARKETING DIVE' as decorative sub-element. "
            "Envelope icon subtly integrated into the design. "
            "Bottom: 無料で適性を診断する in a refined layout. "
            "Square 1:1 format. Japanese editorial design meets invitation card aesthetic."
        )
    },

    # ===== Group D: 深海ファンタジー × タイポグラフィ =====
    {
        "index": 16,
        "group": "D_deep_sea_typo",
        "hook": "歓迎フック",
        "headline": "あなたを、迎えにきた",
        "gaze": "中央集中",
        "hypothesis": "深海で招待状に手を伸ばすKV — strategy.jsonのkeyVisualそのもの",
        "prompt": (
            "A cinematic deep ocean scene. Dark blue-black water fills the frame. "
            "In the center, a glowing invitation envelope floats, radiating golden-white light upward. "
            "A human hand reaches toward the envelope from the bottom of the frame. "
            "Blue bioluminescent particles and light rays streaming through the water. "
            "The light from the envelope illuminates the hand and creates god rays. "
            "Above: large white Japanese text あなたを、迎えにきた with subtle glow. "
            "The text appears to float in the water. "
            "Bottom: small white text 無料で適性を診断する. "
            "Square 1:1 format. Ethereal, emotional, like an underwater movie scene."
        )
    },
    {
        "index": 17,
        "group": "D_deep_sea_typo",
        "hook": "適性フック",
        "headline": "あなたの才能、招待します",
        "gaze": "対角線",
        "hypothesis": "深海×漆黒背景×単一被写体（Aquatilis的）で、才能が光る表現",
        "prompt": (
            "A dark, atmospheric underwater scene. Pure black background. "
            "A single bioluminescent jellyfish-like creature glowing in cyan (#67CAFF) and gold (#FFC61C), "
            "positioned in the lower-right area. "
            "The creature emits light that illuminates the surrounding darkness. "
            "Large white text あなたの才能、招待します positioned diagonally from upper-left. "
            "The text has mixed font weights — 才能 is extra bold, rest is light. "
            "Generous negative space (40% of canvas is pure dark). "
            "Tiny particles of light scattered sparsely. "
            "Bottom-left: 無料で適性を診断する in thin white font. "
            "Square 1:1 format. Aquatilis Expedition style: dark luxury, minimal, profound."
        )
    },
    {
        "index": 18,
        "group": "D_deep_sea_typo",
        "hook": "共感フック",
        "headline": "その発想力、持て余してない？",
        "gaze": "F型",
        "hypothesis": "深海の圧力×解放のメタファーで、N1の閉塞感と可能性を表現",
        "prompt": (
            "A dramatic split composition. Top half: dark, heavy deep ocean pressure — compressed dark blue, "
            "with a small silhouette of a person sitting at a desk, looking down. "
            "Bottom half: the ocean opens up into a vast bright underwater world with blue light, "
            "coral-like structures, and floating golden particles. "
            "The transition between dark and light is dramatic. "
            "Text: その発想力、持て余してない？ in bold white, positioned across the transition zone. "
            "The word 発想力 is highlighted in cyan (#67CAFF). "
            "Bottom: 無料で適性を診断する with warm orange (#FF6600) button. "
            "Square 1:1 format. Emotional, metaphorical, contrast between constraint and freedom."
        )
    },
    {
        "index": 19,
        "group": "D_deep_sea_typo",
        "hook": "面白さフック",
        "headline": "面白いほうへ、おいで",
        "gaze": "Z型",
        "hypothesis": "Nike Tech Pack的な写真×ボールドタイポ — 深海写真にデュオトーン照明",
        "prompt": (
            "A high-impact design inspired by Nike Tech Pack posters. "
            "Full-bleed photo of deep ocean scene with duotone lighting — blue (#1058C4) from left, "
            "warm orange (#FF6600) from right, creating dramatic dual-color effect. "
            "Massive white Japanese text 面白いほうへ、おいで overlaid on the photo. "
            "The text is so large that 面白い extends beyond the left edge. "
            "Wide letter spacing on the text, premium typographic feel. "
            "Small 'MARKETING DIVE' text in thin white at top-right corner. "
            "Bottom: 無料で適性を診断する in clean white. "
            "Square 1:1 format. Athletic poster energy applied to deep sea imagery."
        )
    },
    {
        "index": 20,
        "group": "D_deep_sea_typo",
        "hook": "歓迎フック",
        "headline": "あなたを、迎えにきた",
        "gaze": "中央集中",
        "hypothesis": "被写体中央+背面大型タイポ(Dance的) — 招待状を持つ人物の背後に巨大文字",
        "prompt": (
            "A powerful composition inspired by Dance poster (Behance). "
            "Deep dark blue-black background. "
            "Center: full-height silhouette of a figure standing, holding a glowing envelope at chest level. "
            "Behind the figure: enormous faded Japanese text 招待 (invitation) as background typography layer, "
            "partially visible behind the figure, creating depth with text-behind-subject technique. "
            "The envelope emits warm golden (#FFC61C) light upward. "
            "Blue (#1058C4) and cyan (#67CAFF) rim lighting on the figure's edges. "
            "Above: white text あなたを、迎えにきた in bold but smaller than the background text. "
            "Bottom: 無料で適性を診断する. "
            "Square 1:1 format. Cinematic, layered, elegant darkness."
        )
    },
]

def create_task(prompt, aspect_ratio="1:1"):
    payload = {
        "model": "gemini",
        "task_type": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio
        }
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(f"{BASE_URL}/task", data)
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", API_KEY)
    req.add_header("User-Agent", "BannerPark/7.0")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ERROR creating task: {e}")
        return None

def get_task(task_id):
    req = urllib.request.Request(f"{BASE_URL}/task/{task_id}")
    req.add_header("x-api-key", API_KEY)
    req.add_header("User-Agent", "BannerPark/7.0")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ERROR getting task: {e}")
        return None

def download_image(url, filepath):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "BannerPark/7.0")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  ERROR downloading: {e}")
        return False

def main():
    print("=" * 60)
    print("  BANNER PARK v7.0 — MARKETING DIVE 20 Banners")
    print("  Design References: Blue Posters / Persona 3R / Collage / Deep Sea")
    print("=" * 60)

    # Phase 1: Create all tasks
    tasks = {}
    for spec in BANNER_SPECS:
        idx = spec["index"]
        fp = os.path.join(KV_DIR, f"kv_{idx:02d}.png")
        if os.path.exists(fp) and os.path.getsize(fp) > 10240:
            print(f"  [SKIP] Banner {idx:02d} — already exists")
            continue

        print(f"  [CREATE] Banner {idx:02d} ({spec['group']}) — {spec['headline']}")
        result = create_task(spec["prompt"])
        if result and result.get("data", {}).get("task_id"):
            task_id = result["data"]["task_id"]
            tasks[idx] = task_id
            print(f"    task_id: {task_id}")
        else:
            print(f"    FAILED: {result}")
        time.sleep(1.5)  # Rate limit spacing

    if not tasks:
        print("\nAll banners already exist or all tasks failed.")
        return

    # Phase 2: Poll for completion
    print(f"\n{'=' * 60}")
    print(f"  Waiting for {len(tasks)} tasks to complete...")
    print(f"{'=' * 60}")

    completed = set()
    failed = set()
    max_wait = 600  # 10 minutes
    start_time = time.time()

    while len(completed) + len(failed) < len(tasks):
        if time.time() - start_time > max_wait:
            print("\n  TIMEOUT — stopping poll")
            break

        for idx, task_id in tasks.items():
            if idx in completed or idx in failed:
                continue

            result = get_task(task_id)
            if not result:
                continue

            status = result.get("data", {}).get("status", "")

            if status == "completed":
                # Extract image URL
                output = result.get("data", {}).get("output", {})
                image_url = None

                # Try different response structures
                if isinstance(output, dict):
                    image_url = output.get("image_url") or output.get("url")
                    if not image_url and "image_urls" in output:
                        urls = output["image_urls"]
                        if urls:
                            image_url = urls[0] if isinstance(urls, list) else urls

                if not image_url:
                    # Try nested structure
                    try:
                        image_url = result["data"]["output"]["image_url"]
                    except (KeyError, TypeError):
                        pass

                if not image_url:
                    # Try to find any URL in the output
                    output_str = json.dumps(result.get("data", {}))
                    import re
                    urls = re.findall(r'https?://[^\s"]+\.(?:png|jpg|jpeg|webp)', output_str)
                    if urls:
                        image_url = urls[0]

                if image_url:
                    fp = os.path.join(KV_DIR, f"kv_{idx:02d}.png")
                    if download_image(image_url, fp):
                        completed.add(idx)
                        print(f"  ✅ Banner {idx:02d} — downloaded")
                    else:
                        failed.add(idx)
                        print(f"  ❌ Banner {idx:02d} — download failed")
                else:
                    failed.add(idx)
                    print(f"  ❌ Banner {idx:02d} — no image URL in response")
                    print(f"     Output: {json.dumps(result.get('data', {}), ensure_ascii=False)[:200]}")

            elif status == "failed":
                failed.add(idx)
                error = result.get("data", {}).get("error", "unknown")
                print(f"  ❌ Banner {idx:02d} — FAILED: {error}")

        remaining = len(tasks) - len(completed) - len(failed)
        if remaining > 0:
            print(f"  ... waiting ({len(completed)} done, {len(failed)} failed, {remaining} pending)")
            time.sleep(10)

    # Phase 3: Save specs
    for spec in BANNER_SPECS:
        spec_path = os.path.join(SPEC_DIR, f"banner_{spec['index']:02d}_spec.json")
        with open(spec_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  GENERATION COMPLETE")
    print(f"  ✅ Completed: {len(completed)}")
    print(f"  ❌ Failed: {len(failed)}")
    skipped = len(BANNER_SPECS) - len(tasks)
    if skipped:
        print(f"  ⏭  Skipped (already existed): {skipped}")
    print(f"  📁 Output: {KV_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""MELTY Typography Play Round 3 — A1〜D2ビジュアル × タイポグラフィ遊び"""

import os
import time
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL = "gemini-3.1-flash-image-preview"
OUT = os.path.join(os.path.dirname(__file__), "banners_09_melty_v31")

BRAND_CONTEXT = """
Brand: MELTY — 月額制アルチザンスイーツ定期便
Target: 働く女性（25-35歳）
Tone: Playful, indulgent, self-reward
Copy: 「がんばった日は、もうひとつ食べていい。」
Brand name "MELTY" must appear on every banner.
Colors: Soft pink (#ff8a9e), cream (#fffaf5), chocolate brown (#5a3e36)
ALL Japanese text must be 100% accurate — every single character must be perfectly correct.

IMPORTANT TYPOGRAPHY DIRECTION:
The text should NOT just be placed plainly on the image. Play with the typography creatively:
- Mix font sizes dramatically (some words HUGE, some tiny)
- Let text interact with the food photography (wrap around, peek behind, overlap)
- Use playful kerning, line breaks at unexpected places
- Make the text feel like part of the design, not an afterthought
- Think magazine editorial, fashion ads, high-end confectionery packaging
"""

variants = [
    {
        "id": "A1t_flatlay_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Luxurious overhead flat lay — artisan macarons, chocolates, flower petals, gold leaf scattered on marble surface. Treasure-box composition from above. Warm cream and pink tones.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 is arranged in a SPIRAL or SCATTERED layout among the sweets — as if the words are scattered treasures too. "がんばった日は" in tiny delicate text, then "もうひとつ" HUGE and bold in the center, then "食べていい。" small and playful. "MELTY" in elegant thin letters at top. The text becomes part of the flat lay composition itself.
"""
    },
    {
        "id": "A2t_chocolate_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Rich liquid chocolate pouring and swirling. Dark chocolate × gold accents. Luxurious, indulgent, close-up of melting chocolate. Deep brown background.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 in GOLD metallic text that looks like it's floating ON the chocolate surface. "食べていい。" is the biggest word, dripping slightly like the chocolate. Mix of sizes — "がんばった日は、" small and refined at top, then "もうひとつ" medium, then "食べていい。" MASSIVE and bold. "MELTY" in sleek gold sans-serif. The gold text against dark chocolate = luxury.
"""
    },
    {
        "id": "B1t_macaron_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Colorful pastel macarons cascading/falling dynamically through the frame. Pink, lavender, mint, peach macarons in motion. Bright, joyful, dynamic energy.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 is WOVEN between the falling macarons — some text in FRONT of macarons, some BEHIND, creating depth layers. "もうひとつ" is the biggest word, tilted slightly at a playful angle. Different words in different pastel colors matching the macarons. "MELTY" bold at the top. The text dances with the macarons.
"""
    },
    {
        "id": "B2t_giftbox_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Beautiful gift box being opened, revealing artisan sweets inside. Ribbon, tissue paper, the moment of unboxing. Self-love, treat yourself. Soft pink and gold.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 is designed like a GIFT TAG or RIBBON text. "がんばった日は、" curves along a ribbon shape. "もうひとつ食べていい。" is written large and bold as if it's the message INSIDE the gift card. "MELTY" appears as the brand stamp on the box. The text feels like part of the packaging design.
"""
    },
    {
        "id": "C1t_woman_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Beautiful woman about to take a blissful first bite of a macaron. Beauty-ad quality portrait. Soft lighting, eyes closed in anticipation. Warm, dreamy.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 wraps around her like a WHISPER — text follows a curved path around her face/shoulders. "もうひとつ" is the largest word, positioned near the macaron she's about to eat. Rest of the text is delicate and small, like a secret she's telling herself. "MELTY" small and elegant in corner. The text feels intimate, like inner monologue.
"""
    },
    {
        "id": "C2t_cozy_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Cozy evening scene — hot cocoa, subscription box of sweets, blanket, warm lighting. Hygge/comfort vibes. Warm tones, soft focus.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 is styled like HANDWRITTEN text on a steamy window or in cocoa foam. Warm, cozy, imperfect handwriting. "がんばった日は、" written small like a diary entry, "もうひとつ食べていい。" bigger and more confident — as if she's giving herself permission. "MELTY" on the subscription box. Text feels like a cozy journal entry.
"""
    },
    {
        "id": "D1t_minimal_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Single macaron on a clean minimal surface. Lots of white/cream space. Editorial, sophisticated, less is more.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 is the HERO — takes up 70% of the frame in bold, confident typography. Dramatic size contrast: "もうひとつ" is ENORMOUS (fills half the image), rest of the text is tiny. The single macaron sits perfectly in the negative space created by the text layout. "MELTY" tiny at bottom. Think Swiss/Japanese minimalist poster design.
"""
    },
    {
        "id": "D2t_strawberry_typo",
        "prompt": f"""{BRAND_CONTEXT}

VISUAL: Strawberry tart being completed — powdered sugar dusting through the air, fresh strawberries, golden pastry crust. The magical moment of finishing touch.

TYPOGRAPHY PLAY: The copy 「がんばった日は、もうひとつ食べていい。」 is arranged in a VERTICAL STACK on one side, with each line a different size. "食べていい。" at the bottom is the LARGEST, like a declaration. The powdered sugar particles seem to interact with the text. "MELTY" integrated into the composition as a brand watermark. Text and food create a balanced editorial spread.
"""
    },
]

for i, v in enumerate(variants):
    print(f"\n{'='*60}")
    print(f"[{i+1}/8] Generating {v['id']}...")
    print(f"{'='*60}")
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=v["prompt"],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )
        
        saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                path = os.path.join(OUT, f"melty_{v['id']}.png")
                with open(path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✅ Saved: melty_{v['id']}.png")
                saved = True
            elif part.text:
                print(f"📝 {part.text[:150]}")
        
        if not saved:
            print("⚠️ No image generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(3)

print("\n🎉 Typography Round 3 — All 8 base visuals with typo play — complete!")

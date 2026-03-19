#!/usr/bin/env python3
"""MELTY Typography Play Round 2 — もっと攻めたタイポグラフィ"""

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
ALL Japanese text must be 100% accurate — every character must be correct.
"""

variants = [
    {
        "id": "T5_melting_text",
        "prompt": f"""{BRAND_CONTEXT}

Create a premium banner ad (1080x1080px) with an EXTREME typography concept:

MELTING TEXT — The Japanese copy 「がんばった日は、もうひとつ食べていい。」 is rendered in elegant serif font, but the bottom of each character is MELTING like chocolate dripping down. The text starts solid at the top and dissolves into liquid chocolate streams at the bottom. Background is minimal cream/white. A few artisan chocolates and macarons are scattered at the bottom where the melted text pools. Brand name "MELTY" in clean sans-serif at the top. The melting effect should look luxurious, not messy — like haute couture meets confectionery.
"""
    },
    {
        "id": "T6_giant_letter",
        "prompt": f"""{BRAND_CONTEXT}

Create a premium banner ad (1080x1080px) with an EXTREME typography concept:

GIANT LETTER — The letter "M" from MELTY fills 90% of the frame. The "M" shape acts as a WINDOW/MASK — inside the letter shape, we see a beautiful photo of artisan macarons, chocolates, and pastries in soft pink and gold tones. Outside the "M" is solid soft pink (#ff8a9e). The Japanese copy 「がんばった日は、もうひとつ食べていい。」 is written small and elegant below the giant M in brown (#5a3e36). The rest of "ELTY" appears small next to the giant M. Think high-fashion magazine cover typography.
"""
    },
    {
        "id": "T7_handwritten",
        "prompt": f"""{BRAND_CONTEXT}

Create a premium banner ad (1080x1080px) with an EXTREME typography concept:

HANDWRITTEN STYLE — A beautiful overhead photo of a pastel pink marble table with macarons, a latte, and flower petals. On top of this photo, the Japanese copy 「がんばった日は、もうひとつ食べていい。」 appears as if HAND-WRITTEN directly on the photo in chocolate brown ink with a calligraphy pen. The handwriting should look feminine, elegant, and slightly imperfect — like a love letter to yourself. "MELTY" appears in a clean printed font as a small logo in the corner. The handwritten text should be the HERO — large, flowing, and full of personality.
"""
    },
    {
        "id": "T8_negative_space",
        "prompt": f"""{BRAND_CONTEXT}

Create a premium banner ad (1080x1080px) with an EXTREME typography concept:

NEGATIVE SPACE TEXT — The entire frame is filled with a rich, close-up photo of colorful macarons, chocolates, and berries. The Japanese copy 「がんばった日は、もうひとつ食べていい。」 is CUT OUT from this photo in WHITE — the text shapes reveal white/cream beneath, creating a knockout/negative space effect. The text is large and bold, taking up the center of the image. "MELTY" is also cut out in white at the top. The effect: you read the message THROUGH the absence of sweets. Sophisticated, editorial, striking.
"""
    },
]

for v in variants:
    print(f"\n{'='*60}")
    print(f"Generating {v['id']}...")
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
                print(f"✅ Saved: {path}")
                saved = True
            elif part.text:
                print(f"📝 Model note: {part.text[:200]}")
        
        if not saved:
            print("⚠️ No image generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(2)

print("\n🎉 Typography Round 2 complete!")

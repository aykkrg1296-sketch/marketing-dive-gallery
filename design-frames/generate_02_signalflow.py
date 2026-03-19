#!/usr/bin/env python3
"""SIGNALFLOW — 02 SaaS/B2B AIデータ分析プラットフォーム"""

import os
import time
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL = "gemini-3.1-flash-image-preview"
OUT = os.path.join(os.path.dirname(__file__), "banners_02_signalflow")
os.makedirs(OUT, exist_ok=True)

BRAND = """
Brand: SIGNALFLOW — AIデータ分析プラットフォーム（SaaS/B2B）
Target: Male, marketing directors/CMOs, 30-45歳
Tone: HARD, authoritative, trustworthy, cutting-edge
Copy: 「データは語っている。聞こえているか。」
Brand name "SIGNALFLOW" must appear on every banner.
Colors: Dark navy (#0a1628), Blue (#1058C4), Sky blue (#67CAFF), Light (#e8f4fd), White
Design direction: Swiss Design, clean grids, data visualization aesthetic, minimal, professional
Typography: Sharp, geometric sans-serif. Clean. No decorative fonts.
ALL Japanese text must be 100% accurate — every character must be perfectly correct.
"""

# ========== BASE 8枚 ==========
base = [
    {
        "id": "A1_dashboard",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: A sleek dark dashboard UI floating in dark navy space. Glowing blue data charts, line graphs, and KPI numbers. Clean, minimal, professional. The dashboard looks like it's projecting holographic data.
TEXT: "SIGNALFLOW" in clean geometric sans-serif at top. Copy「データは語っている。聞こえているか。」in white, sharp typography below. Subtitle "AI-Powered Analytics Platform" small at bottom.
"""
    },
    {
        "id": "A2_dataflow",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Abstract data streams — glowing blue light particles flowing in organized streams against dark navy. Like a river of data. Beautiful, almost artistic. Think Ryoji Ikeda meets corporate.
TEXT: "SIGNALFLOW" bold at top. Copy「データは語っている。聞こえているか。」in white, clean typography. The text sits in a clear zone while data flows around it.
"""
    },
    {
        "id": "B1_grid",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Pure Swiss Design grid layout. Dark navy background with precise blue grid lines. Minimal geometric shapes (circles, rectangles) in #1058C4 and #67CAFF placed with mathematical precision. Clean, structured, confident.
TEXT: "SIGNALFLOW" in large, bold geometric sans-serif. Copy「データは語っている。聞こえているか。」in a clear grid zone. Everything aligned to the grid perfectly.
"""
    },
    {
        "id": "B2_signal",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: A single dramatic signal wave/pulse — like an audio waveform or heartbeat monitor — in bright #67CAFF against pure dark navy. One continuous line that peaks dramatically in the center. Minimal, powerful, symbolic.
TEXT: "SIGNALFLOW" next to or above the signal line. Copy「データは語っている。聞こえているか。」below. Clean, centered composition.
"""
    },
    {
        "id": "C1_executive",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Confident businessman in a modern office, looking at a large screen showing data analytics. Dark, moody lighting with blue accent light from the screen. Professional, authoritative atmosphere.
TEXT: "SIGNALFLOW" in clean sans-serif at top. Copy「データは語っている。聞こえているか。」overlaid in white. Subtle "Make Data Speak" tagline.
"""
    },
    {
        "id": "C2_meeting",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Modern glass meeting room, team looking at a large screen with data visualization. Blue-tinted lighting. The data on screen is glowing and organized. Professional, collaborative atmosphere.
TEXT: "SIGNALFLOW" at top. Copy「データは語っている。聞こえているか。」in bold white text overlaid on the scene.
"""
    },
    {
        "id": "D1_minimal",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Ultra-minimal. Pure dark navy (#0a1628) background. Only one small glowing blue dot in the center, emanating subtle concentric rings — like a signal being broadcast. Nothing else. Maximum negative space.
TEXT: "SIGNALFLOW" large and bold at the top. Copy「データは語っている。聞こえているか。」centered below the dot. Pure typography power on dark background.
"""
    },
    {
        "id": "D2_split",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Split design — left half is pure dark navy with white text, right half shows a blue-tinted data visualization (network graph, connected nodes). Clean geometric dividing line.
TEXT: Left side: "SIGNALFLOW" bold at top, Copy「データは語っている。聞こえているか。」in white. Right side: visual data with subtle "AI Analytics" label.
"""
    },
]

# ========== TYPOGRAPHY PLAY 8枚 ==========
typo = [
    {
        "id": "A1t_dashboard_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Dark dashboard UI with glowing blue data visualizations.
TYPOGRAPHY PLAY: The copy「データは語っている。聞こえているか。」uses EXTREME size contrast. 「データ」is MASSIVE (fills 40% of frame) in bold white. 「は語っている。」is tiny underneath. 「聞こえているか。」is medium-sized, positioned like a challenge/provocation. "SIGNALFLOW" sharp at top. The text IS the design.
"""
    },
    {
        "id": "A2t_dataflow_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Flowing data streams of blue light particles on dark navy.
TYPOGRAPHY PLAY: The copy「データは語っている。聞こえているか。」is INTEGRATED into the data flow — the characters are made of the same blue light particles as the data streams. The text IS the data. "SIGNALFLOW" in solid white at top. Text and visual are one.
"""
    },
    {
        "id": "B1t_grid_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Swiss Design grid on dark navy.
TYPOGRAPHY PLAY: The copy「データは語っている。聞こえているか。」is placed in a strict GRID SYSTEM — each word occupies its own grid cell. Different sizes per cell. 「聞こえているか。」breaks out of the grid slightly — the only element that breaks the rules. Rebellion within structure. "SIGNALFLOW" perfectly aligned.
"""
    },
    {
        "id": "B2t_signal_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Signal waveform line on dark navy.
TYPOGRAPHY PLAY: The copy「データは語っている。聞こえているか。」follows the SHAPE of the signal wave — text rises and falls with the waveform. When the signal peaks, 「聞こえているか。」is at the highest point, largest. "SIGNALFLOW" clean at top.
"""
    },
    {
        "id": "C1t_exec_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Businessman with data screen, moody blue lighting.
TYPOGRAPHY PLAY: 「聞こえているか。」is the BIGGEST text — a direct challenge to the viewer, positioned prominently. 「データは語っている。」is smaller, like context. The text feels like a personal confrontation from the executive in the image. "SIGNALFLOW" subtle.
"""
    },
    {
        "id": "C2t_meeting_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Team meeting with data screen.
TYPOGRAPHY PLAY: The copy is arranged as a VERTICAL COLUMN on the right side — Japanese vertical text reading top to bottom. 「データは語っている。聞こえているか。」Each character stacked vertically. Clean, editorial, magazine-style. "SIGNALFLOW" horizontal at bottom.
"""
    },
    {
        "id": "D1t_minimal_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Ultra-minimal dark navy with single glowing blue dot.
TYPOGRAPHY PLAY: GIANT NEGATIVE SPACE — the copy「データは語っている。聞こえているか。」is the ONLY visual element besides the dot. Text takes up 80% of the frame. HUGE bold white text. The dot sits between 「語っている。」and「聞こえているか。」like a period/signal point. "SIGNALFLOW" tiny at bottom. Text IS the entire design.
"""
    },
    {
        "id": "D2t_split_typo",
        "prompt": f"""{BRAND}
Create a premium banner ad (1080x1080px):
VISUAL: Split layout.
TYPOGRAPHY PLAY: Left half (dark navy): 「データは」in sky blue #67CAFF, HUGE. Right half (white): 「語っている。」in dark navy #0a1628, HUGE. Below spanning full width: 「聞こえているか。」in #1058C4, medium. The split represents data (left) and insight (right). "SIGNALFLOW" centered at top spanning both halves.
"""
    },
]

all_variants = base + typo
for i, v in enumerate(all_variants):
    section = "BASE" if i < 8 else "TYPO"
    num = i + 1 if i < 8 else i - 7
    total = 8
    print(f"\n{'='*60}")
    print(f"[{section} {num}/{total}] Generating {v['id']}...")
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
                path = os.path.join(OUT, f"sf_{v['id']}.png")
                with open(path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"✅ Saved: sf_{v['id']}.png")
                saved = True
            elif part.text:
                print(f"📝 {part.text[:150]}")
        
        if not saved:
            print("⚠️ No image generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(3)

print("\n🎉 SIGNALFLOW — 16 banners complete!")

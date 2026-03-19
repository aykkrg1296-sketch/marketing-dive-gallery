#!/usr/bin/env python3
"""
MARKETING DIVE 適性テスト バナー 20枚生成
パクさんリファレンス型 × strategy.json × Nano Banana Pro（Gemini一発生成）
"""

import subprocess, os, time, json

# === ENV ===
def _load_env_all():
    """zshrcから全環境変数を一括読み込み"""
    try:
        r = subprocess.run(
            ['zsh', '-c', 'source ~/.zshrc 2>/dev/null; env'],
            capture_output=True, text=True, timeout=10
        )
        for line in r.stdout.splitlines():
            if '=' in line:
                k, _, v = line.partition('=')
                if k and v and k in ('GOOGLE_API_KEY','GEMINI_API_KEY_1','GEMINI_API_KEY_2','GEMINI_API_KEY_3'):
                    os.environ[k] = v
    except:
        pass

_load_env_all()

from google import genai
from google.genai import types

# GOOGLE_API_KEY を優先
API_KEYS = []
gkey = os.environ.get('GOOGLE_API_KEY','').strip()
if gkey:
    API_KEYS.append(gkey)
for i in range(1,4):
    k = os.environ.get(f'GEMINI_API_KEY_{i}','').strip()
    if k and k not in API_KEYS:
        API_KEYS.append(k)

if not API_KEYS:
    print("❌ APIキーが見つかりません")
    exit(1)

clients = [genai.Client(api_key=k) for k in API_KEYS]
print(f"✅ Gemini APIキー: {len(clients)}本")

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = script_dir
banner_dir = os.path.join(out_dir, 'banners')
spec_dir = os.path.join(out_dir, 'specs')
os.makedirs(banner_dir, exist_ok=True)
os.makedirs(spec_dir, exist_ok=True)

# === カラーパレット ===
# primary: #1058C4 (深海ブルー)
# secondary: #67CAFF (明るいブルー)
# accent1: #A7FFFB (シアン)
# accent2: #FF6600 (オレンジ)
# warm1: #FFC61C (ゴールド)
# warm2: #FFE500 (イエロー)

# === 20枚のバナースペック（パクさんの型×MARKETING DIVEコンセプト）===
banner_specs = [
    # --- 歓迎フック（5枚）---
    {
        "index": 1,
        "type": "感情直撃×深海KV型",
        "hook": "歓迎",
        "headline": "あなたを、迎えにきた",
        "sub": "マーケティング適性テスト — 無料",
        "cta": "適性を診断する",
        "visual": "A dark deep ocean scene. A glowing golden invitation letter floats in the center of the deep blue water, radiating warm golden light through the dark water. A silhouette of a person reaching toward the invitation from below. Deep navy blue (#1058C4) water with caustic light rays. The invitation emits warm gold (#FFC61C) particles floating upward. Cinematic, atmospheric, dreamlike quality. Fantasy RPG aesthetic.",
        "text_style": "Large bold white Japanese headline 'あなたを、迎えにきた' positioned top-center, taking up 30% of the image width. Subtitle 'マーケティング適性テスト — 無料' in smaller white text below. CTA button '適性を診断する' in orange (#FF6600) rounded rectangle at bottom-center. 'MARKETING DIVE' small logo text at top-right corner in white.",
        "hypothesis": "愛ベースの感情直撃コピーは夜のSNSスクロールでCTR最高値を出すか"
    },
    {
        "index": 2,
        "type": "RPGゲート×冒険型",
        "hook": "歓迎",
        "headline": "ようこそ、この世界へ",
        "sub": "3分で始まる冒険",
        "cta": "冒険を始める",
        "visual": "A massive ornate fantasy gate half-open, brilliant warm light (#FFC61C, #FFE500) pouring through the gap into dark surroundings. The gate has intricate deep-sea themed carvings (coral, fish, waves). Beyond the gate, a vibrant luminous underwater fantasy world is visible. Dark blue (#1058C4) atmosphere on this side, golden light on the other side. RPG game aesthetic, epic scale.",
        "text_style": "Bold white Japanese headline 'ようこそ、この世界へ' at top, large and commanding. '3分で始まる冒険' in cyan (#A7FFFB) below. CTA '冒険を始める' in warm gold button at bottom. 'MARKETING DIVE' logo at top-right, small white.",
        "hypothesis": "RPGゲート演出はゲーム経験のある30代男性の冒険心をトリガーするか"
    },
    {
        "index": 3,
        "type": "招待状クローズアップ×パーソナル型",
        "hook": "歓迎",
        "headline": "この招待状は、あなた宛て",
        "sub": "マーケの世界が待っている",
        "cta": "開封する",
        "visual": "Close-up of elegant hands holding a beautiful wax-sealed invitation letter that glows with soft golden light. The letter is partially opened, light spilling out. Background is deep dark blue (#1058C4) with subtle light particles. Warm, intimate atmosphere. The wax seal has a subtle compass/dive motif. Soft bokeh in background.",
        "text_style": "Japanese headline 'この招待状は、あなた宛て' in bold white, positioned top area. 'マーケの世界が待っている' smaller below in light blue (#67CAFF). CTA '開封する' in orange (#FF6600) button at bottom. 'MARKETING DIVE' small logo top-right.",
        "hypothesis": "パーソナル感（あなた宛て）はCTRとCVR両方に効くか"
    },
    {
        "index": 4,
        "type": "極短コピー×ミニマルKV型",
        "hook": "歓迎",
        "headline": "待ってたよ",
        "sub": "マーケティング適性テスト",
        "cta": "無料で診断する",
        "visual": "Minimalist deep ocean scene. Single glowing invitation letter centered, floating in perfectly still dark blue (#1058C4) water. Gold (#FFC61C) particles rising from the letter like fireflies. No other elements. Clean, elegant, breathtaking simplicity. The letter is the only source of light. Vertical light rays from above barely visible.",
        "text_style": "Very large bold white Japanese text '待ってたよ' centered, extremely prominent, taking 40% width. Clean sans-serif font. 'マーケティング適性テスト' in small light blue (#A7FFFB) text below. CTA '無料で診断する' in orange button at bottom. 'MARKETING DIVE' tiny at top-right.",
        "hypothesis": "極短コピー（3文字）はスクロール中の拇指停止率を最大化するか"
    },
    {
        "index": 5,
        "type": "席空け×具象歓迎型",
        "hook": "歓迎",
        "headline": "あなたの席、空けてある",
        "sub": "MARKETING DIVE 適性テスト",
        "cta": "席に着く",
        "visual": "Underwater fantasy banquet scene. A long luminous table set deep in the ocean, one empty chair with a spotlight of golden light on it, other seats occupied by glowing silhouettes. Bioluminescent elements, coral chandeliers, floating light particles. Deep blue (#1058C4) with warm gold (#FFC61C) highlights on the empty seat. Magical dinner party underwater.",
        "text_style": "Bold white headline 'あなたの席、空けてある' at top. 'MARKETING DIVE 適性テスト' in light blue below. CTA '席に着く' in gold button at bottom. Logo top-right.",
        "hypothesis": "具象的な歓迎（席が用意されている）は抽象的歓迎より行動を促すか"
    },
    # --- 適性フック（5枚）---
    {
        "index": 6,
        "type": "才能覚醒×光芒型",
        "hook": "適性",
        "headline": "あなたの才能、招待します",
        "sub": "3分のマーケティング適性テスト",
        "cta": "才能を確かめる",
        "visual": "A glowing crystal-like gem floating in dark deep water, radiating brilliant cyan (#A7FFFB) and gold (#FFC61C) light. An invitation letter unfolds around the gem like wings. The gem represents hidden talent. Deep navy (#1058C4) background with dramatic light rays. Ethereal, magical atmosphere. The gem has internal fire.",
        "text_style": "Large white headline 'あなたの才能、招待します' at top. '3分のマーケティング適性テスト' in cyan below. CTA '才能を確かめる' orange button at bottom. 'MARKETING DIVE' top-right.",
        "hypothesis": "才能訴求は自己肯定欲求が強いENFPタイプのCTRを上げるか"
    },
    {
        "index": 7,
        "type": "覚醒×石像ひび割れ型",
        "hook": "適性",
        "headline": "眠れる才能、起こしにきた",
        "sub": "マーケティング適性テスト",
        "cta": "目覚めさせる",
        "visual": "A stone statue of a human figure underwater, cracking open with brilliant golden light (#FFC61C) streaming through the cracks. The figure is breaking free. Dark deep blue (#1058C4) ocean surrounds. Gold particles and light beams escape through every crack. Dark fantasy aesthetic, powerful awakening moment. Dramatic chiaroscuro lighting.",
        "text_style": "Bold white headline '眠れる才能、起こしにきた' at top, large text. 'マーケティング適性テスト' in cyan (#67CAFF) below. CTA '目覚めさせる' in orange button. 'MARKETING DIVE' logo top-right.",
        "hypothesis": "覚醒メタファーは「持て余してる」N1の行動意欲を引き出すか"
    },
    {
        "index": 8,
        "type": "数字ドカン×ポータル型",
        "hook": "適性",
        "headline": "3分で、才能が目覚める",
        "sub": "無料マーケティング適性テスト",
        "cta": "今すぐ診断する",
        "visual": "A giant luminous number '3' floating in deep ocean water, and inside the number is a portal showing a vibrant colorful world of marketing (graphs, creative sparks, connections). The number itself is a gateway. Deep blue (#1058C4) surroundings, the number glows with warm gold (#FFC61C) edges. Magical portal concept.",
        "text_style": "Large bold white '3分で、才能が目覚める' headline, the '3' extra large. '無料マーケティング適性テスト' smaller in light blue. CTA '今すぐ診断する' orange button at bottom. 'MARKETING DIVE' top-right.",
        "hypothesis": "数字ファースト（3分）は行動ハードルを下げてCVR向上するか"
    },
    {
        "index": 9,
        "type": "直感肯定×価値転換型",
        "hook": "適性",
        "headline": "その直感、マーケの才能です",
        "sub": "適性テストで確かめてみない？",
        "cta": "無料で診断する",
        "visual": "Abstract visualization of intuition as glowing neural pathways and light connections in deep blue (#1058C4) space. Golden (#FFC61C) sparks and connections forming a brain-like pattern. Some connections lead to marketing icons (lightbulb, chart, megaphone) made of light. Beautiful, scientific yet magical. Data visualization meets deep sea bioluminescence.",
        "text_style": "White headline 'その直感、マーケの才能です' bold at top. '適性テストで確かめてみない？' in light blue below, casual tone. CTA '無料で診断する' orange button. 'MARKETING DIVE' logo top-right.",
        "hypothesis": "日常体験の再定義（直感→才能）はN1の自己認識を変えてCTR向上するか"
    },
    {
        "index": 10,
        "type": "宝探し×RPG冒険型",
        "hook": "適性",
        "headline": "才能は、見つけた人のもの",
        "sub": "マーケティング適性テスト",
        "cta": "宝を探しに行く",
        "visual": "Underwater treasure scene. A glowing treasure chest half-buried in ocean floor sand, partially open with golden light streaming out. An old treasure map unfolds nearby, made of luminous material. Coral and sea life surround the scene. Deep blue (#1058C4) water, gold (#FFC61C) treasure light. RPG adventure game aesthetic, treasure hunt excitement.",
        "text_style": "Bold white '才能は、見つけた人のもの' at top. 'マーケティング適性テスト' in cyan. CTA '宝を探しに行く' gold button. 'MARKETING DIVE' top-right.",
        "hypothesis": "RPG宝探しメタファーはENFPの冒険心×限定感でCTR向上するか"
    },
    # --- 面白さフック（5枚）---
    {
        "index": 11,
        "type": "カジュアル誘い×トンネル型",
        "hook": "面白さ",
        "headline": "面白いほうへ、おいで",
        "sub": "マーケティング適性テスト",
        "cta": "面白い方へ行く",
        "visual": "Looking through a dark tunnel toward a brilliant, colorful exit. The far end shows a vibrant underwater fantasy world full of light, color, and movement. A small silhouette stands at the entrance, about to step through. Dark navy (#1058C4) tunnel walls, brilliant warm light (#FFC61C, #FFE500, #FF6600) at the exit. Contrast between dark present and bright future.",
        "text_style": "Large bold white '面白いほうへ、おいで' at top, friendly casual tone. 'マーケティング適性テスト' in light blue below. CTA '面白い方へ行く' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "カジュアルな誘い口調はフォーマルなビジネス訴求よりCTR高いか"
    },
    {
        "index": 12,
        "type": "壮大ゲート×入口演出型",
        "hook": "面白さ",
        "headline": "最高に面白い入口",
        "sub": "マーケティングの世界への招待状",
        "cta": "入場する",
        "visual": "A magnificent underwater gate/arch made of coral and luminous crystals, towering in the deep ocean. Beyond the gate, a mesmerizing world of colorful bioluminescent creatures, floating data visualizations, and light shows. The gate itself is ornate with golden (#FFC61C) trim. Deep blue (#1058C4) ocean, the world beyond is alive with color (#A7FFFB, #FF6600, #FFE500). Grand scale, awe-inspiring.",
        "text_style": "Bold white '最高に面白い入口' large at top. 'マーケティングの世界への招待状' in cyan below. CTA '入場する' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "テスト＝面白い入口の再定義はテスト忌避層の心理バリアを下げるか"
    },
    {
        "index": 13,
        "type": "禁断フレーズ×渦巻き型",
        "hook": "面白さ",
        "headline": "知ったら最後、戻れない",
        "sub": "マーケティングの沼へようこそ",
        "cta": "沼に入る",
        "visual": "A mesmerizing spiral vortex in deep ocean water, pulling everything toward a brilliant glowing center. The spiral is made of bioluminescent particles in blue (#67CAFF) and gold (#FFC61C). The center glows intensely white-gold. Dark navy (#1058C4) edges. Hypnotic, addictive visual pattern. Cannot look away. The gravitational pull is visible.",
        "text_style": "Bold white '知ったら最後、戻れない' at top, dramatic font. 'マーケティングの沼へようこそ' in gold (#FFC61C) below. CTA '沼に入る' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "禁断フレーズ（戻れない）は好奇心ドライブをトリガーしてCTR向上するか"
    },
    {
        "index": 14,
        "type": "鍵穴覗き見×低コミット型",
        "hook": "面白さ",
        "headline": "一度覗いたら、ハマる世界",
        "sub": "3分で分かるマーケ適性",
        "cta": "覗いてみる",
        "visual": "View through an ornate golden keyhole. Through the keyhole, a vivid colorful underwater marketing world is visible - full of light, floating graphs, creative sparks, and warm glow. The keyhole side is dark. Sharp contrast between the dark mystery and bright discovered world. Gold (#FFC61C) keyhole frame, deep blue darkness (#1058C4), vibrant world inside.",
        "text_style": "White bold '一度覗いたら、ハマる世界' at top. '3分で分かるマーケ適性' in light blue below. CTA '覗いてみる' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "低コミットメント入口（覗く）はCVR向上に効くか"
    },
    {
        "index": 15,
        "type": "コンセプト直球×ポップアップ型",
        "hook": "面白さ",
        "headline": "マーケの世界への招待状",
        "sub": "適性テスト、始まる",
        "cta": "招待を受ける",
        "visual": "A large beautiful invitation letter in the center, opened up like a pop-up book. From inside, 3D elements of the marketing world spring out: tiny glowing charts, creative lightbulbs, connected people figures, all made of light and color. Deep blue (#1058C4) background. The pop-up elements glow in warm tones (#FFC61C, #FF6600, #A7FFFB). Playful, whimsical, surprising.",
        "text_style": "Bold white 'マーケの世界への招待状' at top. '適性テスト、始まる' in cyan. CTA '招待を受ける' gold button. 'MARKETING DIVE' top-right.",
        "hypothesis": "コンセプト直球コピー（招待状）は認知フェーズのインプレッション効率を上げるか"
    },
    # --- 共感フック（5枚）---
    {
        "index": 16,
        "type": "N1痛み直撃×深夜デスク型",
        "hook": "共感",
        "headline": "その発想力、持て余してない？",
        "sub": "マーケティング適性テスト",
        "cta": "適性を診断する",
        "visual": "A person sitting alone at a desk at night, illuminated only by a laptop screen and a warm desk lamp. The window shows a dark city skyline with scattered lights. The person looks thoughtful, resting chin on hand. On the desk, crumpled papers and coffee cup. But from their head, subtle golden (#FFC61C) light particles float upward - unused potential escaping. Moody, intimate, relatable. Deep blue (#1058C4) night atmosphere.",
        "text_style": "Large bold white 'その発想力、持て余してない？' at top, question format. 'マーケティング適性テスト' in light blue. CTA '適性を診断する' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "N1の痛みの直接言語化は共感フックとしてCTR効率が最も良いか"
    },
    {
        "index": 17,
        "type": "内面語×窓辺内省型",
        "hook": "共感",
        "headline": "このままでいいのかな",
        "sub": "その答え、3分で分かるかも",
        "cta": "答えを見つける",
        "visual": "A contemplative scene at a window at night. Looking out at city lights through slightly foggy glass. Reflection of a person visible in the window. A smartphone screen glows softly in the foreground, slightly out of focus. The mood is quiet introspection. Deep navy blue (#1058C4) night sky, warm orange (#FF6600) city lights in distance. Soft, cinematic, melancholic beauty.",
        "text_style": "Large white 'このままでいいのかな' at center, as if it's the person's inner voice. 'その答え、3分で分かるかも' in light blue below, gentle. CTA '答えを見つける' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "N1の内面語をそのまま使う共感コピーはスクロール停止率最高か"
    },
    {
        "index": 18,
        "type": "モヤモヤ肯定×光る粒子型",
        "hook": "共感",
        "headline": "そのモヤモヤ、才能の証拠",
        "sub": "マーケティング適性テスト",
        "cta": "証拠を確かめる",
        "visual": "An abstract scene in deep water. Misty, foggy, unclear shapes. But within the fog, countless tiny golden (#FFC61C) light particles are scattered - hidden treasures within confusion. The fog is dark blue (#1058C4), but the particles create a beautiful pattern. The fog is transforming into something beautiful. The particles are forming a constellation-like pattern.",
        "text_style": "Bold white 'そのモヤモヤ、才能の証拠' at top. 'マーケティング適性テスト' in light blue. CTA '証拠を確かめる' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "ネガティブ感情の肯定的再定義はN1の自己肯定感を刺激してCTR向上するか"
    },
    {
        "index": 19,
        "type": "before/after対比×二分割型",
        "hook": "共感",
        "headline": "もっと面白い場所がある",
        "sub": "マーケティングの世界への招待状",
        "cta": "面白い場所を見る",
        "visual": "Split composition - top half is a gray, desaturated office scene (cubicle, fluorescent lights, boring). Bottom half is a vibrant, colorful underwater fantasy world full of golden light, bioluminescence, and wonder. The boundary between the two halves glows with a brilliant line of gold (#FFC61C) and cyan (#A7FFFB) light. Stark contrast between mundane and magical.",
        "text_style": "Bold white 'もっと面白い場所がある' centered at the boundary line. 'マーケティングの世界への招待状' in cyan below. CTA '面白い場所を見る' orange button at bottom. 'MARKETING DIVE' top-right.",
        "hypothesis": "before/after対比構図は転職潜在層の心理に最も効くか"
    },
    {
        "index": 20,
        "type": "混沌→秩序×収束型",
        "hook": "共感",
        "headline": "発想力の使い道、見つかる",
        "sub": "マーケティング適性テスト",
        "cta": "使い道を見つける",
        "visual": "Abstract visualization: scattered chaotic light fragments on the left side gradually converging into a single brilliant focused beam of light on the right side. The fragments are multi-colored (#67CAFF, #A7FFFB, #FFC61C, #FF6600) representing scattered ideas. They merge into a powerful golden (#FFC61C) beam pointing forward. Deep blue (#1058C4) background. Beautiful data visualization aesthetic meets deep sea.",
        "text_style": "Bold white '発想力の使い道、見つかる' at top. 'マーケティング適性テスト' in light blue. CTA '使い道を見つける' orange button. 'MARKETING DIVE' top-right.",
        "hypothesis": "痛み→解決の2ステップコピーはCVR（テスト開始率）を上げるか"
    },
]

# === 生成実行 ===
ok = ng = 0
total = len(banner_specs)

for spec in banner_specs:
    idx = spec['index']
    fn = f"banner_{idx:02d}.png"
    fp = os.path.join(banner_dir, fn)

    if os.path.exists(fp) and os.path.getsize(fp) > 10240:
        print(f"⏭️  Banner {idx:02d} — 既存スキップ")
        ok += 1
        continue

    # text_styleから 'MARKETING DIVE' ロゴ指示を除去（後で本物ロゴを合成するため）
    import re
    clean_text_style = re.sub(r"['\"]?MARKETING DIVE['\"]?\s*(small\s+)?logo\s*(text\s+)?(at\s+)?top[^.]*\.", "", spec['text_style'], flags=re.IGNORECASE)
    clean_text_style = re.sub(r"['\"]?MARKETING DIVE['\"]?\s+top-right\.?", "", clean_text_style, flags=re.IGNORECASE)

    # フルプロンプト組み立て
    prompt = f"""Create a professional 1:1 (1080x1080) Japanese advertisement banner for a marketing aptitude test.

[VISUAL]
{spec['visual']}

[TEXT OVERLAY - CRITICAL: Render all Japanese text perfectly, clearly legible, high contrast]
{clean_text_style}
IMPORTANT: Do NOT include any 'MARKETING DIVE' text or logo. Leave the top-right corner empty - a real logo will be added later.

[QUALITY]
- Professional advertisement quality, not stock photo
- All Japanese characters must be perfectly rendered, clean modern sans-serif
- Sufficient contrast between text and background
- No text cut off at edges (maintain 5% safe margin)
- No watermarks, no blurry text, no overlapping text
- No English translations of Japanese text
- Do NOT render 'MARKETING DIVE' text anywhere on the image
- Color palette: deep blue #1058C4, cyan #67CAFF #A7FFFB, orange #FF6600, gold #FFC61C #FFE500
"""

    print(f"\n🎨 Banner {idx:02d} [{spec['type']}] 「{spec['headline']}」...")

    generated = False
    for attempt in range(3):
        c = clients[(idx + attempt) % len(clients)]
        try:
            resp = c.models.generate_content(
                model='gemini-3-pro-image-preview',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text','Image']
                )
            )
            img = next((p.inline_data.data for p in resp.parts if p.inline_data), None)
            if not img or len(img) < 10240:
                print(f"  ⚠️ attempt {attempt+1}: 画像小さすぎ or 空")
                if attempt < 2:
                    time.sleep(3)
                continue
            with open(fp, 'wb') as f:
                f.write(img)
            print(f"  ✅ {fn} ({len(img)//1024}KB)")
            ok += 1
            generated = True
            break
        except Exception as e:
            print(f"  ❌ attempt {attempt+1}: {str(e)[:80]}")
            if attempt < 2:
                time.sleep(5)

    if not generated:
        ng += 1
        print(f"  ❌ Banner {idx:02d} 生成失敗")

    # スペック保存
    spec_path = os.path.join(spec_dir, f"banner_{idx:02d}_spec.json")
    with open(spec_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    time.sleep(2)

print(f"\n{'='*50}")
print(f"=== 生成結果: {ok}/{total} OK, {ng}/{total} NG ===")
print(f"{'='*50}")

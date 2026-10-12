import math
import random
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断 - Statistical & Cynical", page_icon="🎰", layout="centered"
)

# --- 0. CSVデータの読み込みと数値化パース ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('neta_master.csv')
        def parse_probability(text):
            text_str = str(text)
            if '1/36' in text_str:
                return 1/36 * 100
            if '432万分の1' in text_str or '0.000023%' in text_str:
                return 0.000023
            if '65万分の1' in text_str or '0.00015%' in text_str:
                return 0.00015
            if '1000兆分の1' in text_str:
                return 1e-12
            if '数百万分の1' in text_str or '0.00001%' in text_str:
                return 0.00001
            import re
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', text_str)
            if matches:
                return float(matches[0])
            ranges = re.findall(r'([0-9]+\.?[0-9]*)%?[〜~]([0-9]+\.?[0-9]*)%', text_str)
            if ranges:
                return (float(ranges[0][0]) + float(ranges[0][1])) / 2.0
            return 50.0
        
        df['prob_val'] = df['確率・数値'].apply(parse_probability)
        return df
    except Exception:
        return None

df_master = load_data()

# --- 1. デザイン用のカスタムCSS ＆ レイヤー設定 ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, p {
        font-family: 'DotGothic16', sans-serif !important;
    }
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    label, .stRadio p, .stNumberInput p, .stSelectbox p {
        color: #cbd5e1 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        position: relative;
        z-index: 10;
    }
    .stRadio > div {
        flex-direction: row !important;
        gap: 10px;
    }
    /* 背景「ざわ…」侵食レイヤー（最奥に固定） */
    .zawa-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .zawa-item {
        position: absolute;
        font-weight: 900;
        font-family: 'Yu Gothic', sans-serif;
        color: rgba(255, 51, 102, 0.15);
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. 状態判定（倍率ベース）と名言フレーズ・コメント、および「ざわ…」頻度の定義 ---
ZONE_DEFINITIONS = {
    "peaceful": {
        "title": "STAGE 1 : 慢心 / 平穏域 (WHITE)",
        "hp_percent": 100,
        "border_color": "#f8fafc",  # 白
        "accent_color": "#f8fafc",
        "hp_text_color": "#22c55e",  # 緑（ステージ1）
        "bg_color": "#111827",
        "quote": "狙い台…計画通り…！",
        "zawa_count": 0,
        "comments": [
            "「おっ、早めの当りですね！ まだ財布も心もノーダメージでウハウハな時間帯ですわ」",
            "「このスピード感で当たってくれると助かるんですけどねぇ。まあ、油断大敵ですよ」",
            "「サクッと初当りを引けてご機嫌なご様子。ここから連チャンを伸ばせるかが見せ所ですね」"
        ],
        "footers": [
            "※早い当りは嬉しいですが、持ち玉の維持こそが勝負の分かれ道です。",
            "※この調子でプラス域をキープしてさっさと逃げたいところですね。",
            "※確率の恩恵を素直に受け取っておきましょう。"
        ]
    },
    "caution": {
        "title": "STAGE 2 : 強がり / 警戒域 (BLUE)",
        "hp_percent": 75,
        "border_color": "#38bdf8",  # 青
        "accent_color": "#38bdf8",
        "hp_text_color": "#facc15",  # 黄（ステージ2）
        "bg_color": "#082f49",
        "quote": "まだあわてるような投資じゃない",
        "zawa_count": 0,
        "comments": [
            "「確率分母以内ですからね、まだまだ『まあまあ許容範囲内』ってところですわ」",
            "「『そろそろ当たるはず』……いやいや、分母以内ならまだ平常運転ですよ。気楽にいきましょう」",
            "「ここまでは想定内の挙動ですね。焦らず淡々とハンドルを握っていきましょうか」"
        ],
        "footers": [
            "※確率分母以内での当りは全体の約63%です。まだ普通の範囲内ですね。",
            "※ここから先が本当の地獄の始まり……なんて冗談ですけど、油断は禁物です。",
            "※財布のHPはまだ満タンに近いです。"
        ]
    },
    "yutime_ghost": {
        "title": "STAGE 3 : 屈辱 / 警告域 (YELLOW)",
        "hp_percent": 50,
        "border_color": "#facc15",  # 黄
        "accent_color": "#facc15",
        "hp_text_color": "#f97316",  # オレンジ（ステージ3）
        "bg_color": "#422006",
        "quote": "その日 パチンカーは思い出した<br>確率の妙に囚われていた屈辱を……",
        "zawa_count": 8,
        "comments": [
            "「うーん、分母を超えて2倍ハマりコースですか。まあ、パチンコ打ってりゃよくある日常風景ですね」",
            "<span>「『こんな時もあるさ』と自分に言い聞かせるフェーズですね。まだメンタルは折れてません？」</span>",
            "「ちょっと嫌な汗をかく頃合いですが、ここから一撃でまくる台も多いですからねえ」"
        ],
        "footers": [
            "※2倍ハマりに到達する確率は約13.5%です。まだまだよくある日常です。",
            "※「ここから取り返せばいいや」という甘い期待が泥沼の始まりです。",
            "※演出の派手さと裏腹に、財布の残高は着実に削られています。"
        ]
    },
    "deep": {
        "title": "STAGE 4 : 執着 / 深海トラウマ領域 (GREEN)",
        "hp_percent": 25,
        "border_color": "#22c55e",  # 緑
        "accent_color": "#22c55e",
        "hp_text_color": "#ef4444",  # 赤（ステージ4）
        "bg_color": "#052e16",
        "quote": "まだだ!まだ台が当たりたがっている!!",
        "zawa_count": 28,
        "comments": [
            "<span><span>「おや、3倍ハマり手前まで来ましたか。ちょっと雲行きが怪くなってきましたねぇ……」</span></span>",
            "「ここまで来ると『ここまで入れたんだからRUSH入れて取り返さないと割に合わない』って思考になりがちですね」",
            "「じっと耐える時間帯です。隣の連チャンを横目に見ながらメンタルを保てるかが勝負ですよ」"
        ],
        "footers": [
            "※3倍ハマりに到達する確率は約5%未満。そろそろ不穏な領域です。",
            "※サンクコスト効果に支配されていませんか？ 冷静になりましょう。",
            "※ハンドルを固定したところで、確率はあなたに微笑みません。"
        ]
    },
    "god": {
        "title": "STAGE 5 : 狂気 / 確率特異点 (RED)",
        "hp_percent": 5,
        "border_color": "#ef4444",  # 赤
        "accent_color": "#ef4444",
        "hp_text_color": "#ef4444",  # 赤（ステージ5）
        "bg_color": "#450a0a",
        "quote": "台が球を吐き出さない限り、止まるんじゃねぇぞ…",
        "zawa_count": 55,
        "comments": [
            "「出ました、3倍ハマり超の虚無ゾーン！ もはや当たろうが当たるまいが、ムキになってサンドに札を入れるだけの作業ですね」",
            "「ここまで来ると笑うしかありませんね！ 脳から変なアドレナリンが出ているのを感じませんか？」",
            "<span>「お疲れ様です。パチンコ屋のATMに多額の寄付をする尊いボランティア、見事な狂気っぷりですね！」</span>"
        ],
        "footers": [
            "※ここから当たる確率はごくわずか。完全な虚無との戦いです。",
            "※周囲の視線は同情、あるいは哀れみを含んだものに変わっています。",
            "※財布の命日へようこそ。撤退の二文字はすでに脳内から消えています。"
        ]
    },
}

# --- 3. タイトルとコントロールエリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center; letter-spacing: 2px; margin-bottom: 8px;'>🎰 パチンコ確率診断コア</h3>",
    unsafe_allow_html=True,
)

spec_options = {
    "甘デジ (1/99)": 99.9,
    "ライトミドル (1/199)": 199.8,
    "ミドル (1/319)": 319.6,
    "ラッキートリガー (1/349)": 349.0,
    "カスタム": 0.0,
}

selected_spec_name = st.selectbox("大当り確率", list(spec_options.keys()), index=2)
if selected_spec_name == "カスタム":
    p_denom = st.number_input("大当り確率の分母", min_value=1.1, value=319.6, step=0.1)
else:
    p_denom = spec_options[selected_spec_name]

# --- 回転数の入力機構（倍率選択 ＋ 自由入力） ---
rot_options = {
    "0.5倍": 0.5,
    "1倍 (分母)": 1.0,
    "2倍": 2.0,
    "3倍": 3.0,
    "4倍": 4.0,
    "5倍": 5.0,
    "自由入力": 0.0,
}

selected_rot_name = st.selectbox("ハマり回転数（倍率選択）", list(rot_options.keys()), index=2)

if selected_rot_name == "自由入力":
    max_limit = int(p_denom * 8)
    default_val = min(300, max_limit)
    current_rotation = st.number_input(
        "現在の回転数（自由入力）",
        min_value=0,
        max_value=max_limit,
        value=default_val,
        step=1
    )
else:
    multiplier = rot_options[selected_rot_name]
    current_rotation = int(p_denom * multiplier)
    st.markdown(f"<p style='font-size: 12px; color: #94a3b8; margin: -10px 0 10px 0;'>設定回転数: <b>{current_rotation} 回転</b> ({selected_rot_name})</p>", unsafe_allow_html=True)

# --- 4. 計算ロジック ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100
rotation_ratio = current_rotation / p_denom if p_denom > 0 else 0

# --- 5. 状態判定の決定 ---
if rotation_ratio < 0.31:
    zone_key = "peaceful"
elif rotation_ratio < 1.0:
    zone_key = "caution"
elif rotation_ratio < 2.0:
    zone_key = "yutime_ghost"
elif rotation_ratio < 3.0:
    zone_key = "deep"
else:
    zone_key = "god"

zone_data = ZONE_DEFINITIONS[zone_key]

# --- 6. CSVネタマッチング ---
if df_master is not None and len(df_master) > 0:
    df_master['diff'] = (df_master['prob_val'] - prob_ハマり).abs()
    closest_row = df_master.loc[df_master['diff'].idxmin()]
    approx_rate = str(closest_row.get('確率・数値', ''))
    comparison_text = str(closest_row.get('事象', '')) + "：" + str(closest_row.get('コメント', ''))
else:
    approx_rate = f"約 {prob_ハマり:.1f}%"
    comparison_text = "計算されたハマり確率に合致する日常の事象"

# --- 7. コメント・フッターのランダム選択（ハッシュシード利用） ---
hash_seed = int(prob_ハマり * 1000) % 3
comment_text = zone_data['comments'][hash_seed % len(zone_data['comments'])]
footer_cynic = zone_data['footers'][hash_seed % len(zone_data['footers'])]
quote_text = zone_data['quote']

# --- 8. 背景「ざわ…」演出の動的生成 ---
zawa_count = zone_data["zawa_count"]
if zawa_count > 0:
    zawa_html_list = []
    random.seed(int(current_rotation + p_denom))
    for i in range(zawa_count):
        top = random.randint(2, 95)
        left = random.randint(2, 95)
        size = random.uniform(0.9, 1.8) + (zawa_count * 0.005)
        deg = random.randint(-20, 20)
        text = "ざわ…" if i % 2 == 0 else "ざわ"
        zawa_html_list.append(
            f'<div class="zawa-item" style="top:{top}vh; left:{left}vw; font-size:{size}rem; transform:rotate({deg}deg);">{text}</div>'
        )
    zawa_container = f'<div class="zawa-container">{"".join(zawa_html_list)}</div>'
    st.markdown(zawa_container, unsafe_allow_html=True)

# --- 9. カード構築 ---
border_color = zone_data['border_color']
accent_color = zone_data['accent_color']
bg_color = zone_data['bg_color']
hp_percent = zone_data['hp_percent']
hp_text_color = zone_data['hp_text_color']

hp_bar_color = "#c2527f" 

card_html = f"""
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
<style>
* {{
    font-family: 'DotGothic16', sans-serif !important;
}}
</style>
<div style="border: 2px solid {border_color}; background-color: {bg_color}; color: #f8fafc; padding: 16px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.8); max-width: 500px; margin: 5px auto 0 auto; box-sizing: border-box; transition: background-color 0.4s ease, border-color 0.4s ease; position: relative;">
    
    <!-- 【一番上】至高の名言置換フレーズ枠 -->
    <div style="margin-bottom: 12px; text-align: center; padding: 6px 10px; background: rgba(0,0,0,0.2); border-bottom: 1px dashed rgba(255,255,255,0.15); border-radius: 4px;">
        <div style="font-size: 11px; color: #94a3b8; line-height: 1.4; letter-spacing: 0.5px; opacity: 0.85;">
            {quote_text}
        </div>
    </div>

    <!-- 【メイン主役】ハマり確率 -->
    <div style="background-color: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15); padding: 14px; border-radius: 6px; margin-bottom: 12px; text-align: center;">
        <div style="display: flex; align-items: baseline; justify-content: center; gap: 4px; margin: 4px 0; line-height: 1;">
            <span style="font-size: 13px; color: #94a3b8; letter-spacing: 1px;">ハマり確率：</span>
            <span style="font-size: 38px; color: {accent_color}; font-weight: bold;">{prob_ハマり:.2f}%</span>
        </div>
        
        <!-- 【補助情報】大当り確率と回転数 -->
        <div style="border-top: 1px dashed rgba(255,255,255,0.15); margin-top: 10px; padding-top: 8px; display: flex; justify-content: center; align-items: center; gap: 10px; font-size: 13px; color: #94a3b8; white-space: nowrap;">
            <span>大当り: <b style="color: #f8fafc; font-size: 13px;">1/{p_denom}</b></span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span>回転数: <b style="color: #f8fafc; font-size: 13px;">{current_rotation}</b> <span style="font-size: 11px; color: {accent_color};">({rotation_ratio:.1f}倍ハマり)</span></span>
        </div>
    </div>

    <!-- 【客観分析】同じ確率で起きる身近な出来事 -->
    <div style="background-color: rgba(0,0,0,0.45); border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; letter-spacing: 0.5px; margin-bottom: 3px;">
            <span>[ 同じ確率で起きる身近な出来事 ]</span>
            <span style="color: #38bdf8;">{approx_rate}</span>
        </div>
        <div style="font-size: 11px; color: #cbd5e1; line-height: 1.3;">
            <span style="color: #38bdf8;">>></span> {comparison_text}
        </div>
    </div>

    <!-- 【シニカルコメント枠】 -->
    <div style="margin-bottom: 10px;">
        <div style="display: flex; align-items: flex-start; background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px;">
            <div style="min-width: 36px; height: 36px; background-color: rgba(0,0,0,0.3); border: 1px dashed {accent_color}; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #94a3b8; margin-right: 8px; text-align: center;">
                [ICON]
            </div>
            <div style="font-size: 11px; color: #f1f5f9; line-height: 1.4;">
                {comment_text}
            </div>
        </div>
    </div>

    <!-- パズドラ風HPバー -->
    <div style="background-color: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="{hp_bar_color}" style="display: inline-block; vertical-align: middle; flex-shrink: 0;">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
        <div style="flex-grow: 1; background-color: rgba(0,0,0,0.6); height: 8px; border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.15);">
            <div style="width: {hp_percent}%; background-color: {hp_bar_color}; height: 100%; transition: width 0.4s ease;"></div>
        </div>
        <span style="font-size: 11px; font-weight: bold; color: {hp_text_color}; min-width: 65px; text-align: right;">{hp_percent}/100</span>
    </div>

    <!-- サブリミナル・フッター -->
    <div style="text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
        {footer_cynic}
    </div>

</div>
"""

components.html(card_html, height=620, scrolling=False)

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

# --- 1. デザイン用のカスタムCSS ＆ レイヤー修正 ---
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
    label, .stRadio p, .stNumberInput p {
        color: #cbd5e1 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        position: relative;
        z-index: 10; /* メインコンテンツを確実に手前にする */
    }
    /* ラジオボタンをコンパクトに横並びさせる調整 */
    .stRadio > div {
        flex-direction: row !important;
        gap: 10px;
    }
    /* 背景「ざわ…」侵食レイヤー（最奥に固定、クリックを邪魔しない） */
    .zawa-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0; /* メインより奥に配置 */
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

# --- 2. 状態判定（倍率ベース）と決定版名言フレーズの定義 ---
ZONE_DEFINITIONS = {
    "peaceful": {
        "title": "STAGE 1 : 慢心 (NORMAL)",
        "hp_percent": 100,
        "hp_status": "STABLE",
        "border_color": "#00ffcc",
        "accent_color": "#00ffcc",
        "bg_color": "#0d1b2a",
        "quote": "狙い台…計画通り…！",
        "zawa_count": 0,
        "footer": "※早い当りは嬉しいですが、持ち玉の維持こそが勝負の分かれ道です。"
    },
    "caution": {
        "title": "STAGE 2 : 強がり (CAUTION)",
        "hp_percent": 75,
        "hp_status": "CAUTION",
        "border_color": "#ffcc00",
        "accent_color": "#ffcc00",
        "bg_color": "#062318",
        "quote": "まだあわてるような投資じゃない",
        "zawa_count": 5,
        "footer": "※確率分母以内での当りは全体の約63%です。まだ普通の範囲内ですね。"
    },
    "yutime_ghost": {
        "title": "STAGE 3 : 屈辱 (WARNING)",
        "hp_percent": 50,
        "hp_status": "WARNING",
        "border_color": "#ff9900",
        "accent_color": "#ff9900",
        "bg_color": "#1e102f",
        "quote": "その日 パチンカーは思い出した<br>確率の妙に囚われていた屈辱を……",
        "zawa_count": 18,
        "footer": "※「ここから取り返せばいいや」という甘い期待が泥沼の始まりです。"
    },
    "deep": {
        "title": "STAGE 4 : 執着 (DEEP)",
        "hp_percent": 25,
        "hp_status": "DANGER",
        "border_color": "#ff3333",
        "accent_color": "#ff3333",
        "bg_color": "#2c150b",
        "quote": "まだだ！まだ台が当たりたがっている！！",
        "zawa_count": 35,
        "footer": "※サンクコスト効果に支配されていませんか？ 冷静になりましょう。"
    },
    "god": {
        "title": "STAGE 5 : 狂気 (SINGULARITY)",
        "hp_percent": 5,
        "hp_status": "CRITICAL",
        "border_color": "#ff0055",
        "accent_color": "#ff0055",
        "bg_color": "#2d0f0f",
        "quote": "台が球を吐き出さない限り、止まるんじゃねぇぞ…",
        "zawa_count": 55,
        "footer": "※財布の命日へようこそ。撤退の二文字はすでに脳内から消えています。"
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

# セッションステートで回転数を管理
if 'rotation_input' not in st.session_state or st.session_state.get('last_spec') != p_denom:
    st.session_state['rotation_input'] = min(300, int(p_denom * 6))
    st.session_state['last_spec'] = p_denom

# クイックジャンプ（0.5倍、1倍、2倍、3倍）
st.markdown("<p style='font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;'>▼ クイックジャンプ（倍率選択）</p>", unsafe_allow_html=True)
jump_option = st.radio(
    "クイックジャンプ",
    ["微調整", "0.5倍", "1倍(分母)", "2倍", "3倍"],
    horizontal=True,
    label_visibility="collapsed"
)

# 選択された倍率に応じて回転数を即座にセット
if jump_option == "0.5倍":
    st.session_state['rotation_input'] = int(p_denom * 0.5)
elif jump_option == "1倍(分母)":
    st.session_state['rotation_input'] = int(p_denom * 1.0)
elif jump_option == "2倍":
    st.session_state['rotation_input'] = int(p_denom * 2.0)
elif jump_option == "3倍":
    st.session_state['rotation_input'] = int(p_denom * 3.0)

# number_input 配置
max_limit = int(p_denom * 6)
current_rotation = st.number_input(
    "現在のハマり回転数（データカウンターの数字）",
    min_value=0,
    max_value=max_limit,
    step=1,
    key='rotation_input'
)

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

# --- 7. 背景「ざわ…」演出の動的生成（最奥に描画） ---
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

# --- 8. カード構築 ---
border_color = zone_data['border_color']
accent_color = zone_data['accent_color']
bg_color = zone_data['bg_color']
hp_percent = zone_data['hp_percent']
quote_text = zone_data['quote']
footer_cynic = zone_data['footer']

card_html = f"""
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
<style>
* {{
    font-family: 'DotGothic16', sans-serif !important;
}}
</style>
<div style="border: 2px solid {border_color}; background-color: {bg_color}; color: #f8fafc; padding: 16px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.8); max-width: 500px; margin: 5px auto 0 auto; box-sizing: border-box; transition: background-color 0.4s ease, border-color 0.4s ease; position: relative;">
    
    <!-- 【最上部】状態判定ヘッダー -->
    <div style="background-color: rgba(0,0,0,0.5); border-left: 4px solid {accent_color}; padding: 8px 12px; border-radius: 4px; margin-bottom: 12px;">
        <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">■ 現在の状態判定</div>
        <div style="font-size: 14px; color: {accent_color}; font-weight: bold; margin-top: 2px;">{zone_data['title']}</div>
    </div>

    <!-- 【メイン主役】ハマり確率 -->
    <div style="background-color: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15); padding: 14px; border-radius: 6px; margin-bottom: 12px; text-align: center;">
        <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 2px;">[ ハマり確率（ここまで当らない確率） ]</div>
        <div style="font-size: 38px; color: {accent_color}; font-weight: bold; line-height: 1.1; margin: 4px 0;">{prob_ハマり:.2f}%</div>
        
        <!-- 【補助情報】大当り確率と回転数 -->
        <div style="border-top: 1px dashed rgba(255,255,255,0.15); margin-top: 10px; padding-top: 8px; display: flex; justify-content: center; align-items: center; gap: 16px; font-size: 11px; color: #94a3b8;">
            <span>大当り確率: <b style="color: #f8fafc;">1/{p_denom}</b></span>
            <span style="color: rgba(255,255,255,0.2);">|</span>
            <span>回転数: <b style="color: #f8fafc; font-size: 13px;">{current_rotation}</b> <span style="font-size: 10px; color: {accent_color};">({rotation_ratio:.1f}倍ハマり)</span></span>
        </div>
    </div>

    <!-- 【軸1】無機質アナライザー -->
    <div style="background-color: rgba(0,0,0,0.45); border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 9px; color: #64748b; letter-spacing: 1px; margin-bottom: 3px;">
            <span>[ SYSTEM: OBJECTIVE_ANALYSIS ]</span>
            <span style="color: #38bdf8;">{approx_rate}</span>
        </div>
        <div style="font-size: 11px; color: #cbd5e1; line-height: 1.3;">
            <span style="color: #38bdf8;">>></span> {comparison_text}
        </div>
    </div>

    <!-- 【軸2】名言置換フレーズ枠 -->
    <div style="margin-bottom: 10px;">
        <div style="display: flex; align-items: center; background: rgba(0,0,0,0.35); border: 1px solid {accent_color}; padding: 12px; border-radius: 6px;">
            <div style="font-size: 12px; color: #f1f5f9; line-height: 1.5; text-align: center; width: 100%; font-weight: bold;">
                {quote_text}
            </div>
        </div>
    </div>

    <!-- 財布・メンタル HPゲージ -->
    <div style="background-color: rgba(0,0,0,0.3); padding: 6px 10px; border-radius: 6px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 2px;">
            <span>💳 財布 / メンタル残存値</span>
            <span>{zone_data['hp_status']} ({hp_percent}%)</span>
        </div>
        <div style="width: 100%; background-color: rgba(0,0,0,0.5); height: 4px; border-radius: 2px; overflow: hidden;">
            <div style="width: {hp_percent}%; background-color: {border_color}; height: 100%; transition: width 0.4s ease, background-color 0.4s ease;"></div>
        </div>
    </div>

    <!-- サブリミナル・フッター -->
    <div style="text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
        {footer_cynic}
    </div>

</div>
"""

components.html(card_html, height=580, scrolling=False)

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

# --- 1. デザイン用のカスタムCSS（DotGothic16フォント ＆ ダークテーマ） ---
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
    label, .stRadio p, .stSlider p {
        color: #cbd5e1 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. ゾーンごとのデータ・シニカルコメント定義 ---
ZONE_MESSAGES = {
    "peaceful": {
        "title": "平穏域 (NORMAL)",
        "comment": "まだ確率の収束を語るには早すぎる回転数です。財布のライフはまだ満タンです。",
        "footer_cynic": "※台の機嫌はあなたとは無関係に一定の確率で抽選し続けています。",
        "hp_percent": 100,
        "hp_status": "STABLE",
        "border_color": "#3b82f6",
        "accent_color": "#60a5fa",
    },
    "caution": {
        "title": "警戒域 (CAUTION)",
        "comment": "投資がかさみ、「そろそろ当たるはず」という正常性バイアスが顔を出す頃合いです。",
        "footer_cynic": "※確率に「そろそろ」という概念は存在しません。",
        "hp_percent": 60,
        "hp_status": "CAUTION",
        "border_color": "#10b981",
        "accent_color": "#34d399",
    },
    "yutime_ghost": {
        "title": "警告域 / 遊タイム非搭載 (WARNING)",
        "comment": "かつての基準であれば約 {yutime_rot}回転で救済されていましたが、現代の荒波スペックに慈悲はありません。",
        "footer_cynic": "※冷徹な液晶演出だけが、あなたの財布のHPを削っていきます。",
        "hp_percent": 30,
        "hp_status": "WARNING",
        "border_color": "#a855f7",
        "accent_color": "#c084fc",
    },
    "deep": {
        "title": "深海トラウマ領域 (DEEP)",
        "comment": "RUSH即抜けの絶望に比べれば可愛いもの……と言い聞かせなければ正気を保てない深度です。",
        "footer_cynic": "※ハンドルを固定したところで、数学的確率は1ミリも変動しません。",
        "hp_percent": 10,
        "hp_status": "DANGER",
        "border_color": "#f97316",
        "accent_color": "#fb923c",
    },
    "god": {
        "title": "確率特異点 / 神の領域 (SINGULARITY)",
        "comment": "数学的・統計的観点から言えば、レア事象を引き当てる才能の無駄遣いが発生しています。",
        "footer_cynic": "※周囲の視線は同情か、あるいは反面教師を見るような冷ややかなものです。",
        "hp_percent": 1,
        "hp_status": "CRITICAL",
        "border_color": "#ef4444",
        "accent_color": "#f87171",
    },
}

# --- 3. タイトルと選択エリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center; letter-spacing: 2px;'>🎰 パチンコ確率診断コア</h3>",
    unsafe_allow_html=True,
)

spec_options = {
    "甘デジ (1/99)": 99.9,
    "ライトミドル (1/199)": 199.8,
    "ミドル (1/319)": 319.6,
    "ラッキートリガー (1/349)": 349.0,
    "カスタム": 0.0,
}

selected_spec_name = st.selectbox("機種スペック", list(spec_options.keys()), index=2)

if selected_spec_name == "カスタム":
    p_denom = st.number_input("大当り確率の分母", min_value=1.1, value=319.6, step=0.1)
else:
    p_denom = spec_options[selected_spec_name]

# --- 4. スライダーによる回転数調整 ---
max_slider = int(p_denom * 6)
current_rotation = st.slider("現在のハマり回転数", min_value=0, max_value=max_slider, value=min(300, max_slider), step=10)

# --- 5. 計算ロジック ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100

# --- 6. ゾーン分岐 ---
if prob_ハマり > 50:
    zone_key = "peaceful"
elif prob_ハマり > 20:
    zone_key = "caution"
elif prob_ハマり > 10:
    zone_key = "yutime_ghost"
elif prob_ハマり > 1.0:
    zone_key = "deep"
else:
    zone_key = "god"

zone_data = ZONE_MESSAGES[zone_key]

comment_text = zone_data["comment"]
if zone_key == "yutime_ghost":
    yutime_rot = int(p_denom * 3)
    comment_text = comment_text.format(yutime_rot=yutime_rot)

# --- 7. CSVネタマッチング ---
if df_master is not None and len(df_master) > 0:
    df_master['diff'] = (df_master['prob_val'] - prob_ハマり).abs()
    closest_row = df_master.loc[df_master['diff'].idxmin()]
    approx_rate = str(closest_row.get('確率・数値', ''))
    comparison_text = str(closest_row.get('事象', '')) + "：" + str(closest_row.get('コメント', ''))
else:
    approx_rate = f"約 {prob_ハマり:.1f}%"
    comparison_text = "計算されたハマり確率に合致する日常の事象"

# --- 8. データ診断カードの構築（3段構成） ---
border_color = zone_data['border_color']
accent_color = zone_data['accent_color']
hp_percent = zone_data['hp_percent']

card_html = f"""
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
<style>
* {{
    font-family: 'DotGothic16', sans-serif !important;
}}
</style>
<div style="border: 2px solid {border_color}; background-color: #111827; color: #f8fafc; padding: 20px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); max-width: 500px; margin: 0 auto; box-sizing: border-box;">
    
    <!-- 第1段：データコア（スペック・回転数・確率） -->
    <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
            <span>スペック: <b>1/{p_denom}</b></span>
            <span>現在回転数: <b style="color: #fff;">{current_rotation}回転</b></span>
        </div>
        <div style="text-align: center; background-color: rgba(0,0,0,0.4); padding: 12px; border-radius: 6px;">
            <div style="font-size: 10px; color: {accent_color}; letter-spacing: 1px; text-transform: uppercase;">{zone_data['title']}</div>
            <div style="font-size: 38px; color: {accent_color}; font-weight: bold; line-height: 1.1; margin: 4px 0;">{prob_ハマり:.2f}%</div>
            <div style="font-size: 10px; color: #94a3b8;">（この回転数まで一度も当らない数学的確率）</div>
        </div>
    </div>

    <!-- 第2段：科学的・日常的比較ファクト -->
    <div style="background-color: rgba(0,0,0,0.3); border: 1px dashed rgba(255,255,255,0.15); padding: 10px 12px; border-radius: 6px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #38bdf8; margin-bottom: 4px;">
            <span>科学的スケール比較</span>
            <span>{approx_rate}</span>
        </div>
        <div style="font-size: 12px; color: #f1f5f9; line-height: 1.4;">
            • {comparison_text}
        </div>
    </div>

    <!-- 診断解説（ガローズユーモア） -->
    <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5; margin-bottom: 14px; background: rgba(255,255,255,0.02); padding: 10px; border-radius: 6px; border-left: 3px solid {accent_color};">
        {comment_text}
    </div>

    <!-- 財布・メンタル HPゲージ -->
    <div style="background-color: rgba(0,0,0,0.4); padding: 8px 10px; border-radius: 6px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 4px;">
            <span>💳 財布 / メンタル残存値</span>
            <span>{zone_data['hp_status']} ({hp_percent}%)</span>
        </div>
        <div style="width: 100%; background-color: #1e293b; height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="width: {hp_percent}%; background-color: {border_color}; height: 100%;"></div>
        </div>
    </div>

    <!-- 第3段：サブリミナル・フッター（冷徹な皮肉） -->
    <div style="text-align: center; font-size: 10px; color: #64748b; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px;">
        {zone_data['footer_cynic']}
    </div>

</div>
"""

components.html(card_html, height=520, scrolling=False)

import math
import random
import pandas as pd
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断 - おみくじEdition", page_icon="🎰", layout="centered"
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

# --- 1. デザイン用のカスタムCSS（DotGothic16フォント ＆ おみくじ風スタイル） ---
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

# --- 2. ゾーンごとのメッセージ・演出定義（おみくじ風） ---
ZONE_MESSAGES = {
    "peaceful": {
        "title": "小吉（平穏の領域）",
        "omikuji_luck": "平穏",
        "comment": "まだ慌てるような時間じゃない。財布の紐はしっかり締まっています。",
        "footer_cynic": "※台の機嫌はあなたとは無関係に変わりません。",
        "hp_percent": 100,
        "hp_status": "NORMAL",
        "card_bg": "#111827",
        "border_color": "#3b82f6", # 青 (平和)
        "accent_color": "#60a5fa",
    },
    "caution": {
        "title": "中吉（ざわ… ざわ…）",
        "omikuji_luck": "微悶絶",
        "comment": "少し財布の紐がキュッとなる頃合い。深呼吸してコーヒーでもどうぞ。",
        "footer_cynic": "※「もしかして当たるのでは？」という予感は大体外れます。",
        "hp_percent": 60,
        "hp_status": "CAUTION",
        "card_bg": "#111827",
        "border_color": "#10b981", # 緑
        "accent_color": "#34d399",
    },
    "yutime_ghost": {
        "title": "吉のあやかし（幻の遊タイム）",
        "omikuji_luck": "幻影",
        "comment": "昔の基準なら【約 {yutime_rot}回転】で助かってましたね……（遠い目）",
        "footer_cynic": "※現代の台に救済の幻影を求めてはいけません。",
        "hp_percent": 30,
        "hp_status": "WARNING",
        "card_bg": "#1e1b4b",
        "border_color": "#a855f7", # 紫
        "accent_color": "#c084fc",
    },
    "deep": {
        "title": "凶（深海トラウマ領域）",
        "omikuji_luck": "深海",
        "comment": "RUSH即抜けの虚しさに比べれば、このハマりなど微風……と言い聞かせる頃。",
        "footer_cynic": "※ハンドルを固定しても運勢は固定されません。",
        "hp_percent": 10,
        "hp_status": "DANGER",
        "card_bg": "#431407",
        "border_color": "#f97316", # 赤
        "accent_color": "#fb923c",
    },
    "god": {
        "title": "大凶（歴史的絶望 / 神の領域）",
        "omikuji_luck": "神域",
        "comment": "もはや語るまい。300回転ハマりはホールのおばあちゃんにはアツくても、数学的にはただの38.8%デス（※もっとハマってます）。",
        "footer_cynic": "※店員も静観するこの空間で、真実（数学）を伝える唯一のアプリです。",
        "hp_percent": 1,
        "hp_status": "DEAD",
        "card_bg": "#450a0a",
        "border_color": "#ef4444", # 金/赤
        "accent_color": "#f87171",
    },
}

# --- 3. タイトルと選択エリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center; letter-spacing: 2px;'>🎰 パチンコおみくじ診断</h3>",
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

# コメント内のプレースホルダー展開
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

# --- 8. おみくじ風カードのHTML構築 ---
omikuji_html = f"""
<div style="
    border: 4px double {zone_data['border_color']}; 
    background-color: {zone_data['card_bg']}; 
    padding: 20px; 
    border-radius: 12px; 
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    max-width: 500px;
    margin: 0 auto;
">
    <!-- 【上段】おみくじヘッダー（運勢・ステータス） -->
    <div style="text-align: center; border-bottom: 1px dashed {zone_data['border_color']}; padding-bottom: 12px; margin-bottom: 14px;">
        <div style="font-size: 11px; color: #94a3b8; letter-spacing: 3px;">【 運 勢 判 定 】</div>
        <div style="font-size: 22px; color: {zone_data['accent_color']}; font-weight: bold; margin: 4px 0;">
            {zone_data['title']}
        </div>
        <div style="font-size: 11px; color: #cbd5e1;">
            スペック: <b>1/{p_denom}</b> ｜ 現在: <b style="color: #fff;">{current_rotation}回転</b>
        </div>
    </div>

    <!-- 【中段の核】 確率 ＆ 科学データ解説 -->
    <div style="text-align: center; background-color: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; margin-bottom: 14px;">
        <div style="font-size: 10px; color: #94a3b8; letter-spacing: 1px;">（この回転数まで当らない確率）</div>
        <div style="font-size: 40px; color: {zone_data['accent_color']}; font-weight: bold; line-height: 1.1; margin: 6px 0;">
            {prob_ハマり:.2f}%
        </div>
        
        <div style="margin-top: 10px; text-align: left; border-top: 1px solid rgba(255,255,255,0.1); pt: 8px; padding-top: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 10px; color: #38bdf8; margin-bottom: 2px;">
                <span>科学的比較ファクト</span>
                <span>{approx_rate}</span>
            </div>
            <div style="font-size: 12px; color: #f1f5f9; line-height: 1.4;">
                • {comparison_text}
            </div>
        </div>
    </div>

    <!-- 【解説・お告げ】 メインツッコミ -->
    <div style="font-size: 13px; color: #e2e8f0; line-height: 1.5; margin-bottom: 14px; text-align: center; background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px;">
        「{comment_text}」
    </div>

    <!-- 💳 財布/メンタル HPゲージ -->
    <div style="background-color: rgba(0,0,0,0.4); padding: 8px 10px; border-radius: 6px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 4px;">
            <span>💳 財布 / メンタル HP</span>
            <span>{zone_data['hp_status']} ({zone_data['hp_percent']}%)</span>
        </div>
        <div style="width: 100%; background-color: #1e293b; height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="width: {zone_data['hp_percent']}%; background-color: {zone_data['border_color']}; height: 100%;"></div>
        </div>
    </div>

    <!-- 【下段】サブリミナル・フッター（シュールな皮肉） -->
    <div style="text-align: center; font-size: 10px; color: #64748b; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 8px;">
        {zone_data['footer_cynic']}
    </div>
</div>
"""

st.markdown(omikuji_html, unsafe_allow_html=True)

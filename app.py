import math
import random
import pandas as pd
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断", page_icon="🎰", layout="centered"
)

# --- 0. CSVデータの読み込み ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv('neta_master.csv')
    except Exception:
        return None

df_master = load_data()

# --- 1. デザイン用のカスタムCSS（DotGothic16フォントの導入） ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, p {
        font-family: 'DotGothic16', sans-serif !important;
    }
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    label, .stRadio p, .stSlider p {
        color: #e2e8f0 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. ゾーンごとのメッセージ・演出定義 ---
ZONE_MESSAGES = {
    "peaceful": {
        "title": "まだ慌てるような時間じゃない",
        "neg_messages": [
            "まだ慌てるような時間じゃない。ここからが本番です。",
            "財布の紐はまだしっかり締まっています。平和な日常ですね。",
        ],
        "pos_messages": [
            "素晴らしい立ち上がり。この調子で宇宙の真理へ近づきましょう。",
            "穏やかな風が吹いています。今日のあなたは一味違います。",
        ],
        "hp_percent": 100,
        "hp_status": "NORMAL (元気)",
        "card_bg": "#1e293b",
        "border_color": "#475569",
        "text_color": "#e2e8f0",
    },
    "caution": {
        "title": "ざわ… ざわ… ゾーン",
        "neg_messages": [
            "少し財布の紐がキュッとなる頃合い。深呼吸してコーヒーでもどうぞ。",
            "「もしかして、今日もやられる日なのでは…？」という悪寒が走り始める頃。",
        ],
        "pos_messages": [
            "ここからの巻き返しが一番ドラマチックなんです。期待値は上昇中。",
            "運命の歯車があなたの方を向き始めています。焦る必要はありません。",
        ],
        "hp_percent": 60,
        "hp_status": "CAUTION (注意)",
        "card_bg": "#1e293b",
        "border_color": "#64748b",
        "text_color": "#cbd5e1",
    },
    "yutime_ghost": {
        "title": "【幻の遊タイム】非搭載ゾーン",
        "neg_messages": [
            "昔の基準なら【約 {yutime_rot}回転】で助かってましたね……（遠い目）"
        ],
        "pos_messages": [
            "あえて遊タイムに頼らない。自力での引き戻しが試される黄金期です。"
        ],
        "hp_percent": 30,
        "hp_status": "WARNING (警告)",
        "card_bg": "#2e1065",
        "border_color": "#a855f7",
        "text_color": "#f3e8ff",
    },
    "deep": {
        "title": "領域展開（深海トラウマ）",
        "neg_messages": [
            "RUSHに入った瞬間3秒で駆け抜けたあの日の虚しさに比べれば、このハマりなど微風です。"
        ],
        "pos_messages": [
            "歴史に名を残す大当りのための『溜め』が完了しつつあります。神様もそろそろ目を覚ます頃。"
        ],
        "hp_percent": 10,
        "hp_status": "DANGER (瀕死)",
        "card_bg": "#431407",
        "border_color": "#ea580c",
        "text_color": "#ffedd5",
    },
    "god": {
        "title": "歴史に名を刻むレベル",
        "neg_messages": [
            "もはや語るまい。歴史に名を刻むレベルのレア体験デス。"
        ],
        "pos_messages": [
            "おめでとうございます。宇宙の確率変動を引き当てた『選ばれし者』の領域です。"
        ],
        "hp_percent": 1,
        "hp_status": "DEAD (精神崩壊)",
        "card_bg": "#450a0a",
        "border_color": "#ef4444",
        "text_color": "#fee2e2",
    },
}

# --- 3. タイトルと選択エリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center;'>🎰 パチンコ確率診断</h3>",
    unsafe_allow_html=True,
)

# モード選択（3択）
diag_mode = st.radio(
    "表示モード",
    ["両方味わう", "絶望に浸る", "狂気的に肯定される"],
    index=0,
    horizontal=True,
)

spec_options = {
    "甘デジ (1/99)": 99.9,
    "ライトミドル (1/199)": 199.8,
    "ミドル (1/319)": 319.6,
    "ラッキートリガー (1/349)": 349.0,
    "カスタム": 0.0,
}

selected_spec_name = st.radio(
    "機種スペックを選択",
    list(spec_options.keys()),
    index=2,
    horizontal=True,
)

if selected_spec_name == "カスタム":
    p_denom = st.number_input(
        "大当り確率の分母を入力 (例: 319.6)",
        min_value=0.0,
        max_value=10000.0,
        value=319.6,
        step=0.1,
    )
    if p_denom <= 1.0:
        st.error(
            "⚠️ エラー: 確率の分母は「1.0」より大きい数値を入力してください。"
        )
        st.stop()
else:
    p_denom = spec_options[selected_spec_name]

# --- 4. スライダーによる直感的な回転数調整 ---
max_slider = int(p_denom * 6)
step_val = 5 if p_denom <= 100 else 10

current_rotation = st.slider(
    "現在の回転数",
    min_value=0,
    max_value=max_slider,
    value=min(500, max_slider),
    step=step_val,
)

# --- 5. 計算ロジック ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100

# --- 6. 演出・ステータス分岐 ---
st.markdown("---")

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

status_title = zone_data["title"]
card_bg = zone_data["card_bg"]
border_color = zone_data["border_color"]
text_color = zone_data["text_color"]
hp_percent = zone_data["hp_percent"]
hp_status = zone_data["hp_status"]
image_url = (
    "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
)

# メッセージの取得
neg_comment = random.choice(zone_data["neg_messages"])
pos_comment = random.choice(zone_data["pos_messages"])

if zone_key == "yutime_ghost":
    yutime_rot = int(p_denom * 3)
    neg_comment = neg_comment.format(yutime_rot=yutime_rot)
    pos_comment = pos_comment.format(yutime_rot=yutime_rot)

# 比較データの取得（neta_master.csvから安全にランダム取得、なければフォールバック）
if df_master is not None and len(df_master) > 0:
    sample_row = df_master.sample(1).iloc[0]
    comparison_category = str(sample_row.get('ゾーン', '日常'))
    approx_rate = str(sample_row.get('確率・数値', ''))
    comparison_text = str(sample_row.get('事象', '')) + "：" + str(sample_row.get('コメント', ''))
else:
    comparison_category = "日常"
    approx_rate = "約 25%"
    comparison_text = "日常のちょっとした不運な出来事"

# --- 7. ラベルを排除したシームレスなカード構築 ---
content_html = ""

if diag_mode == "両方味わう":
    content_html += (
        f'<p style="font-size: 13px; color: #f1f5f9; line-height: 1.4;'
        f' margin-bottom: 6px; text-align: center;">{neg_comment}</p>'
    )
    content_html += (
        f'<p style="font-size: 13px; color: #fce7f3; line-height: 1.4;'
        f' margin-bottom: 10px; text-align: center; opacity: 0.9;">'
        f"{pos_comment}</p>"
    )
    comparison_display = f'<div style="margin-bottom: 4px;">• {comparison_text}</div>'
elif diag_mode == "絶望に浸る":
    content_html += (
        f'<p style="font-size: 13px; color: {text_color}; line-height: 1.4;'
        f' margin-bottom: 10px; text-align: center;">{neg_comment}</p>'
    )
    comparison_display = f'• {comparison_text}'
else:
    content_html += (
        f'<p style="font-size: 13px; color: {text_color}; line-height: 1.4;'
        f' margin-bottom: 10px; text-align: center;">{pos_comment}</p>'
    )
    comparison_display = f'• {comparison_text}'

card_html = (
    '<div style="border: 3px double '
    + border_color
    + "; background-color: "
    + card_bg
    + '; padding: 14px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">'
    '<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px; margin-bottom: 10px; font-size: 12px; color: #94a3b8;">'
    '<span>スペック: <b style="color: #f8fafc;">1 / '
    + str(p_denom)
    + "</b></span>"
    '<span>現在: <b style="color: #f8fafc;">'
    + str(current_rotation)
    + "回転</b></span>"
    "</div>"
    '<div style="text-align: center; margin-bottom: 8px;">'
    '<div style="font-size: 12px; color: '
    + text_color
    + '; text-transform: uppercase; letter-spacing: 2px;">'
    + status_title
    + "</div>"
    "</div>"
    '<div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 10px; background-color: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px;">'
    '<div style="text-align: left;">'
    '<h2 style="color: '
    + text_color
    + '; margin: 0; font-size: 36px; letter-spacing: 1px;">'
    + f"{prob_ハマり:.1f}%"
    + "</h2>"
    '<div style="font-size: 10px; color: '
    + text_color
    + '; opacity: 0.8;">（この回転数まで当らない確率）</div>'
    "</div>"
    "<div>"
    '<img src="'
    + image_url
    + '" style="width: 60px; height: 60px; object-fit: contain; border-radius: 50%; background-color: rgba(255,255,255,0.9); padding: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />'
    "</div>"
    "</div>"
    + content_html
    + '<div style="background-color: rgba(0, 0, 0, 0.4); border: 1px dashed '
    + border_color
    + '; padding: 8px 10px; border-radius: 6px; text-align: left; margin-bottom: 10px;">'
    '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
    '<span style="font-size: 10px; color: #38bdf8; font-weight: bold; background-color: rgba(56, 189, 248, 0.1); padding: 1px 5px; border-radius: 4px;">'
    + comparison_category
    + "</span>"
    '<span style="font-size: 10px; color: #38bdf8; font-weight: bold;">'
    + approx_rate
    + "</span>"
    "</div>"
    '<div style="font-size: 11px; color: '
    + text_color
    + '; line-height: 1.4;">'
    + comparison_display
    + "</div>"
    "</div>"
    '<!-- 💳 財布/メンタル HPゲージ演出 -->'
    '<div style="background-color: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 6px;">'
    '<div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 3px;">'
    "<span>💳 財布/メンタル HP</span>"
    "<span>"
    + hp_status
    + " "
    + str(hp_percent)
    + "%</span>"
    "</div>"
    '<div style="width: 100%; background-color: #334155; height: 6px; border-radius: 3px; overflow: hidden;">'
    '<div style="width: '
    + str(hp_percent)
    + "%; background-color: "
    + (
        "#22c55e"
        if hp_percent > 50
        else "#eab308"
        if hp_percent > 20
        else "#ef4444"
    )
    + '; height: 100%; transition: width 0.3s ease;"></div>'
    "</div>"
    "</div>"
    "</div>"
)

st.markdown(card_html, unsafe_allow_html=True)

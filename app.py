import math
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断", page_icon="🎰", layout="centered"
)

# --- 1. デザイン用のカスタムCSS（DotGothic16フォントの導入） ---
st.markdown(
    """
    <!-- Google Fontsから「DotGothic16」を読み込み -->
    <link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
    
    <style>
    /* 全体にレトロドットフォントを適用 */
    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, p {
        font-family: 'DotGothic16', sans-serif !important;
    }
    
    .stApp {
        background-color: #0f172a; /* 落ち着いたダークネイビー */
        color: #f8fafc;
    }
    
    /* ラジオボタンやスライダーの文字調整 */
    label, .stRadio p, .stSlider p {
        color: #e2e8f0 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. タイトルと選択エリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center;'>🎰 パチンコ確率診断</h3>",
    unsafe_allow_html=True,
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

# スペックの決定とカスタム入力
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

# --- 3. スペックに応じたスライダー最大値の動的調整 ---
max_slider = max(1000, int(p_denom * 4.2))
step_val = 5 if p_denom <= 100 else 10

current_rotation = st.slider(
    "現在の回転数",
    min_value=0,
    max_value=max_slider,
    value=min(500, max_slider),
    step=step_val,
)

# --- 4. 計算ロジック（幾何分布のハマり確率：小数点第1位まで） ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100

# --- 5. 演出・ステータス分岐 ---
st.markdown("---")

is_yutime_over = current_rotation >= (p_denom * 2.8)

if prob_ハマり > 50:
  status_emoji = "🧊"
  status_title = "平穏（平常運転）"
  card_bg = "#1e293b"
  border_color = "#475569"
  text_color = "#e2e8f0"
  comment = "まだ慌てるような時間じゃない。ここからが本番です。"
  danger_level = 0.2
elif prob_ハマり > 20:
  status_emoji = "☕"
  status_title = "ざわ... ざわ..."
  card_bg = "#1e293b"
  border_color = "#64748b"
  text_color = "#cbd5e1"
  comment = "少し財布の紐がキュッとなる頃合い。深呼吸してコーヒーでもどうぞ。"
  danger_level = 0.5
elif is_yutime_over:
  status_emoji = "👻"
  status_title = "【幻の遊タイム】非搭載ゾーン"
  card_bg = "#2e1065"
  border_color = "#a855f7"
  text_color = "#f3e8ff"
  comment = f"昔の基準なら【約 {int(p_denom * 3)}回転】で助かってましたね……（遠い目）"
  danger_level = 0.8
elif prob_ハマり > 5:
  status_emoji = "🔥"
  status_title = "領域展開（深海）"
  card_bg = "#431407"
  border_color = "#ea580c"
  text_color = "#ffedd5"
  comment = "周囲の視線と、自分のメンタルが試されるディープゾーン。"
  danger_level = 0.85
else:
  status_emoji = "⚡"
  status_title = "神域（都市伝説）"
  card_bg = "#450a0a"
  border_color = "#ef4444"
  text_color = "#fee2e2"
  comment = "もはや語るまい。歴史に名を刻むレベルのレア体験デス。"
  danger_level = 1.0

# 選択状況の表示カード
st.markdown(
    f"""
    <div style="background-color: #1e293b; border: 1px solid #334155; padding: 10px; border-radius: 6px; text-align: center; margin-bottom: 10px;">
        <span style="font-size: 14px; color: #94a3b8;">選択スペック: <b style="color: #f8fafc;">1 / {p_denom}</b> ／ 現在: <b style="color: #f8fafc;">{current_rotation}回転</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# メインのインパクトカード（フォント・枠線をゲームUI風に調整）
st.markdown(
    f"""
    <div style="
        border: 3px double {border_color}; 
        background-color: {card_bg}; 
        padding: 24px 20px; 
        border-radius: 8px; 
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    ">
        <div style="font-size: 42px; margin-bottom: 5px;">{status_emoji}</div>
        <div style="font-size: 14px; color: {text_color}; text-transform: uppercase; letter-spacing: 2px;">{status_title}</div>
        <h2 style="color: {text_color}; margin: 10px 0 6px 0; font-size: 40px; letter-spacing: 1px;">{prob_ハマり:.1f}%</h2>
        <div style="font-size: 12px; color: {text_color}; opacity: 0.8; margin-bottom: 14px;">（この回転数まで当らない確率）</div>
        <p style="font-size: 15px; color: {text_color}; line-height: 1.6;">{comment}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 6. 危険度メーター ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 13px; color: #94a3b8; margin-bottom: 4px;'>📊"
    " ハマり危険度</p>",
    unsafe_allow_html=True,
)
st.progress(danger_level)

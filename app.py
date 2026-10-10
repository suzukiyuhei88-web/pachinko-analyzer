import math
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断", page_icon="🎰", layout="centered"
)

# --- 1. タイトルと選択エリア ---
st.markdown("### 🎰 パチンコ確率診断")

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

# スペックの決定とカスタム入力・エラーハンドリング
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
  elif p_denom > 5000.0:
    st.warning("⚠️ 注意: 少し大きすぎる数値が入力されています。")
else:
  p_denom = spec_options[selected_spec_name]

# --- 2. スペックに応じたスライダー最大値の動的調整 ---
# 分母の約4倍を目安に最大値を設定（最低1000回転は確保）
max_slider = max(1000, int(p_denom * 4.2))

# スペックによってスライダーの刻み幅を変更
if p_denom <= 100:
  step_val = 5
elif p_denom <= 250:
  step_val = 10
else:
  step_val = 10

current_rotation = st.slider(
    "現在の回転数",
    min_value=0,
    max_value=max_slider,
    value=min(500, max_slider),
    step=step_val,
)

# --- 3. 計算ロジック（幾何分布のハマり確率） ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100  # パーセンテージ（％）

# --- 4. 演出・ステータス分岐（遊タイム煽りを含む） ---
st.markdown("---")

# かつての遊タイムライン（約2.8倍）を超えているか判定
is_yutime_over = current_rotation >= (p_denom * 2.8)

if prob_ハマり > 50:
  status_emoji = "🌱"
  status_title = "平和ゾーン"
  card_bg = "#f0f4f8"
  border_color = "#cbd5e1"
  text_color = "#334155"
  comment = "まだまだ序盤！ここからの巻き返しが勝負の分かれ道です。"
  danger_level = 0.25
elif prob_ハマり > 20:
  status_emoji = "⚠️"
  status_title = "ざわ... ざわ... ゾーン"
  card_bg = "#fef9c3"
  border_color = "#fde047"
  text_color = "#854d0e"
  comment = (
      "おやおや…？ なかなかの深みにハマってきましたね。深呼吸しましょう。"
  )
  danger_level = 0.55
elif is_yutime_over:
  # 💡 懐かしの遊タイム煽り演出！
  status_emoji = "👻"
  status_title = "【幻の遊タイム】非搭載ゾーン"
  card_bg = "#f3e8ff"
  border_color = "#d8b4fe"
  text_color = "#6b21a8"
  comment = (
      f"惜しい！ 昔の基準なら【約 {int(p_denom * 3)}回転】で遊タイム発動して助かってましたね……残念！"
  )
  danger_level = 0.85
elif prob_ハマり > 5:
  status_emoji = "🔥"
  status_title = "領域展開（大ハマり）ゾーン"
  card_bg = "#ffedd5"
  border_color = "#fdba74"
  text_color = "#9a3412"
  comment = (
      "領域展開レベルのハマりです。周囲の視線が少し気になり始める頃。"
  )
  danger_level = 0.75
else:
  status_emoji = "⚡"
  status_title = "都市伝説・神域ゾーン"
  card_bg = "#fee2e2"
  border_color = "#fca5a5"
  text_color = "#991b1b"
  comment = "【超レア体験】もはや都市伝説レベルのハマりデス…。"
  danger_level = 1.0

# 選択状況の表示カード
st.markdown(
    f"""
    <div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
        <span style="font-size: 14px; color: #64748b;">選択スペック: <b>1 / {p_denom}</b> ／ 現在: <b>{current_rotation}回転</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# メインのインパクトカード
st.markdown(
    f"""
    <div style="
        border: 2px solid {border_color}; 
        background-color: {card_bg}; 
        padding: 24px 20px; 
        border-radius: 16px; 
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    ">
        <div style="font-size: 45px; margin-bottom: 5px;">{status_emoji}</div>
        <div style="font-size: 13px; color: {text_color}; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">{status_title}</div>
        <h2 style="color: {text_color}; margin: 8px 0 4px 0; font-size: 34px;">{prob_ハマり:.2f}%</h2>
        <div style="font-size: 12px; color: {text_color}; opacity: 0.8; margin-bottom: 15px;">（この回転数まで当らない確率）</div>
        <p style="font-size: 15px; color: {text_color}; font-weight: bold; line-height: 1.4;">{comment}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 5. 視覚的な「危険度メーター」 ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 4px;'>📊"
    " ハマり危険度メーター</p>",
    unsafe_allow_html=True,
)
st.progress(danger_level)

import math
import streamlit as st

# ページの基本設定（スマホ幅を意識）
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

  # 異常値のチェック
  if p_denom <= 1.0:
    st.error(
        "⚠️ エラー: 確率の分母は「1.0」より大きい数値を入力してください。"
    )
    st.stop()  # 処理をここでストップしてアプリのクラッシュを防ぐ
  elif p_denom > 5000.0:
    st.warning("⚠️ 注意: 少し大きすぎる数値が入力されています。")
else:
  p_denom = spec_options[selected_spec_name]

# 現在の回転数入力
current_rotation = st.slider("現在の回転数", 0, 2000, 500, step=10)

# --- 2. 計算ロジック（幾何分布のハマり確率） ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100  # パーセンテージ

# --- 3. ラフ画風：コメントカード ＆ ビジュアルフレーム ---
st.markdown("---")

# 上部：現在の選択状況を示すカード
with st.container():
  st.markdown(
      f"""
        <div style="
            background-color: #f0f2f6; 
            padding: 15px; 
            border-radius: 10px; 
            text-align: center;
            margin-bottom: 10px;
        ">
            <span style="font-size: 14px; color: #555;">選択スペック: <b>1 / {p_denom}</b> ／ 現在: <b>{current_rotation}回転</b></span>
        </div>
        """,
      unsafe_allow_html=True,
  )

# 確率に応じた絵文字とコメントの切り替え
if prob_ハマり > 50:
  status_emoji = "🌱"
  comment = "まだまだ序盤！ここからの巻き返しが勝負の分かれ道です。"
elif prob_ハマり > 20:
  status_emoji = "⚠️"
  comment = (
      "おやおや…？ なかなかの深みにハマってきましたね。深呼吸しましょう。"
  )
elif prob_ハマり > 5:
  status_emoji = "🔥"
  comment = (
      "領域展開レベルのハマりです。周囲の視線が少し気になり始める頃。"
  )
else:
  status_emoji = "⚡"
  comment = "【超レア体験】もはや都市伝説レベルのハマりデス…。"

# 下部：メインの結果表示カード（イラスト・枠組み風）
st.markdown(
    f"""
    <div style="
        border: 2px solid #ff4b4b; 
        background-color: #fff5f5; 
        padding: 25px 20px; 
        border-radius: 15px; 
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    ">
        <div style="font-size: 45px; margin-bottom: 5px;">{status_emoji}</div>
        <div style="font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;">ハマり継続率</div>
        <h2 style="color: #ff4b4b; margin: 5px 0 15px 0; font-size: 32px;">{prob_ハマり:.2f}%</h2>
        <p style="font-size: 15px; color: #333; font-weight: bold; line-height: 1.4;">{comment}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

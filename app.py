import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# ページ全体のレイアウト設定（スマホ向けにすっきりと）
st.set_page_config(
    page_title="パチンコ確率診断", page_icon="🎯", layout="centered"
)

# --- スタイルの調整（ラフ画のようなすっきり感） ---
st.markdown(
    """
    <style>
    .main {
        background-color: #fafafa;
    }
    h3 {
        color: #333333;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- タイトル ---
st.markdown(
    "<h3 style='text-align: center; margin-bottom: 20px;'>パチンコはまり確率</h3>",
    unsafe_allow_html=True,
)

# --- 1. スペック選択（ラフ画風の横並びボタン形式 ＋ カスタム対応） ---
spec_options = {
    "甘デジ (1/99)": 99.9,
    "ライトミドル (1/199)": 199.8,
    "ミドル (1/319)": 319.6,
    "ラッキートリガー (1/349)": 349.0,
    "カスタム": 0.0,  # 自由入力用
}

# 横並びのラジオボタンで選択式にする
selected_spec_name = st.radio(
    "機種スペックを選択",
    list(spec_options.keys()),
    index=2,  # デフォルトでミドル(1/319)を選択
    horizontal=True,
)

# 「カスタム」が選ばれた時だけ、自由に入力できる数値を出す
if selected_spec_name == "カスタム":
  p_denom = st.number_input(
      "大当り確率の分母を入力 (例: 319.6)",
      min_value=1.0,
      max_value=1000.0,
      value=319.6,
      step=0.1,
  )
else:
  p_denom = spec_options[selected_spec_name]

# --- 2. 現在の回転数入力 ---
current_spin = st.slider(
    "現在の回転数（ハマり回転数）",
    min_value=10,
    max_value=int(p_denom * 3),
    value=int(p_denom * 1.5),
    step=10,
)

# --- 3. 確率の計算 ---
prob = (1.0 - (1.0 / p_denom)) ** current_spin
hit_prob_percent = (1 - prob) * 100  # 当たる確率（累積確率）
hamari_prob_percent = prob * 100  # はまり確率（残り確率）

# --- 4. ラフ画の「ネタ・コメント」カード ---
if hit_prob_percent >= 99:
    comment_title = "🔥 【奇跡の領域】そろそろ当たるはず…！"
    comment_desc = "ここから当たらなかったら、逆に持っています。"
elif hit_prob_percent >= 90:
    comment_title = "⚡ 【大ハマり】9割がすでに通過したライン"
    comment_desc = "なかなかのレア体験ゾーンに突入しています。"
elif hit_prob_percent >= 50:
    comment_title = "🌊 【平常運転】およそ平均的なハマり"
    comment_desc = "確率の壁のちょうど折り返し地点です。"
else:
    comment_title = "🌱 【序盤】まだまだこれから！"
    comment_desc = "落ち着いて深呼吸していきましょう。"

# ラフ画のカード風デザイン（グレーのボックス）
st.markdown(
    f"""
    <div style="background-color: #f1f3f4; border: 1px solid #dadce0; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h4 style="margin: 0 0 8px 0; color: #202124; font-size: 18px;">{comment_title}</h4>
        <p style="margin: 0; color: #5f6368; font-size: 14px;">{comment_desc}</p>
        <hr style="margin: 15px 0; border: none; border-top: 1px solid #e0e0e0;">
        <div style="display: flex; justify-content: space-around; align-items: center;">
            <div style="font-size: 14px; color: #5f6368;">はまり確率</div>
            <div style="font-size: 24px; font-weight: bold; color: #137333;">{hamari_prob_percent:.1f}%</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 5. ラフ画のイメージに合わせたシンプル＆スタイリッシュなグラフ ---
fig, ax = plt.subplots(figsize=(8, 3.5))

spins_range = np.linspace(10, int(p_denom * 3), 100)
hamari_rates = ((1.0 - (1.0 / p_denom)) ** spins_range) * 100

# グラフの線を綺麗に描画
ax.plot(
    spins_range, hamari_rates, color="#5f6368", linewidth=2, linestyle="-"
)
ax.axvline(
    x=current_spin, color="#d93025", linestyle="--", linewidth=1.5, alpha=0.7
)
ax.scatter(
    [current_spin],
    [hamari_prob_percent],
    color="#d93025",
    zorder=5,
    s=70,
    label="現在地",
)

# 軸や余分な装飾を削ってラフ画のようにミニマルにする
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#888888")
ax.spines["bottom"].set_color("#888888")
ax.xaxis.set_tick_params(color="#888888", labelcolor="#5f6368")
ax.yaxis.set_tick_params(color="#888888", labelcolor="#5f6368")

ax.set_title("はまり確率の推移イメージ", fontsize=11, color="#333333", pad=10)
ax.grid(True, linestyle=":", alpha=0.4)

st.pyplot(fig)

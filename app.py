import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ページ全体のレイアウト設定
st.set_page_config(
    page_title="パチンコ確率診断",
    page_icon="🎯",
    layout="centered"
)

# --- タイトル ---
st.markdown("<h3 style='text-align: center;'>🎯 パチンコはまり確率診断</h3>", unsafe_allow_html=True)

# --- 1. スペック選択（横並びですっきり） ---
spec_options = {
    "甘デジ (1/99.9)": 99.9,
    "ライトミドル (1/199.8)": 199.8,
    "ミドル (1/319.6)": 319.6,
    "ラッキートリガー等 (1/349.0)": 349.0,
    "超ミドル (1/399.6)": 399.6
}

selected_spec_name = st.selectbox("機種スペックを選択", list(spec_options.keys()), index=2)
p_denom = spec_options[selected_spec_name]

# --- 2. 現在の回転数入力 ---
col1, col2 = st.columns([3, 1])
with col1:
    current_spin = st.slider(
        "現在の回転数（ハマり回転数）",
        min_value=10,
        max_value=int(p_denom * 4),
        value=int(p_denom * 1.5),
        step=10
    )
with col2:
    current_spin = st.number_input("回転数", min_value=1, max_value=5000, value=current_spin)

# --- 3. 確率の計算 ---
prob = (1.0 - (1.0 / p_denom)) ** current_spin
hit_prob_percent = (1 - prob) * 100  # 当たる確率（累積確率）

# --- 4. インパクトのある「ネタ・コメントカード」の表示 ---
if hit_prob_percent >= 99:
    comment_title = "🔥 【奇跡の領域】そろそろ当たるはず…！"
    comment_desc = "ここから当たらなかったら、逆に持っているとしか言えません。"
elif hit_prob_percent >= 90:
    comment_title = "⚡ 【大ハマり】9割の人がすでに当てているライン"
    comment_desc = "10人中9人がこれより手前で当てています。"
elif hit_prob_percent >= 50:
    comment_title = "🌊 【平常運転】およそ平均的なハマり"
    comment_desc = "確率の壁のちょうど折り返し地点です。"
else:
    comment_title = "🌱 【序盤】まだまだこれから！"
    comment_desc = "落ち着いて深呼吸していきましょう。"

st.markdown(f"""
    <div style="padding: 16px; border-radius: 10px; background-color: #f0f2f6; border-left: 6px solid #ff4b4b; margin-bottom: 15px;">
        <h4 style="margin: 0; color: #31333F;">{comment_title}</h4>
        <p style="margin: 6px 0 0 0; font-size: 14px; color: #555;">{comment_desc}</p>
        <hr style="margin: 10px 0; border: none; border-top: 1px solid #ddd;">
        <div style="font-size: 16px; font-weight: bold; color: #ff4b4b;">
            当たる確率： {hit_prob_percent:.1f}% （ハマり続ける確率： {prob*100:.1f}%）
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 身近な確率との比較ネタ ---
st.markdown("#### 🌍 身近な確率との比較")

if prob < 0.01:
    analogy = "一卵性双生児が生まれる確率（約0.4%〜）よりも低い、超レアな領域に入っています…"
elif prob < 0.05:
    analogy = "AB型の人が生まれる確率（約10%）よりも低い、なかなかのレアケースです。"
elif prob < 0.20:
    analogy = "左利きの人に出会う確率（約10%）と同等か、それ以下です。"
else:
    analogy = "日常の中でたまに起こるイベントくらいの確率です。まだまだこれから！"

st.info(analogy)

# --- 6. 補助的なグラフの表示 ---
fig, ax = plt.subplots(figsize=(8, 3))

spins_range = np.linspace(10, int(p_denom * 3), 100)
hamari_rates = ((1.0 - (1.0 / p_denom)) ** spins_range) * 100

ax.plot(spins_range, hamari_rates, color='#1f77b4', linewidth=2, label="Non-hit")
ax.axvline(x=current_spin, color='#ff4b4b', linestyle='--', linewidth=1.5)
ax.scatter([current_spin], [prob * 100], color='#ff4b4b', zorder=5, s=60)

ax.set_title("Hamari Curve", fontsize=10, fontweight='bold')
ax.set_xlabel("Spins", fontsize=9)
ax.set_ylabel("Remaining (%)", fontsize=9)
ax.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig)

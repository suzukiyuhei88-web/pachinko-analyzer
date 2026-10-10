import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(
    page_title="パチンコ確率診断 狂気のガローズユーモア",
    page_icon="🎰",
    layout="centered"
)

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.75rem;
    }
    .stButton>button:hover {
        background-color: #ff2b2b;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #374151;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('neta_master.csv')

try:
    df = load_data()
except Exception as e:
    st.error(f"データファイル 'neta_master.csv' の読み込みに失敗しました: {e}")
    st.stop()

st.title("🎰 パチンコ確率・現実乖離 診断")
st.caption("〜「なぜ俺の台だけ当たらんのか」を客観的ファクトで刺すアプリ〜")

tab1, tab2 = st.tabs(["📊 ハマり確率 & 日常比較診断", "🔥 RUSH連続スルー確率"])

with tab1:
    st.subheader("パチンコハマり確率 ＆ ガローズ診断")
    st.write("現在のスペックとハマり回転数を入力してください。その絶望が日常のどの確率に匹敵するかを暴きます。")
    
    col1, col2 = st.columns(2)
    with col1:
        spec_choice = st.selectbox(
            "大当り確率スペック",
            ["ミドル (1/319.7)", "ライトミドル (1/199.8)", "甘デジ (1/99.9)", "カスタム・その他"]
        )
    with col2:
        if "ミドル" in spec_choice:
            default_denom = 319.7
        elif "ライトミドル" in spec_choice:
            default_denom = 199.8
        elif "甘デジ" in spec_choice:
            default_denom = 99.9
        else:
            default_denom = 319.7
            
        denom = st.number_input("分母 (1 / X)", min_value=10.0, max_value=1000.0, value=float(default_denom), step=0.1)

    spins = st.slider("現在のハマり回転数", min_value=50, max_value=2500, value=500, step=10)

    if st.button("🎲 ハマりの絶望度を計測する"):
        # Calculate dry-spell (ハマり) probability: P = (1 - 1/denom)^spins
        p = 1.0 / denom
        hamari_prob = ((1.0 - p) ** spins) * 100.0
        
        st.markdown(f"""
        <div class="metric-card">
            <p style="color: #9ca3af; font-size: 0.9rem; margin-bottom: 0.5rem;">【 あなたの台の現実 】</p>
            <h3 style="color: #f3f4f6; margin-bottom: 0.5rem;">確率 1 / {denom} の台で <b>{spins}回転</b> ハマる確率</h3>
            <h1 style="color: #ef4444; font-weight: bold; margin-bottom: 1rem;">{hamari_prob:.4f} %</h1>
            <p style="color: #9ca3af; font-size: 0.85rem;">（※この回転数まで一度も当らない確率です）</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔍 日常のファクトと比較したガローズ判定")
        
        # Pick a random sample or matching sample from df to add flavor
        sample = df.sample(1).iloc[0]
        
        st.markdown(f"""
        <div class="metric-card" style="background-color: #111827; border-color: #4b5563;">
            <p style="color: #9ca3af; font-size: 0.9rem; margin-bottom: 0.5rem;">【 比較対象の日常ファクト 】</p>
            <h4 style="color: #f3f4f6; margin-bottom: 0.3rem;">{sample['事象']}</h4>
            <p style="color: #38bdf8; font-weight: bold; margin-bottom: 0.8rem;">現実の確率： {sample['確率・数値']}</p>
            <hr style="border-color: #374151; margin: 0.8rem 0;">
            <p style="color: #e5e7eb; font-size: 1.05rem; font-style: italic;">「 {sample['コメント']} 」</p>
        </div>
        """, unsafe_allow_html=True)
        
        if hamari_prob < 1.0:
            st.error("⚠️ **【神域・奇跡の領域】**：文字通り「異常値」です。ホールに管理されているか、あなたの運の総量が別の次元で消費されています。")
        elif hamari_prob < 10.0:
            st.warning("⚠️ **【深海ゾーン】**：かなりの絶望深度です。日常でなかなか起きないレアケースを、あなたは今ホールで独り占めしています。")
        elif hamari_prob < 30.0:
            st.info("⚡ **【ざわつきゾーン】**：十分あり得るハマりですが、じわじわと財布とメンタルを削り取られる嫌な時間帯です。")
        else:
            st.success("🍵 **【平穏ゾーン】**：まだまだ序盤です。ここからがパチンコの本当の地獄の始まりです。")

with tab2:
    st.subheader("🔥 RUSH連続スルー確率シミュレータ")
    st.write("50%継続などのRUSHや突破型スペックを何連単（連続スルー）で外したかの絶望度を計算します。")
    
    rush_prob = st.slider("RUSH継続率 / 当たり確率 (%)", 1, 99, 50)
    streak = st.slider("連続スルー・外し回数 (連単)", 1, 10, 3)
    
    p_fail = (100 - rush_prob) / 100.0
    fail_prob = (p_fail ** streak) * 100
    
    st.info(f"継続率 {rush_prob}% の抽選を **{streak}連続で外す確率**： **{fail_prob:.4f}%** （約 {1/p_fail**streak:.1f}回に1回）")
    st.write("「これだけの奇跡的な低確率を、あなたは今日ホールで成し遂げました。」")

st.markdown("---")
st.caption("Data source: neta_master.csv | Developed with Gallows Humor")

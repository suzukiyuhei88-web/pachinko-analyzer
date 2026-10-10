import streamlit as st
import pandas as pd
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

tab1, tab2 = st.tabs(["📊 日常確率 & ガローズ診断", "🔥 RUSH連続スルー確率"])

with tab1:
    st.subheader("現実の確率 vs パチンコの絶望")
    
    zone_filter = st.selectbox(
        "現在のハマり・ゾーン状況を選択",
        ["すべてのゾーン", "peaceful (平穏)", "caution (ざわつき)", "yutime_ghost (幽霊・前兆)", "deep (深海・天井手前)", "god (神域・奇跡)"]
    )
    
    filtered_df = df.copy()
    if "peaceful" in zone_filter:
        filtered_df = df[df['ゾーン'] == 'peaceful']
    elif "caution" in zone_filter:
        filtered_df = df[df['ゾーン'] == 'caution']
    elif "yutime_ghost" in zone_filter:
        filtered_df = df[df['ゾーン'] == 'yutime_ghost']
    elif "deep" in zone_filter:
        filtered_df = df[df['ゾーン'] == 'deep']
    elif "god" in zone_filter:
        filtered_df = df[df['ゾーン'] == 'god']

    if st.button("🎲 現実の過酷さを突きつける"):
        if len(filtered_df) > 0:
            sample = filtered_df.sample(1).iloc[0]
            
            st.markdown(f"""
            <div class="metric-card">
                <p style="color: #9ca3af; font-size: 0.9rem; margin-bottom: 0.5rem;">【 比較ファクト 】</p>
                <h3 style="color: #f3f4f6; margin-bottom: 0.5rem;">{sample['事象']}</h3>
                <h2 style="color: #ef4444; font-weight: bold; margin-bottom: 1rem;">確率：{sample['確率・数値']}</h2>
                <hr style="border-color: #374151; margin: 1rem 0;">
                <p style="color: #e5e7eb; font-size: 1.1rem; font-style: italic;">「 {sample['コメント']} 」</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("該当するデータがありません。")

with tab2:
    st.subheader("🔥 RUSH連続スルー確率シミュレータ")
    st.write("50%継続などのRUSHを何連単でスルーしたかの絶望度を計算します。")
    
    rush_prob = st.slider("RUSH継続率 / 当たり確率 (%)", 1, 99, 50)
    streak = st.slider("連続スルー・外し回数 (連単)", 1, 10, 3)
    
    p = (100 - rush_prob) / 100.0
    fail_prob = (p ** streak) * 100
    
    st.info(f"継続率 {rush_prob}% の抽選を **{streak}連続で外す確率**： **{fail_prob:.4f}%** （約 {1/p**streak:.1f}回に1回）")
    st.write("「これだけの奇跡的な低確率を、あなたは今日ホールで成し遂げました。」")

st.markdown("---")
st.caption("Data source: neta_master.csv | Developed with Gallows Humor")

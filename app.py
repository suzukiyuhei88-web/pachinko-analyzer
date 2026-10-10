import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ページ設定
st.set_page_config(page_title="パチンコ確率アナライザー", layout="centered")

st.title("🎰 パチンコハマり・連続通常 確率チェッカー")
st.caption("あなたのハマり・連続通常は、世の中のどんな出来事・確率に匹敵するのか？")

# サイドバー：設定
st.sidebar.header("⚙️ 設定・入力")
app_mode = st.sidebar.radio("診断モードを選択", ["ハマり回転数 診断", "連続通常（単発連続） 診断"])

# スペック定義
spec_options = {
    "ミドル (1/319.6)": 1 / 319.6,
    "ライトミドル (1/199.9)": 1 / 199.9,
    "甘デジ (1/99.9)": 1 / 99.9,
    "カスタム設定": None
}

if app_mode == "ハマり回転数 診断":
    st.header("📊 大号泣（大ハマり）間ハマり 診断")
    
    spec_name = st.sidebar.selectbox("スペック選択", list(spec_options.keys()))
    if spec_name == "カスタム設定":
        p_denom = st.sidebar.number_input("大当たり確率の分母 (1/X)", value=319.6, step=0.1)
        p = 1.0 / p_denom
    else:
        p = spec_options[spec_name]
        p_denom = 1.0 / p

    rotations = st.number_input("現在のハマり回転数を入力", min_value=1, value=600, step=10)
    
    # 確率計算（幾何分布の生存関数）
    prob_hamari = ((1 - p) ** rotations) * 100
    one_in_x = 100 / prob_hamari if prob_hamari > 0 else float('inf')

    # 結果表示
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ハマり継続確率", f"{prob_hamari:.2f} %")
    with col2:
        st.metric("出現頻度", f"約 {one_in_x:.1f} 人に1人")

    # 比較メッセージ（生物・自然現象・義務教育ネタを組み込んだロジック）
    st.subheader("🌍 世の中の出来事・確率と比較すると…")
    
    if prob_hamari > 50:
        pos_msg = "じゃんけんで負ける、コイン投げで裏が出るレベルの日常的な確率です。"
        neg_msg = "特に何も起きていません。平穏な通常運転です。"
    elif prob_hamari > 20:
        pos_msg = "血液型がAB型の人（約10%）や左利きの人よりは引く確率が高い！そろそろ波が来るかも？"
        neg_msg = "ホール内で5人に1人は経験中。よくある日常茶飯事のハマりです。"
    elif prob_hamari > 10:
        pos_msg = "【学校ネタ】35人クラスの中に『自分と同じ誕生日の人が誰もいない確率』（約15%）と同等！逆にレアなマイノリティです。"
        neg_msg = "10人に1人の不運。少し財布の紐を締め直したほうが良いかも…"
    elif prob_hamari > 4:
        pos_msg = "スマホゲームのSSRガチャ単発（約3〜5%）を引き当てるレベルの運の偏り！"
        neg_msg = "ホール内でちょっとついてない位置。缶コーヒーでも飲んでリフレッシュを。"
    elif prob_hamari > 1:
        pos_msg = "【生物ネタ】『双子が生まれる確率』（約1%）クラスの超・激レア体験！今なら何か別の幸運が起きる気配…？"
        neg_msg = "100人に1人の大不幸。心が折れかける耐え時です。"
    elif prob_hamari > 0.2:
        pos_msg = "【学校ネタ】35人クラスで『血液型AB型の人が1人もいない確率』（約2.3%）や、ジャンボ宝くじ4等レベル！"
        neg_msg = "歴史的ハマり。店長ボタンを疑いたくなるレベルの不条理な偏りです。"
    else:
        pos_msg = "【自然現象】一年のうちに『落雷に遭う確率』や麻雀の『役満』レベルの奇跡！この強烈な偏りはもはや才能です。"
        neg_msg = "伝説級の大ハマり。今日は早めに撤退して美味しいものでも食べましょう…"

    tab1, tab2 = st.tabs(["👿 ネガティブ表示（共感・不幸自慢）", "😇 ポジティブ表示（引き強・ネタ）"])
    with tab1:
        st.error(neg_msg)
    with tab2:
        st.success(pos_msg)

    # グラフ表示
    st.subheader("📈 ハマり確率の分布（生存関数）")
    x = np.arange(1, int(p_denom * 4))
    y = ((1 - p) ** x) * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, label="ハマり継続率 (%)", color="blue")
    ax.axvline(rotations, color="red", linestyle="--", label=f"現在地 ({rotations}回転)")
    ax.set_xlabel("回転数")
    ax.set_ylabel("まだ当たっていない確率 (%)")
    ax.set_title(f"スペック 1/{p_denom:.1f} のハマり分布")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

elif app_mode == "連続通常（単発連続） 診断":
    st.header("💔 連続通常（単発連続） 診断")
    
    rush_rate_pct = st.sidebar.slider("確変/RUSH突入率 (%)", min_value=10, max_value=90, value=60, step=5)
    rush_rate = rush_rate_pct / 100.0
    normal_rate = 1.0 - rush_rate

    consecutive_normals = st.number_input("連続で通常（単発）を引いた回数", min_value=1, value=4, step=1)

    prob_consecutive = (normal_rate ** consecutive_normals) * 100
    one_in_x_norm = 100 / prob_consecutive if prob_consecutive > 0 else float('inf')

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("連続通常 確率", f"{prob_consecutive:.2f} %")
    with col2:
        st.metric("出現頻度", f"約 {one_in_x_norm:.1f} 人に1人")

    st.subheader("🌍 世の中の出来事と比較すると…")
    if prob_consecutive > 10:
        pos_text = "コイン投げで3回連続裏が出る程度の確率。日常的によくある範囲です。"
        neg_text = "連チャンしなくても泣かない。まだ想定内です。"
    elif prob_consecutive > 1:
        pos_text = "ガリガリ君の当たりが出る確率（約4%）並み！逆にすごい引きの偏り！"
        neg_text = "RUSHを華麗に回避し続けるプロ。心が折れかけるレベルです。"
    else:
        pos_text = "★超引き強（の逆）★ 年賀状のお年玉2等や双子の出生率並みのレア体験！"
        neg_text = "店長とのアイコンタクトを疑いたくなるレベルの連続スルーです。"

    tab1, tab2 = st.tabs(["👿 ネガティブ表示", "😇 ポジティブ表示"])
    with tab1:
        st.error(neg_text)
    with tab2:
        st.success(pos_text)

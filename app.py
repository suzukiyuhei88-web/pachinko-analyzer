import math
import random
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断", page_icon="🎰", layout="centered"
)

# --- 1. デザイン用のカスタムCSS（DotGothic16フォントの導入 ＆ コンパクト化） ---
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

# --- 2. ネタ帳データ（コメント ＋ 確率同等事象 ＋ 仮アイコン） ---
ZONE_MESSAGES = {
    "peaceful": {
        "title": "まだ慌てるような時間じゃない",
        "messages": [
            "まだ慌てるような時間じゃない。ここからが本番です。",
            "財布の紐はまだしっかり締まっています。平和な日常ですね。",
            "隣の台が爆連している音をBGMに、静かにレバーを叩くフェーズ。",
        ],
        "comparisons": [
            {
                "text": "コインを投げて2回連続で同じ面が出るくらいの確率",
                "approx": "約 50%",
            },
            {
                "text": "4択クイズでなんとなく選んだ選択肢が外れる確率",
                "approx": "約 75%",
            },
        ],
        "image": (
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
        ),
    },
    "caution": {
        "title": "ざわ… ざわ… ゾーン",
        "messages": [
            "少し財布の紐がキュッとなる頃合い。深呼吸してコーヒーでもどうぞ。",
            "「もしかして、今日もやられる日なのでは…？」という悪寒が走り始める頃。",
            "周囲の出玉を見ないように視線を台に固定するトレーニング期間。",
        ],
        "comparisons": [
            {
                "text": "じゃんけんを2回連続ですべてあいこにする確率",
                "approx": "約 33%",
            },
            {
                "text": "トランプの山札からハートのカードを引く確率",
                "approx": "約 25%",
            },
        ],
        "image": (
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
        ),
    },
    "yutime_ghost": {
        "title": "【幻の遊タイム】非搭載ゾーン",
        "messages": [
            (
                "昔の基準なら【約 {yutime_rot}回転】で助かってましたね……（遠い目）"
            ),
            (
                "遊タイムという名の救済措置が消え去った現代の荒波を、生身で泳いでいます。"
            ),
        ],
        "comparisons": [{
            "text": "昔のゲームの隠しコマンドをノーヒントで当てるくらいの絶望感",
            "approx": "約 15%",
        }],
        "image": (
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
        ),
    },
    "deep": {
        "title": "領域展開（深海トラウマ）",
        "messages": [
            (
                "RUSHに入った瞬間3秒で駆け抜けたあの日の虚しさに比べれば、このハマりなど微風です。"
            ),
            (
                "『からくりサーカス』の運命の一撃で負けた時の絶望感を、思い出させてくれる深海ゾーン。"
            ),
            ("周囲の視線と、自分のメンタルが試されるディープゾーン。"),
        ],
        "comparisons": [
            {
                "text": "トランプのババ抜きで最後までジョーカーが手札に残る確率",
                "approx": "約 10%",
            },
            {
                "text": "街中で見知らぬ人に完全に人違いされる確率",
                "approx": "約 7%",
            },
        ],
        "image": (
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
        ),
    },
    "god": {
        "title": "歴史に名を刻むレベル",
        "messages": [
            ("もはや語るまい。歴史に名を刻むレベルのレア体験デス。"),
            ("確率の女神に完全に嫌われているか、別の何かを召喚している状態です。"),
            ("我が人生に一片の悔い…いや、めちゃくちゃ悔い残るわ！という領域。"),
        ],
        "comparisons": [
            {
                "text": "日常でちょっとした奇跡やハプニングが連続して起きる確率",
                "approx": "約 3%",
            },
            {
                "text": "奇跡と理不尽の境界線を完全に突破している確率",
                "approx": "約 1%未満",
            },
        ],
        "image": (
            "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
        ),
    },
}

# --- 3. タイトルと選択エリア ---
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

# --- 4. スペックに応じたスライダー最大値の動的調整 ---
max_slider = max(1000, int(p_denom * 4.2))
step_val = 5 if p_denom <= 100 else 10

current_rotation = st.slider(
    "現在の回転数",
    min_value=0,
    max_value=max_slider,
    value=min(500, max_slider),
    step=step_val,
)

# --- 5. 計算ロジック（幾何分布のハマり確率：小数点第1位まで） ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100

# --- 6. 演出・ステータス分岐 ---
st.markdown("---")

is_yutime_over = current_rotation >= (p_denom * 2.8)

if prob_ハマり > 50:
  zone_data = ZONE_MESSAGES["peaceful"]
  card_bg = "#1e293b"
  border_color = "#475569"
  text_color = "#e2e8f0"
  comment = random.choice(zone_data["messages"])
  comparison_item = random.choice(zone_data["comparisons"])
  danger_level = 0.2
elif prob_ハマり > 20:
  zone_data = ZONE_MESSAGES["caution"]
  card_bg = "#1e293b"
  border_color = "#64748b"
  text_color = "#cbd5e1"
  comment = random.choice(zone_data["messages"])
  comparison_item = random.choice(zone_data["comparisons"])
  danger_level = 0.5
elif is_yutime_over:
  zone_data = ZONE_MESSAGES["yutime_ghost"]
  card_bg = "#2e1065"
  border_color = "#a855f7"
  text_color = "#f3e8ff"
  yutime_rot = int(p_denom * 3)
  comment = random.choice(zone_data["messages"]).format(yutime_rot=yutime_rot)
  comparison_item = random.choice(zone_data["comparisons"])
  danger_level = 0.8
elif prob_ハマり > 5:
  zone_data = ZONE_MESSAGES["deep"]
  card_bg = "#431407"
  border_color = "#ea580c"
  text_color = "#ffedd5"
  comment = random.choice(zone_data["messages"])
  comparison_item = random.choice(zone_data["comparisons"])
  danger_level = 0.85
else:
  zone_data = ZONE_MESSAGES["god"]
  card_bg = "#450a0a"
  border_color = "#ef4444"
  text_color = "#fee2e2"
  comment = random.choice(zone_data["messages"])
  comparison_item = random.choice(zone_data["comparisons"])
  danger_level = 1.0

status_title = zone_data["title"]
comparison_text = comparison_item["text"]
comparison_approx = comparison_item["approx"]
image_url = zone_data["image"]

# --- 7. 統合メインカード（スペック・回転数・確率・アイコン・コメント・比較をすべて集約） ---
card_html = f"""
<div style="border: 3px double {border_color}; background-color: {card_bg}; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
    
    <!-- ヘッダー：選択スペックと現在回転数をカード内に内包 -->
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 14px; font-size: 13px; color: #94a3b8;">
        <span>スペック: <b style="color: #f8fafc;">1 / {p_denom}</b></span>
        <span>現在: <b style="color: #f8fafc;">{current_rotation}回転</b></span>
    </div>

    <!-- ゾーンタイトルとステータス -->
    <div style="text-align: center; margin-bottom: 10px;">
        <div style="font-size: 13px; color: {text_color}; text-transform: uppercase; letter-spacing: 2px;">{status_title}</div>
    </div>

    <!-- 横並びレイアウト（左：確率表示 ＆ 右：アイコンイラスト） -->
    <div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 14px; background-color: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <div style="text-align: left;">
            <h2 style="color: {text_color}; margin: 0; font-size: 42px; letter-spacing: 1px;">{prob_ハマり:.1f}%</h2>
            <div style="font-size: 11px; color: {text_color}; opacity: 0.8;">（この回転数まで当らない確率）</div>
        </div>
        <div>
            <img src="{image_url}" style="width: 75px; height: 75px; object-fit: contain; border-radius: 50%; background-color: rgba(255,255,255,0.9); padding: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />
        </div>
    </div>

    <!-- シュールなコメント -->
    <p style="font-size: 14px; color: {text_color}; line-height: 1.5; margin-bottom: 14px; text-align: center; padding: 0 5px;">{comment}</p>
    
    <!-- 現実世界の確率スケール -->
    <div style="background-color: rgba(0, 0, 0, 0.4); border: 1px dashed {border_color}; padding: 10px 12px; border-radius: 6px; text-align: left;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 11px; color: #94a3b8; letter-spacing: 1px;">🌍 現実世界での確率スケール</span>
            <span style="font-size: 11px; color: #38bdf8; font-weight: bold; background-color: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 4px;">{comparison_approx}</span>
        </div>
        <p style="font-size: 12px; color: {text_color}; margin: 0; line-height: 1.4;">🎯 {comparison_text}</p>
    </div>
</div>
"""
st.markdown(card_html, unsafe_allow_html=True)

# --- 8. 危険度メーター ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 13px; color: #94a3b8; margin-bottom: 4px;'>📊"
    " ハマり危険度</p>",
    unsafe_allow_html=True,
)
st.progress(danger_level)

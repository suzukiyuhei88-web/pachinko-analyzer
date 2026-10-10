import math
import random
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断", page_icon="🎰", layout="centered"
)

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

# --- 2. ゾーンごとのデータ定義（平穏 ➔ ざわ… ➔ 遊タイム非搭載 ➔ 領域展開 ➔ 神域） ---
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
        "hp_percent": 100,
        "hp_status": "NORMAL (元気)",
        "card_bg": "#1e293b",
        "border_color": "#475569",
        "text_color": "#e2e8f0",
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
        "hp_percent": 60,
        "hp_status": "CAUTION (注意)",
        "card_bg": "#1e293b",
        "border_color": "#64748b",
        "text_color": "#cbd5e1",
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
        "hp_percent": 30,
        "hp_status": "WARNING (警告)",
        "card_bg": "#2e1065",
        "border_color": "#a855f7",
        "text_color": "#f3e8ff",
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
        "hp_percent": 10,
        "hp_status": "DANGER (瀕死)",
        "card_bg": "#431407",
        "border_color": "#ea580c",
        "text_color": "#ffedd5",
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

# --- 6. 演出・ステータス分岐（確率の階段を上から順に正しく判定） ---
st.markdown("---")

is_yutime_over = current_rotation >= (p_denom * 2.8)

if prob_ハマり > 50:
  zone_key = "peaceful"  # 1. 平穏（確率50%超）
elif prob_ハマり > 20:
  zone_key = "caution"  # 2. ざわ…（確率20%超）
elif prob_ハマり > 10:
  zone_key = "yutime_ghost"  # 3. 【幻の遊タイム】非搭載ゾーン
elif prob_ハマり > 1.0:
  zone_key = "deep"  # 4. 領域展開（深海トラウマ）
else:
  zone_key = "god"  # 5. 神域（確率1%以下）

zone_data = ZONE_MESSAGES[zone_key]

status_title = zone_data["title"]
card_bg = zone_data["card_bg"]
border_color = zone_data["border_color"]
text_color = zone_data["text_color"]
hp_percent = zone_data["hp_percent"]
hp_status = zone_data["hp_status"]
image_url = zone_data["image"]

# メッセージや比較データの安全な取得
comment = random.choice(zone_data["messages"])
if zone_key == "yutime_ghost":
  yutime_rot = int(p_denom * 3)
  comment = comment.format(yutime_rot=yutime_rot)

comparison_item = random.choice(zone_data["comparisons"])
comparison_text = comparison_item["text"]
comparison_approx = comparison_item["approx"]

# --- 7. 統合メインカード ---
card_html = (
    '<div style="border: 3px double '
    + border_color
    + "; background-color: "
    + card_bg
    + '; padding: 18px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">'
    '<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 12px; font-size: 13px; color: #94a3b8;">'
    '<span>スペック: <b style="color: #f8fafc;">1 / '
    + str(p_denom)
    + "</b></span>"
    '<span>現在: <b style="color: #f8fafc;">'
    + str(current_rotation)
    + "回転</b></span>"
    "</div>"
    '<div style="text-align: center; margin-bottom: 10px;">'
    '<div style="font-size: 13px; color: '
    + text_color
    + '; text-transform: uppercase; letter-spacing: 2px;">'
    + status_title
    + "</div>"
    "</div>"
    '<div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 12px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">'
    '<div style="text-align: left;">'
    '<h2 style="color: '
    + text_color
    + '; margin: 0; font-size: 40px; letter-spacing: 1px;">'
    + f"{prob_ハマり:.1f}%"
    + "</h2>"
    '<div style="font-size: 11px; color: '
    + text_color
    + '; opacity: 0.8;">（この回転数まで当らない確率）</div>'
    "</div>"
    "<div>"
    '<img src="'
    + image_url
    + '" style="width: 70px; height: 70px; object-fit: contain; border-radius: 50%; background-color: rgba(255,255,255,0.9); padding: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />'
    "</div>"
    "</div>"
    '<p style="font-size: 14px; color: '
    + text_color
    + '; line-height: 1.5; margin-bottom: 12px; text-align: center; padding: 0 5px;">'
    + comment
    + "</p>"
    '<div style="background-color: rgba(0, 0, 0, 0.4); border: 1px dashed '
    + border_color
    + '; padding: 10px 12px; border-radius: 6px; text-align: left; margin-bottom: 12px;">'
    '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
    '<span style="font-size: 11px; color: #94a3b8; letter-spacing: 1px;">🌍 現実世界での確率スケール</span>'
    '<span style="font-size: 11px; color: #38bdf8; font-weight: bold; background-color: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 4px;">'
    + comparison_approx
    + "</span>"
    "</div>"
    '<p style="font-size: 12px; color: '
    + text_color
    + '; margin: 0; line-height: 1.4;">🎯 '
    + comparison_text
    + "</p>"
    "</div>"
    '<!-- 💳 財布/メンタル HPゲージ演出 -->'
    '<div style="background-color: rgba(0,0,0,0.3); padding: 8px 10px; border-radius: 6px;">'
    '<div style="display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-bottom: 4px;">'
    "<span>💳 財布/メンタル HP</span>"
    "<span>"
    + hp_status
    + " "
    + str(hp_percent)
    + "%</span>"
    "</div>"
    '<div style="width: 100%; background-color: #334155; height: 8px; border-radius: 4px; overflow: hidden;">'
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

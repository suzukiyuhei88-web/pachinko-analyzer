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

# --- 2. ゾーンごとのデータ定義（ネガティブ ＆ ポジティブ対応） ---
ZONE_MESSAGES = {
    "peaceful": {
        "title": "まだ慌てるような時間じゃない",
        "neg_messages": [
            "まだ慌てるような時間じゃない。ここからが本番です。",
            "財布の紐はまだしっかり締まっています。平和な日常ですね。",
        ],
        "pos_messages": [
            "素晴らしい立ち上がり！このままの勢いで宇宙の真理に到達しましょう。",
            "平和な立ち上がり。今日のあなたは一味違う気がします。",
        ],
        "comparisons": [
            {
                "category": "日常・学校",
                "neg": "授業中、先生に当てられないかビクビクしてたら本当に当てられる確率",
                "pos": "なんとなく予習したページがそのままテストに出る確率",
            },
            {
                "category": "パチ・スロ",
                "neg": "朝イチのガセ前兆に惑わされて無駄に投資が膨らむ確率",
                "pos": "投資1Kでプレミアムフラグを引いてドヤ離席する確率",
            },
        ],
        "hp_percent": 100,
        "hp_status": "NORMAL (元気)",
        "card_bg": "#1e293b",
        "border_color": "#475569",
        "text_color": "#e2e8f0",
    },
    "caution": {
        "title": "ざわ… ざわ… ゾーン",
        "neg_messages": [
            "少し財布の紐がキュッとなる頃合い。深呼吸してコーヒーでもどうぞ。",
            "「もしかして、今日もやられる日なのでは…？」という悪寒が走り始める頃。",
        ],
        "pos_messages": [
            "ここからの巻き返しが一番ドラマチックなんです。期待値は爆上がり中！",
            "運命の歯車があなたの方を向き始めています。焦る必要はありません。",
        ],
        "comparisons": [
            {
                "category": "日常・学校",
                "neg": "購買のパン戦争で、お目当ての焼きそばパンが目の前で売り切れる確率",
                "pos": "自動販売機で当たりが出てもう一本ジュースがもらえる確率",
            },
            {
                "category": "科学",
                "neg": "スマホを落としたとき、画面ではなく背面から奇跡的に落ちる…と見せかけてバキバキになる確率",
                "pos": "身の回りの原子が奇跡的に整列してテレポートが起きる確率（ほぼゼロだけど夢はある）",
            },
        ],
        "hp_percent": 60,
        "hp_status": "CAUTION (注意)",
        "card_bg": "#1e293b",
        "border_color": "#64748b",
        "text_color": "#cbd5e1",
    },
    "yutime_ghost": {
        "title": "【幻の遊タイム】非搭載ゾーン",
        "neg_messages": [
            (
                "昔の基準なら【約 {yutime_rot}回転】で助かってましたね……（遠い目）"
            ),
            (
                "遊タイムという名の救済措置が消え去った現代の荒波を、生身で泳いでいます。"
            ),
        ],
        "pos_messages": [
            (
                "あえて遊タイムに頼らない！真の漢（おとこ）の自力引きが試される黄金期です！"
            ),
            (
                "これだけ耐えたのだから、ここから訪れる爆連のエネルギーは計り知れません。"
            ),
        ],
        "comparisons": [
            {
                "category": "パチ・スロ",
                "neg": "隣の台が「単発→即ヤメ」された直後に、別の人が座って一撃3万発出す確率",
                "pos": "自分の台に秘められたポテンシャルが全解放され、周囲がざわめき立つ確率",
            },
            {
                "category": "日常・学校",
                "neg": "提出期限を完全に勘違いしていて、前日の夜に絶望する確率",
                "pos": "先生の気まぐれで提出期限が1週間伸びる奇跡が起きる確率",
            },
        ],
        "hp_percent": 30,
        "hp_status": "WARNING (警告)",
        "card_bg": "#2e1065",
        "border_color": "#a855f7",
        "text_color": "#f3e8ff",
    },
    "deep": {
        "title": "領域展開（深海トラウマ）",
        "neg_messages": [
            (
                "RUSHに入った瞬間3秒で駆け抜けたあの日の虚しさに比べれば、このハマりなど微風です。"
            ),
            ("周囲の視線と、自分のメンタルが試されるディープゾーン。"),
        ],
        "pos_messages": [
            (
                "歴史に名を残す大当たりのための『溜め』が完了しつつあります。神様もそろそろ目を覚ますはず！"
            ),
            (
                "ここまで耐えたあなたには、全パチンカーを称賛する資格があります。伝説の目撃者になろう！"
            ),
        ],
        "comparisons": [
            {
                "category": "日常・学校",
                "neg": "テストで「絶対に合っている」と確信した答えが、盛大に勘違いだった確率",
                "pos": "テストのヤマ勘がすべて的中して学年1位をかっさらっていく確率",
            },
            {
                "category": "科学",
                "neg": "トーストを落としたとき、100%ジャムを塗った面から地面に直撃する確率",
                "pos": "隕石が直撃する確率よりは低いので、実質安全です。",
            },
        ],
        "hp_percent": 10,
        "hp_status": "DANGER (瀕死)",
        "card_bg": "#431407",
        "border_color": "#ea580c",
        "text_color": "#ffedd5",
    },
    "god": {
        "title": "歴史に名を刻むレベル",
        "neg_messages": [
            ("もはや語るまい。歴史に名を刻むレベルのレア体験デス。"),
            ("確率の女神に完全に嫌われているか、別の何かを召喚している状態です。"),
        ],
        "pos_messages": [
            (
                "おめでとうございます！ 宇宙の確率変動を引き当てた『選ばれし神』の領域です！"
            ),
            (
                "これほどの不運を耐え抜いたあなたには、今後すべての幸運が雪崩れ込んでくることでしょう！"
            ),
        ],
        "comparisons": [
            {
                "category": "科学",
                "neg": "量子力学のバグを疑うレベル。物理法則があなたに対して反逆しています。",
                "pos": "ノーベル賞クラスの大発見に匹敵する、統計学上のレアロマン！",
            },
            {
                "category": "パチ・スロ",
                "neg": "財布のなかの諭吉が、羽が生えたようにではなく、自発的に消えていく怪奇現象。",
                "pos": "この後の大当りで、これまでの負けをすべてお釣りが来るほど捲くる大ストーリーの序章！",
            },
        ],
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

# モード選択スイッチ
diag_mode = st.radio(
    "診断モードを選択",
    ["🖤 ネガティブ（絶望・自虐）", "💖 ポジティブ（狂気的肯定）"],
    index=0,
    horizontal=True,
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

# --- 4. スライダーによる直感的な回転数調整 ---
max_slider = int(p_denom * 6)
step_val = 5 if p_denom <= 100 else 10

current_rotation = st.slider(
    "現在の回転数",
    min_value=0,
    max_value=max_slider,
    value=min(500, max_slider),
    step=step_val,
)

# --- 5. 計算ロジック ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100

# --- 6. 演出・ステータス分岐 ---
st.markdown("---")

if prob_ハマり > 50:
  zone_key = "peaceful"
elif prob_ハマり > 20:
  zone_key = "caution"
elif prob_ハマり > 10:
  zone_key = "yutime_ghost"
elif prob_ハマり > 1.0:
  zone_key = "deep"
else:
  zone_key = "god"

zone_data = ZONE_MESSAGES[zone_key]

status_title = zone_data["title"]
card_bg = zone_data["card_bg"]
border_color = zone_data["border_color"]
text_color = zone_data["text_color"]
hp_percent = zone_data["hp_percent"]
hp_status = zone_data["hp_status"]

# モードに応じたメッセージと比べるネタの選定
if "ネガティブ" in diag_mode:
  comment = random.choice(zone_data["neg_messages"])
  comparison_item = random.choice(zone_data["comparisons"])
  comparison_text = comparison_item["neg"]
  comparison_category = comparison_item["category"]
  image_url = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_kuyashii_man.png"
else:
  comment = random.choice(zone_data["pos_messages"])
  comparison_item = random.choice(zone_data["comparisons"])
  comparison_text = comparison_item["pos"]
  comparison_category = comparison_item["category"]
  image_url = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhqMv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7XJL4e9N7R4ZEolfQVo/s400/pose_yરો_man.png"  # ポジティブ用（あるいは明るい画像）
  # 念のため安全な画像フォールバック
  image_url = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhzxQjD1GLGo16hp2YGk_2eKSbv5WdLfhy6O0c8SN7UrWMxB_AGKMfYDml7ESXhQWvy_RLGNnIHbrrjcnB0Fzt177ND7zvEnCbgsKa7gDsmDLwGHSldHP1jmV6n7R4ZEolfQVo/s400/pose_kuyashii_man.png"

if zone_key == "yutime_ghost":
  yutime_rot = int(p_denom * 3)
  comment = comment.format(yutime_rot=yutime_rot)

# --- 7. 統合メインカード ---
card_html = (
    '<div style="border: 3px double '
    + border_color
    + "; background-color: "
    + card_bg
    + '; padding: 14px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">'
    '<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 6px; margin-bottom: 10px; font-size: 12px; color: #94a3b8;">'
    '<span>スペック: <b style="color: #f8fafc;">1 / '
    + str(p_denom)
    + "</b></span>"
    '<span>現在: <b style="color: #f8fafc;">'
    + str(current_rotation)
    + "回転</b></span>"
    "</div>"
    '<div style="text-align: center; margin-bottom: 8px;">'
    '<div style="font-size: 12px; color: '
    + text_color
    + '; text-transform: uppercase; letter-spacing: 2px;">'
    + status_title
    + "</div>"
    "</div>"
    '<div style="display: flex; align-items: center; justify-content: space-around; margin-bottom: 10px; background-color: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px;">'
    '<div style="text-align: left;">'
    '<h2 style="color: '
    + text_color
    + '; margin: 0; font-size: 36px; letter-spacing: 1px;">'
    + f"{prob_ハマり:.1f}%"
    + "</h2>"
    '<div style="font-size: 10px; color: '
    + text_color
    + '; opacity: 0.8;">（この回転数まで当らない確率）</div>'
    "</div>"
    "<div>"
    '<img src="'
    + image_url
    + '" style="width: 60px; height: 60px; object-fit: contain; border-radius: 50%; background-color: rgba(255,255,255,0.9); padding: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />'
    "</div>"
    "</div>"
    '<p style="font-size: 13px; color: '
    + text_color
    + '; line-height: 1.4; margin-bottom: 10px; text-align: center; padding: 0 4px;">'
    + comment
    + "</p>"
    '<div style="background-color: rgba(0, 0, 0, 0.4); border: 1px dashed '
    + border_color
    + '; padding: 8px 10px; border-radius: 6px; text-align: left; margin-bottom: 10px;">'
    '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">'
    '<span style="font-size: 10px; color: #38bdf8; font-weight: bold; background-color: rgba(56, 189, 248, 0.1); padding: 1px 5px; border-radius: 4px;">'
    + comparison_category
    + "</span>"
    "</div>"
    '<p style="font-size: 11px; color: '
    + text_color
    + '; margin: 0; line-height: 1.3;">🎯 '
    + comparison_text
    + "</p>"
    "</div>"
    '<!-- 💳 財布/メンタル HPゲージ演出 -->'
    '<div style="background-color: rgba(0,0,0,0.3); padding: 6px 8px; border-radius: 6px;">'
    '<div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 3px;">'
    "<span>💳 財布/メンタル HP</span>"
    "<span>"
    + hp_status
    + " "
    + str(hp_percent)
    + "%</span>"
    "</div>"
    '<div style="width: 100%; background-color: #334155; height: 6px; border-radius: 3px; overflow: hidden;">'
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

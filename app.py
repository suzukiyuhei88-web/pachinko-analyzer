import math
import random
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ページの基本設定
st.set_page_config(
    page_title="パチンコ確率診断 - Statistical & Cynical", page_icon="🎰", layout="centered"
)

# --- 0. CSVデータの読み込みと数値化パース ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('neta_master.csv')
        def parse_probability(text):
            text_str = str(text)
            if '1/36' in text_str:
                return 1/36 * 100
            if '432万分の1' in text_str or '0.000023%' in text_str:
                return 0.000023
            if '65万分の1' in text_str or '0.00015%' in text_str:
                return 0.00015
            if '1000兆分の1' in text_str:
                return 1e-12
            if '数百万分の1' in text_str or '0.00001%' in text_str:
                return 0.00001
            import re
            matches = re.findall(r'([0-9]+\.?[0-9]*)%', text_str)
            if matches:
                return float(matches[0])
            ranges = re.findall(r'([0-9]+\.?[0-9]*)%?[〜~]([0-9]+\.?[0-9]*)%', text_str)
            if ranges:
                return (float(ranges[0][0]) + float(ranges[0][1])) / 2.0
            return 50.0
        
        df['prob_val'] = df['確率・数値'].apply(parse_probability)
        return df
    except Exception:
        return None

df_master = load_data()

# --- 1. デザイン用のカスタムCSS ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, p {
        font-family: 'DotGothic16', sans-serif !important;
    }
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    label, .stRadio p, .stSlider p {
        color: #cbd5e1 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. 状態判定（1, 4, 5 と連動：タイトル、HP、カラー、背景色）の定義 ---
ZONE_DEFINITIONS = {
    "peaceful": {
        "title": "平穏域 (NORMAL)",
        "hp_percent": 100,
        "hp_status": "STABLE",
        "border_color": "#3b82f6",
        "accent_color": "#60a5fa",
        "bg_color": "#0d1b2a",
    },
    "caution": {
        "title": "警戒域 (CAUTION)",
        "hp_percent": 60,
        "hp_status": "CAUTION",
        "border_color": "#10b981",
        "accent_color": "#34d399",
        "bg_color": "#062318",
    },
    "yutime_ghost": {
        "title": "警告域 / 遊タイム非搭載 (WARNING)",
        "hp_percent": 30,
        "hp_status": "WARNING",
        "border_color": "#a855f7",
        "accent_color": "#c084fc",
        "bg_color": "#1e102f",
    },
    "deep": {
        "title": "深海トラウマ領域 (DEEP)",
        "hp_percent": 10,
        "hp_status": "DANGER",
        "border_color": "#f97316",
        "accent_color": "#fb923c",
        "bg_color": "#2c150b",
    },
    "god": {
        "title": "確率特異点 / 神の領域 (SINGULARITY)",
        "hp_percent": 1,
        "hp_status": "CRITICAL",
        "border_color": "#ef4444",
        "accent_color": "#f87171",
        "bg_color": "#2d0f0f",
    },
}

# --- 3. タイトルと選択エリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center; letter-spacing: 2px;'>🎰 パチンコ確率診断コア</h3>",
    unsafe_allow_html=True,
)

spec_options = {
    "甘デジ (1/99)": 99.9,
    "ライトミドル (1/199)": 199.8,
    "ミドル (1/319)": 319.6,
    "ラッキートリガー (1/349)": 349.0,
    "カスタム": 0.0,
}

selected_spec_name = st.selectbox("機種スペック", list(spec_options.keys()), index=2)

if selected_spec_name == "カスタム":
    p_denom = st.number_input("大当り確率の分母", min_value=1.1, value=319.6, step=0.1)
else:
    p_denom = spec_options[selected_spec_name]

# --- 4. スライダーによる回転数調整 ---
max_slider = int(p_denom * 6)
current_rotation = st.slider("現在のハマり回転数", min_value=0, max_value=max_slider, value=min(300, max_slider), step=10)

# --- 5. 計算ロジック ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100

# --- 6. 状態判定の決定（1, 4, 5用） ---
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

zone_data = ZONE_DEFINITIONS[zone_key]

# --- 7. CSVネタマッチング（無機質アナライザー用） ---
if df_master is not None and len(df_master) > 0:
    df_master['diff'] = (df_master['prob_val'] - prob_ハマり).abs()
    closest_row = df_master.loc[df_master['diff'].idxmin()]
    approx_rate = str(closest_row.get('確率・数値', ''))
    comparison_text = str(closest_row.get('事象', '')) + "：" + str(closest_row.get('コメント', ''))
else:
    approx_rate = f"約 {prob_ハマり:.1f}%"
    comparison_text = "計算されたハマり確率に合致する日常の事象"

# --- 8. ハマり確率に依存する要素（2. キャラクターセリフ ＆ 3. フッター）のバリエーション ---
hash_seed = int(prob_ハマり * 1000) % 3

if prob_ハマり > 50:
    comments = [
        "「まだ投資も浅いし、気楽なもんですわ。ここから地獄が始まるとも知らずにね」",
        "「おや、まだ財布に余裕がある顔をしていますね。今のうちに楽しんでおきなさいよ」",
        "「この辺りはまだウォーミングアップみたいなもんです。本番はここからですよ」"
    ]
    footers = [
        "※台の機嫌はあなたとは無関係に一定の確率で抽選し続けています。",
        "※まだ傷は浅いです。引き返すなら今のうちかもしれませんよ。",
        "※確率の収束を信じる者は、大抵財布をすり減らします。"
    ]
elif prob_ハマり > 20:
    comments = [
        "「『そろそろ当たるはず』？ いいえ、確率の抽選は毎回リセットですよ。都合よく解釈しないことですね」",
        "「おや、嫌な汗かいてます？ まだまだ中ハマりの入口に立ったばかりですって」",
        "「隣の台が連チャンしているのを見てイライラする、一番メンタルが削られる時間帯ですね」"
    ]
    footers = [
        "※確率に「そろそろ」という概念は存在しません。",
        "※「次で当たる気がする」その錯覚がホールの養分を生み出します。",
        "※過去の投資額は、次の当りの確率を1ミリも上げてくれません。"
    ]
elif prob_ハマり > 10:
    yutime_rot = int(p_denom * 3)
    comments = [
        f"「昔の台ならここで遊タイムの救済があったんですけどねえ……現代の荒波スペックじゃただの養分ロードですわ（※目安約 {yutime_rot}回転）」",
        "「お財布の中身、ちょっと裏のATMに補充しに行ってきます？ いや、笑い事じゃなくなってきましたよ」",
        "「スペックの重さを身をもって体感するゾーンへようこそ。逃げるなら今のうちですってば」"
    ]
    footers = [
        "※冷徹な液晶演出だけが、あなたの財布のHPを削っていきます。",
        "※「ここまで入れたんだから」というサンクコスト効果に囚われていませんか？",
        "※台はあなたを覚えているわけではありません。ただ淡々と金を吸い込んでいます。"
    ]
elif prob_ハマり > 1.0:
    comments = [
        "「ここまで来ると、もはや引き際が見えなくなってパチンコ屋のATMとトモダチ状態ですね。お疲れ様です」",
        "「もはや意地でも当てるまで帰れない雰囲気が漂っていますね。財布の命日も近そうです」",
        "「すげえ深くまで潜りましたねぇ。酸欠で脳の血管が一本切れそうな頃合いじゃありませんか？」"
    ]
    footers = [
        "※ハンドルを固定したところで、数学的確率は1ミリも変動しません。",
        "※負債の沼は深く、あなたの理性をも一緒に沈めていきます。",
        "※帰るに帰れないその足取り、完全にホールのカモのそれですよ。"
    ]
else:
    comments = [
        "「いやあ、見事な下振れ芸ですね！ 凡人には真似できない領域の数字を叩き出してますよ、ある意味で誇っていいんじゃないですか？」",
        "「おめでとうございます！ 確率のバグを踏み抜いた選ばれし者だけが見られる絶景がお待ちです」",
        "「もはやここまで来ると芸術ですね。記念にサンドに入れた万札の枚数を数えておきましょうか」"
    ]
    footers = [
        "※周囲の視線は同情か、あるいは反面教師を見るような冷ややかなものです。",
        "※これほどの低確率を引く強運、別のことに使っていれば人生が変わっていたかもしれませんね。",
        "※神様も呆れて見ていることでしょう。お疲れ様でした。"
    ]

comment_text = comments[hash_seed % len(comments)]
footer_cynic = footers[hash_seed % len(footers)]

# --- 9. 2軸構造化カードの構築 ---
border_color = zone_data['border_color']
accent_color = zone_data['accent_color']
bg_color = zone_data['bg_color']
hp_percent = zone_data['hp_percent']

card_html = f"""
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&display=swap" rel="stylesheet">
<style>
* {{
    font-family: 'DotGothic16', sans-serif !important;
}}
</style>
<div style="border: 2px solid {border_color}; background-color: {bg_color}; color: #f8fafc; padding: 20px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); max-width: 500px; margin: 0 auto; box-sizing: border-box; transition: background-color 0.4s ease, border-color 0.4s ease;">
    
    <!-- 【ベース】データコア -->
    <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-bottom: 4px;">
            <span>スペック: <b>1/{p_denom}</b></span>
            <span>現在回転数: <b style="color: #fff;">{current_rotation}回転</b></span>
        </div>
        <div style="text-align: center; background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
            <div style="font-size: 34px; color: {accent_color}; font-weight: bold; line-height: 1.1; margin: 2px 0;">{prob_ハマり:.2f}%</div>
            <div style="font-size: 10px; color: #94a3b8;">（この回転数まで一度も当らない数学的確率）</div>
        </div>
    </div>

    <!-- 【軸1】無機質アナライザー（科学的スケール比較） -->
    <div style="background-color: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 6px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; font-size: 9px; color: #64748b; letter-spacing: 1px; margin-bottom: 4px;">
            <span>[ SYSTEM: OBJECTIVE_ANALYSIS ]</span>
            <span style="color: #38bdf8;">{approx_rate}</span>
        </div>
        <div style="font-size: 11px; color: #cbd5e1; line-height: 1.3;">
            <span style="color: #38bdf8;">>></span> {comparison_text}
        </div>
    </div>

    <!-- 【軸2】キャラクターセリフ枠（ハマり確率に依存するコメント） -->
    <div style="margin-bottom: 12px;">
        <div style="font-size: 10px; color: {accent_color}; letter-spacing: 1px; margin-bottom: 4px;">■ 状態判定: {zone_data['title']}</div>
        
        <div style="display: flex; align-items: flex-start; background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 6px;">
            <div style="min-width: 40px; height: 40px; background-color: rgba(0,0,0,0.3); border: 1px dashed {accent_color}; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #94a3b8; margin-right: 10px; text-align: center;">
                [ICON]
            </div>
            <div style="font-size: 12px; color: #f1f5f9; line-height: 1.4;">
                {comment_text}
            </div>
        </div>
    </div>

    <!-- 財布・メンタル HPゲージ（状態判定に連動 ＋ トランジションアニメーション追加） -->
    <div style="background-color: rgba(0,0,0,0.3); padding: 6px 10px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 3px;">
            <span>💳 財布 / メンタル残存値</span>
            <span>{zone_data['hp_status']} ({hp_percent}%)</span>
        </div>
        <div style="width: 100%; background-color: rgba(0,0,0,0.5); height: 5px; border-radius: 3px; overflow: hidden;">
            <div style="width: {hp_percent}%; background-color: {border_color}; height: 100%; transition: width 0.4s ease, background-color 0.4s ease;"></div>
        </div>
    </div>

    <!-- サブリミナル・フッター（ハマり確率に依存する皮肉） -->
    <div style="text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
        {footer_cynic}
    </div>

</div>
"""

components.html(card_html, height=560, scrolling=False)

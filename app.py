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
    label, .stRadio p, .stNumberInput p {
        color: #cbd5e1 !important;
        font-family: 'DotGothic16', sans-serif !important;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }
    /* ラジオボタンをコンパクトに横並びさせる調整 */
    .stRadio > div {
        flex-direction: row !important;
        gap: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. 状態判定（倍率ベース）の定義 ---
ZONE_DEFINITIONS = {
    "peaceful": {
        "title": "平穏域 / 超初期 (NORMAL)",
        "hp_percent": 100,
        "hp_status": "STABLE",
        "border_color": "#3b82f6",
        "accent_color": "#60a5fa",
        "bg_color": "#0d1b2a",
    },
    "caution": {
        "title": "警戒域 / 分母以内 (CAUTION)",
        "hp_percent": 75,
        "hp_status": "CAUTION",
        "border_color": "#10b981",
        "accent_color": "#34d399",
        "bg_color": "#062318",
    },
    "yutime_ghost": {
        "title": "警告域 / 2倍ハマり圏 (WARNING)",
        "hp_percent": 50,
        "hp_status": "WARNING",
        "border_color": "#a855f7",
        "accent_color": "#c084fc",
        "bg_color": "#1e102f",
    },
    "deep": {
        "title": "深海トラウマ領域 / 3倍ハマり圏 (DEEP)",
        "hp_percent": 25,
        "hp_status": "DANGER",
        "border_color": "#f97316",
        "accent_color": "#fb923c",
        "bg_color": "#2c150b",
    },
    "god": {
        "title": "確率特異点 / 神の領域 (SINGULARITY)",
        "hp_percent": 5,
        "hp_status": "CRITICAL",
        "border_color": "#ef4444",
        "accent_color": "#f87171",
        "bg_color": "#2d0f0f",
    },
}

# --- 3. タイトルとコントロールエリア ---
st.markdown(
    "<h3 style='color: #f8fafc; text-align: center; letter-spacing: 2px; margin-bottom: 8px;'>🎰 パチンコ確率診断コア</h3>",
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

# セッションステートで回転数を管理
if 'rotation_input' not in st.session_state or st.session_state.get('last_spec') != p_denom:
    st.session_state['rotation_input'] = min(300, int(p_denom * 6))
    st.session_state['last_spec'] = p_denom

# クイックジャンプ（0.5倍、1倍、2倍、3倍）
st.markdown("<p style='font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;'>▼ クイックジャンプ（倍率選択）</p>", unsafe_allow_html=True)
jump_option = st.radio(
    "クイックジャンプ",
    ["微調整", "0.5倍", "1倍(分母)", "2倍", "3倍"],
    horizontal=True,
    label_visibility="collapsed"
)

# 選択された倍率に応じて回転数を即座にセット
if jump_option == "0.5倍":
    st.session_state['rotation_input'] = int(p_denom * 0.5)
elif jump_option == "1倍(分母)":
    st.session_state['rotation_input'] = int(p_denom * 1.0)
elif jump_option == "2倍":
    st.session_state['rotation_input'] = int(p_denom * 2.0)
elif jump_option == "3倍":
    st.session_state['rotation_input'] = int(p_denom * 3.0)

# number_input 配置
max_limit = int(p_denom * 6)
current_rotation = st.number_input(
    "現在のハマり回転数（データカウンターの数字）",
    min_value=0,
    max_value=max_limit,
    step=1,
    key='rotation_input'
)

# --- 4. 計算ロジック ---
p = 1.0 / p_denom if p_denom > 0 else 0
prob_ハマり = ((1.0 - p) ** current_rotation) * 100
rotation_ratio = current_rotation / p_denom if p_denom > 0 else 0

# --- 5. 状態判定の決定 ---
if rotation_ratio < 0.31:
    zone_key = "peaceful"
elif rotation_ratio < 1.0:
    zone_key = "caution"
elif rotation_ratio < 2.0:
    zone_key = "yutime_ghost"
elif rotation_ratio < 3.0:
    zone_key = "deep"
else:
    zone_key = "god"

zone_data = ZONE_DEFINITIONS[zone_key]

# --- 6. CSVネタマッチング ---
if df_master is not None and len(df_master) > 0:
    df_master['diff'] = (df_master['prob_val'] - prob_ハマり).abs()
    closest_row = df_master.loc[df_master['diff'].idxmin()]
    approx_rate = str(closest_row.get('確率・数値', ''))
    comparison_text = str(closest_row.get('事象', '')) + "：" + str(closest_row.get('コメント', ''))
else:
    approx_rate = f"約 {prob_ハマり:.1f}%"
    comparison_text = "計算されたハマり確率に合致する日常の事象"

# --- 7. セリフ＆フッター ---
hash_seed = int(prob_ハマり * 1000) % 3

if zone_key == "peaceful":
    comments = [
        "「おっ、早めの当りですね！ まだ財布も心もノーダメージでウハウハな時間帯ですわ」",
        "「このスピード感で当たってくれると助かるんですけどねぇ。まあ、油断大敵ですよ」",
        "「サクッと初当りを引けてご機嫌なご様子。ここから連チャンを伸ばせるかが見せ所ですね」"
    ]
    footers = [
        "※早い当りは嬉しいですが、持ち玉の維持こそが勝負の分かれ道です。",
        "※この調子でプラス域をキープしてさっさと逃げたいところですね。",
        "※確率の恩恵を素直に受け取っておきましょう。"
    ]
elif zone_key == "caution":
    comments = [
        "「確率分母以内ですからね、まだまだ『まあまあ許容範囲内』ってところですわ」",
        "「『そろそろ当たるはず』……いやいや、分母以内ならまだ平常運転ですよ。気楽にいきましょう」",
        "「ここまでは想定内の挙動ですね。焦らず淡々とハンドルを握っていきましょうか」"
    ]
    footers = [
        "※確率分母以内での当りは全体の約63%です。まだ普通の範囲内ですね。",
        "※ここから先が本当の地獄の始まり……なんて冗談ですけど、油断は禁物です。",
        "※財布のHPはまだ満タンに近いです。"
    ]
elif zone_key == "yutime_ghost":
    comments = [
        "「うーん、分母を超えて2倍ハマりコースですか。まあ、パチンコ打ってりゃよくある日常風景ですね」",
        "「『こんな時もあるさ』と自分に言い聞かせるフェーズですね。まだメンタルは折れてません？」",
        "「ちょっと嫌な汗をかく頃合いですが、ここから一撃でまくる台も多いですからねえ」"
    ]
    footers = [
        "※2倍ハマりに到達する確率は約13.5%です。まだまだよくある日常です。",
        "※「ここから取り返せばいいや」という甘い期待が泥沼の始まりです。",
        "※演出の派手さと裏腹に、財布の残高は着実に削られています。"
    ]
elif zone_key == "deep":
    comments = [
        "<span>「おや、3倍ハマり手前まで来ましたか。ちょっと雲行きが怪しくなってきましたねぇ……」</span>",
        "「ここまで来ると『ここまで入れたんだからRUSH入れて取り返さないと割に合わない』って思考になりがちですね」",
        "「じっと耐える時間帯です。隣の連チャンを横目に見ながらメンタルを保てるかが勝負ですよ」"
    ]
    footers = [
        "※3倍ハマりに到達する確率は約5%未満。そろそろ不穏な領域です。",
        "※サンクコスト効果に支配されていませんか？ 冷静になりましょう。",
        "※ハンドルを固定したところで、確率はあなたに微笑みません。"
    ]
else:
    comments = [
        "「出ました、3倍ハマり超の虚無ゾーン！ もはや当たろうが当たるまいが、ムキになってサンドに札を入れるだけの作業ですね」",
        "<span>「ここまで来ると笑うしかありませんね！ 脳から変なアドレナリンが出ているのを感じませんか？」</span>",
        "「お疲れ様です。パチンコ屋のATMに多額の寄付をする尊いボランティア、見事な狂気っぷりですね！」"
    ]
    footers = [
        "※ここから当たる確率はごくわずか。完全な虚無との戦いです。",
        "※周囲の視線は同情、あるいは哀れみを含んだものに変わっています。",
        "※財布の命日へようこそ。撤退の二文字はすでに脳内から消えています。"
    ]

comment_text = comments[hash_seed % len(comments)]
footer_cynic = footers[hash_seed % len(footers)]

# --- 8. カード構築（ユーザー入力のスペックと現在回転数、倍率をより目立たせる改善） ---
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
<div style="border: 2px solid {border_color}; background-color: {bg_color}; color: #f8fafc; padding: 16px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); max-width: 500px; margin: 5px auto 0 auto; box-sizing: border-box; transition: background-color 0.4s ease, border-color 0.4s ease;">
    
    <!-- 【最上部】状態判定ヘッダー -->
    <div style="background-color: rgba(0,0,0,0.4); border-left: 4px solid {accent_color}; padding: 8px 12px; border-radius: 4px; margin-bottom: 12px;">
        <div style="font-size: 9px; color: #94a3b8; letter-spacing: 1px;">■ 現在の状態判定</div>
        <div style="font-size: 14px; color: {accent_color}; font-weight: bold; margin-top: 2px;">{zone_data['title']}</div>
    </div>

    <!-- 【メイン強調】ユーザー入力値（スペック & 現在回転数 & 倍率） -->
    <div style="background-color: rgba(0,0,0,0.45); border: 1px solid rgba(255,255,255,0.15); padding: 12px; border-radius: 6px; margin-bottom: 12px; text-align: center;">
        <div style="font-size: 10px; color: #94a3b8; margin-bottom: 4px; letter-spacing: 1px;">[ INPUT_STATUS : 1/{p_denom} ]</div>
        <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 8px;">
            <div>
                <div style="font-size: 9px; color: #94a3b8;">現在回転数</div>
                <div style="font-size: 26px; color: #ffffff; font-weight: bold;">{current_rotation} <span style="font-size: 12px; color: #94a3b8;">回転</span></div>
            </div>
            <div style="border-left: 1px solid rgba(255,255,255,0.15); height: 35px;"></div>
            <div>
                <div style="font-size: 9px; color: #94a3b8;">ハマり度合い</div>
                <div style="font-size: 26px; color: {accent_color}; font-weight: bold;">{rotation_ratio:.2f} <span style="font-size: 12px; color: #94a3b8;">倍</span></div>
            </div>
        </div>
        <div style="border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 8px;">
            <div style="font-size: 11px; color: #94a3b8;">ここまでの累計非当選確率</div>
            <div style="font-size: 28px; color: {accent_color}; font-weight: bold; line-height: 1.1; margin-top: 2px;">{prob_ハマり:.2f}%</div>
        </div>
    </div>

    <!-- 【軸1】無機質アナライザー -->
    <div style="background-color: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 9px; color: #64748b; letter-spacing: 1px; margin-bottom: 3px;">
            <span>[ SYSTEM: OBJECTIVE_ANALYSIS ]</span>
            <span style="color: #38bdf8;">{approx_rate}</span>
        </div>
        <div style="font-size: 11px; color: #cbd5e1; line-height: 1.3;">
            <span style="color: #38bdf8;">>></span> {comparison_text}
        </div>
    </div>

    <!-- 【軸2】キャラクターセリフ枠 -->
    <div style="margin-bottom: 10px;">
        <div style="display: flex; align-items: flex-start; background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px;">
            <div style="min-width: 36px; height: 36px; background-color: rgba(0,0,0,0.3); border: 1px dashed {accent_color}; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #94a3b8; margin-right: 8px; text-align: center;">
                [ICON]
            </div>
            <div style="font-size: 11px; color: #f1f5f9; line-height: 1.4;">
                {comment_text}
            </div>
        </div>
    </div>

    <!-- 財布・メンタル HPゲージ -->
    <div style="background-color: rgba(0,0,0,0.3); padding: 6px 10px; border-radius: 6px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 2px;">
            <span>💳 財布 / メンタル残存値</span>
            <span>{zone_data['hp_status']} ({hp_percent}%)</span>
        </div>
        <div style="width: 100%; background-color: rgba(0,0,0,0.5); height: 4px; border-radius: 2px; overflow: hidden;">
            <div style="width: {hp_percent}%; background-color: {border_color}; height: 100%; transition: width 0.4s ease, background-color 0.4s ease;"></div>
        </div>
    </div>

    <!-- サブリミナル・フッター -->
    <div style="text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
        {footer_cynic}
    </div>

</div>
"""

components.html(card_html, height=600, scrolling=False)

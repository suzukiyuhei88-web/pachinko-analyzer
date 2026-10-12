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

# --- 2. 状態判定（倍率ベース：タイトル、HP、カラー、背景色）の定義 ---
ZONE_DEFINITIONS = {
    "peaceful": { # 0.3倍未満（約100回転相当未満：早い！）
        "title": "平穏域 / 超初期 (NORMAL)",
        "hp_percent": 100,
        "hp_status": "STABLE",
        "border_color": "#3b82f6",
        "accent_color": "#60a5fa",
        "bg_color": "#0d1b2a",
    },
    "caution": { # 0.3倍 〜 1.0倍（確率分母以内：まぁまぁいい方）
        "title": "警戒域 / 分母以内 (CAUTION)",
        "hp_percent": 75,
        "hp_status": "CAUTION",
        "border_color": "#10b981",
        "accent_color": "#34d399",
        "bg_color": "#062318",
    },
    "yutime_ghost": { # 1.0倍 〜 2.0倍（2倍ハマり以内：こんな時もある普通）
        "title": "警告域 / 2倍ハマり圏 (WARNING)",
        "hp_percent": 50,
        "hp_status": "WARNING",
        "border_color": "#a855f7",
        "accent_color": "#c084fc",
        "bg_color": "#1e102f",
    },
    "deep": { # 2.0倍 〜 3.0倍（3倍ハマり以内：ちょっとハマった、RUSHで逆転）
        "title": "深海トラウマ領域 / 3倍ハマり圏 (DEEP)",
        "hp_percent": 25,
        "hp_status": "DANGER",
        "border_color": "#f97316",
        "accent_color": "#fb923c",
        "bg_color": "#2c150b",
    },
    "god": { # 3.0倍超（それ以上：虚無、ムキになって回す）
        "title": "確率特異点 / 3倍超過・神の領域 (SINGULARITY)",
        "hp_percent": 5,
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

# 確率分母に対する現在の倍率（ハマり度合い）を算出
rotation_ratio = current_rotation / p_denom if p_denom > 0 else 0

# --- 6. 状態判定の決定（スペック共通の倍率ベースで分岐） ---
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

# --- 7. CSVネタマッチング（無機質アナライザー用） ---
if df_master is not None and len(df_master) > 0:
    df_master['diff'] = (df_master['prob_val'] - prob_ハマり).abs()
    closest_row = df_master.loc[df_master['diff'].idxmin()]
    approx_rate = str(closest_row.get('確率・数値', ''))
    comparison_text = str(closest_row.get('事象', '')) + "：" + str(closest_row.get('コメント', ''))
else:
    approx_rate = f"約 {prob_ハマり:.1f}%"
    comparison_text = "計算されたハマり確率に合致する日常の事象"

# --- 8. プレイヤーの体感・感情に合わせたセリフ＆フッターのバリエーション ---
hash_seed = int(prob_ハマり * 1000) % 3

if zone_key == "peaceful": # 0.3倍未満（早めの当り）
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
elif zone_key == "caution": # 0.3倍〜1.0倍（分母以内）
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
elif zone_key == "yutime_ghost": # 1.0倍〜2.0倍（2倍ハマり以内）
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
elif zone_key == "deep": # 2.0倍〜3.0倍（3倍ハマり以内）
    comments = [
        "「おや、3倍ハマり手前まで来ましたか。ちょっと雲行きが怪しくなってきましたねぇ……」",
        "「ここまで来ると『ここまで入れたんだからRUSH入れて取り返さないと割に合わない』って思考になりがちですね」",
        "「じっと耐える時間帯です。隣の連チャンを横目に見ながらメンタルを保てるかが勝負ですよ」"
    ]
    footers = [
        "※3倍ハマりに到達する確率は約5%未満。そろそろ不穏な領域です。",
        "※サンクコスト効果に支配されていませんか？ 冷静になりましょう。",
        "※ハンドルを固定したところで、確率はあなたに微笑みません。"
    ]
else: # 3.0倍超（それ以上：虚無、ムキになって回す）
    comments = [
        "「出ました、3倍ハマり超の虚無ゾーン！ もはや当たろうが当たるまいが、ムキになってサンドに札を入れるだけの作業ですね」",
        "「ここまで来ると笑うしかありませんね！ 脳から変なアドレナリンが出ているのを感じませんか？」",
        "「お疲れ様です。パチンコ屋のATMに多額の寄付をする尊いボランティア、見事な狂気っぷりですね！」"
    ]
    footers = [
        "※ここから当たる確率はごくわずか。完全な虚無との戦いです。",
        "※周囲の視線は同情、あるいは哀れみを含んだものに変わっています。",
        "※財布の命日へようこそ。撤退の二文字はすでに脳内から消えています。"
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
            <span>スペック: <b>1/{p_denom}</b> (現在 {rotation_ratio:.2f}倍ハマり)</span>
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

    <!-- 【軸2】キャラクターセリフ枠（感情のグラデーションに連動） -->
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

    <!-- 財布・メンタル HPゲージ -->
    <div style="background-color: rgba(0,0,0,0.3); padding: 6px 10px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-bottom: 3px;">
            <span>💳 財布 / メンタル残存値</span>
            <span>{zone_data['hp_status']} ({hp_percent}%)</span>
        </div>
        <div style="width: 100%; background-color: rgba(0,0,0,0.5); height: 5px; border-radius: 3px; overflow: hidden;">
            <div style="width: {hp_percent}%; background-color: {border_color}; height: 100%; transition: width 0.4s ease, background-color 0.4s ease;"></div>
        </div>
    </div>

    <!-- サブリミナル・フッター -->
    <div style="text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
        {footer_cynic}
    </div>

</div>
"""

components.html(card_html, height=560, scrolling=False)

import streamlit as st
import json
import re
import requests
import matplotlib.pyplot as plt
import japanize_matplotlib
from io import BytesIO
# textwrapは、現時点では不要かもしれませんが、念のため残しておきます
# import textwrap 

# --- 1. 設定セクション ---
# APIキーの設定など、最初に必要な設定を記述
try:
    # genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # model = genai.GenerativeModel("gemini-1.5-flash")
    # ※現在API呼び出しをコメントアウトしているため、一旦こちらもコメントアウト
    pass # 何もしない
except Exception as e:
    st.error("APIキーの設定に失敗しました。")
    st.stop()

# --- 2. 関数定義セクション ---
# 機能ごとにコードを整理します

def create_prompt(theme, x_axis_name, x_axis_desc, y_axis_name, y_axis_desc):
    """AIへの指示（プロンプト）を作成する関数"""
    prompt = f"""
    テーマ「{theme}」について、以下の2軸で商品を10個から15個選んで、マトリクスを作成してください。

    ■X軸：{x_axis_name}（{x_axis_desc}）
    ■Y軸：{y_axis_name}（{y_axis_desc}）

    # 指示
    - X軸とY軸の値を、それぞれ0から100の範囲の数値で評価してください。
    - X軸は左端が0、右端が100です。
    - Y軸は下端が0、上端が100です。
    - 日本で実際に市販されている具体的な商品名を挙げてください。
    - 必ず以下のJSON形式の配列で出力してください。説明文や```json ```は不要です。

    [
      {{
        "name": "商品名1",
        "x": 80,
        "y": 70
      }},
      {{
        "name": "商品名2",
        "x": 20,
        "y": 30
      }}
    ]
    """
    return prompt

def get_data_from_ai(prompt):
    """AIを実行してデータを取得する関数（※現在はダミーデータを返します）"""
    # response = model.generate_content(prompt)
    # output_text = response.text
    
    # AIを毎回実行すると時間がかかるため、開発中は固定のダミーデータを使います
    dummy_json_output = """
    [
      {"name": "アサヒスーパードライ", "x": 15, "y": 15},
      {"name": "サッポロ エビス", "x": 30, "y": 25},
      {"name": "サントリー 角瓶", "x": 25, "y": 40},
      {"name": "山崎12年", "x": 85, "y": 60},
      {"name": "チョーヤ 梅酒", "x": 40, "y": 80},
      {"name": "カルロロッシ(赤)", "x": 10, "y": 45}
    ]
    """
    return dummy_json_output

def parse_ai_response(output_text):
    """AIの返答からJSONデータを抽出・解析する関数"""
    match = re.search(r"\[.*\]", output_text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            products = json.loads(json_text)
            return products
        except json.JSONDecodeError:
            st.error("AIの出力がJSON形式ではありませんでした。")
            return None
    else:
        st.error("AIの出力からJSONデータを見つけられませんでした。")
        return None

def plot_chart(products, theme, x_axis_name, y_axis_name):
    """データをもとにチャートを描画する関数"""
    fig, ax = plt.subplots(figsize=(12, 12))
    
    ax.set_xlim(-50, 50)
    ax.set_ylim(-50, 50)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel(x_axis_name, fontsize=14)
    ax.set_ylabel(y_axis_name, fontsize=14, rotation=0, ha='right', va='center')
    ax.set_title(f"「{theme}」の2軸マトリクス", fontsize=18, pad=20)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.xaxis.set_label_coords(0.5, -0.05)
    ax.yaxis.set_label_coords(-0.05, 0.5)

    for product in products:
        x, y, name = product['x'], product['y'], product['name']
        x_scaled = x - 50
        y_scaled = y - 50
        
        ax.plot(x_scaled, y_scaled, 'o', markersize=30, alpha=0.5, mec='black', mew=0.5, zorder=9)
        text_props = dict(boxstyle='round,pad=0.4', fc='whitesmoke', ec='darkgray', lw=0.5, alpha=0.9)
        ax.text(x_scaled, y_scaled - 6, name, ha='center', va='top', fontsize=9, bbox=text_props, zorder=10)

    return fig

# --- 3. メイン処理セクション ---
# ここからが、実際に画面に表示され、動く部分です

# 【変更後】タイトルとキャッチコピー
st.title("プロットる 🚀")
st.header("頭の中のイメージを、一瞬でチャートに。")
st.divider() # 見た目を整える区切り線

# UI（ユーザーインターフェース）
with st.sidebar:
    st.header("設定")

    # 【変更後】簡単な説明を追加
    st.info("『プロットる』は、あなたが気になるテーマ（例：ビール、お菓子、RPGのキャラクター）を、2つの評価軸（例：価格と味、攻撃力と素早さ）でマッピングするアプリです。AIに任せて、世の中のあらゆるものをプロットして、新しい発見を楽しみましょう！")
    
    theme = st.text_input("テーマ（例：お酒）", "お酒")
    x_axis_name = st.text_input("X軸の名前（例：価格帯）", "価格帯")
    x_axis_desc = st.text_input("X軸の説明（例：低価格〜高価格）", "")
    y_axis_name = st.text_input("Y軸の名前（例：味の傾向）", "味の傾向")
    y_axis_desc = st.text_input("Y軸の説明（例：甘口〜辛口）", "")
    
    generate_button = st.button("マトリクスを生成！")

# これ以降の if generate_button: の部分は変更なし
# ボタンが押されたら処理を実行
if generate_button:
    # 1. AIへの指示を作成
    prompt = create_prompt(theme, x_axis_name, x_axis_desc, y_axis_name, y_axis_desc)
    
    with st.spinner("AIが分析中です..."):
        # 2. AIを実行してデータを取得
        ai_output = get_data_from_ai(prompt)

        # 3. AIの返答を解析
        products_data = parse_ai_response(ai_output)

    # 4. 解析が成功したらグラフを描画
    if products_data:
        st.header(f"「{theme}」のマトリクス図")
        fig = plot_chart(products_data, theme, x_axis_name, y_axis_name)
        st.pyplot(fig)

        # --- ▼ ここから追加 ▼ ---

        # 1. グラフ(fig)を画像データ(PNG形式)に変換
        buf = BytesIO()
        fig.savefig(buf, format="png")
        image_data = buf.getvalue()

        # 2. ダウンロードボタンを設置
        st.download_button(
            label="チャートを画像として保存",
            data=image_data,
            file_name=f"{theme}_matrix.png", # ダウンロードするファイル名
            mime="image/png" # ファイルの種類
        )
        
        # --- ▲ ここまで追加 ▲ ---


        with st.expander("AIの元データ（JSON）を見る"):
            st.json(products_data)
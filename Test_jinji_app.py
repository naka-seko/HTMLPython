from flask import Flask, request, jsonify, render_template
import pandas as pd
import html
# import json  # json.dumps用に追加

# Flask アプリケーションを作成
app = Flask(__name__)

# 初期データ
jinji_data = {'名前': [], '年齢': [], '職業': [], 'メール': [], '携帯番号': []}
try:
    # ファイルを開いて、１行ずつリストを作成
    with open("jinji_data.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue
            j_name, j_nenrei, j_occupation, j_email, j_phone = line.split(",", 4)
            jinji_data['名前'].append(j_name.strip())
            jinji_data['年齢'].append(int(j_nenrei.strip()))
            jinji_data['職業'].append(j_occupation.strip())
            jinji_data['メール'].append(j_email.strip())
            jinji_data['携帯番号'].append(j_phone.strip())
except FileNotFoundError:
    # ファイル無し
    print("jinji_data.txt が見つかりません。空のリストで開始します。")
except Exception as e_code:
    # エラー時
    print(f"エラーが発生しました: {e_code}")

jinji_df = pd.DataFrame(jinji_data)
#print(jinji_df)

# トップページ
@app.route("/")
def index():
    return render_template("index.html")

# 抽出メイン処理
@app.route("/filter", methods=["POST"])
def filter_data():
    try:
        # 入力年齢以上を抽出
        nenrei = int(request.form.get("nenrei", 0))
        filtered = jinji_df[jinji_df['年齢'] >= nenrei]
        # フロントに送信するデータの構築（ツールチップ用にメールと携帯を付与）
        result_html = ""
        for _, row in filtered.iterrows():
            tooltip = html.escape(f"メール: {row['メール']} | 携帯: {row['携帯番号']}")
            result_html += f"<div class='person' data-tooltip='{tooltip}'>{row['名前']} ({row['年齢']}歳) - {row['職業']}</div><br>"
        return result_html if result_html else "該当データがありません。"

    except ValueError:
        # 数字以外なら再入力
        return jsonify({"error": "有効な年齢を入力してください。"})
    except Exception as e_code:
        # エラー時
        return app.response_class(
            response=f"エラーが発生しました: {e_code}",
            mimetype='text/plain',
            status=500
        )

if __name__ == "__main__":
    app.run(debug=True)

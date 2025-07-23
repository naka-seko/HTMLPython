# 定義
from flask import Flask, request, jsonify, render_template
import pandas as pd
import html
from datetime import datetime, date
# -*- coding: utf-8 -*-

# Flask アプリケーションを作成
app = Flask(__name__)

# 年齢を計算するための関数
def calculate_age(birthdate_str: str, fmt: str = '%Y/%m/%d') -> int:
    """
    例：'2001/07/23' → 24（※今日が2025/07/23の場合）
    """
    if not birthdate_str:
        return None
    # 日付文字列を datetime オブジェクトに変換
    birth = datetime.strptime(birthdate_str, fmt).date()
    today = date.today()

    # 誕生日がまだ来ていなければ −1
    if (today.month, today.day) < (birth.month, birth.day):
        return today.year - birth.year - 1
    # 誕生日が来ていればそのまま計算
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return age

# 人事データの読み込み
# jinji_data.txt ファイルから人事データを読み込み、DataFrameに変換
jinji_data = {'名前': [], '年齢': [], '職業': [], 'メール': [], '携帯番号': []}
try:
    # ファイルを開いて、１行ずつリストを作成
    with open("jinji_data.txt", "r", encoding="utf-8") as f:
        # １行ずつ読み込み、カンマで分割して辞書に追加
        for line in f:
            # 空行やカンマがない行はスキップ
            line = line.strip()
            if not line or "," not in line:
                continue
            # カンマで分割して各項目を取得
            j_name, j_birthdate, j_occupation, j_email, j_phone = line.split(",", 4)
            jinji_data['名前'].append(j_name.strip())
            # 年齢計算して追加
            if not j_birthdate.strip():
                jinji_data['年齢'].append(None) # 誕生日が空なら年齢も空
            else:
                jinji_data['年齢'].append(calculate_age(j_birthdate.strip()))

            jinji_data['職業'].append(j_occupation.strip())
            jinji_data['メール'].append(j_email.strip())
            jinji_data['携帯番号'].append(j_phone.strip())
except FileNotFoundError:
    # ファイル無し
    print("jinji_data.txt が見つかりません。空のリストで開始します。")
except Exception as e_code:
    # エラー時
    print(f"エラーが発生しました: {e_code}")

# DataFrameに変換
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
        if nenrei < 0:
            return jsonify({"error": "年齢は0以上の整数でなければなりません。"})
        # 年齢フィルター処理
        filtered = jinji_df[jinji_df['年齢'] >= nenrei]
        # フロントに送信するデータの構築（ツールチップ用にメールと携帯を付与）
        result_html = ""
        for _, row in filtered.iterrows():
            tooltip = html.escape(f"メール: {row['メール']} | 携帯: {row['携帯番号']}")
            result_html += f"<div class='person' data-tooltip='{tooltip}'>{row['名前']} ({row['年齢']}歳) - {row['職業']}</div><br>"
        return result_html if result_html else "該当データがありません。"
    except KeyError:
        # 年齢フィールドが存在しない場合
        return jsonify({"error": "年齢フィールドが見つかりません。"})
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
# エラーハンドリング
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404
@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

# アプリケーションの実行
if __name__ == "__main__":
    app.run(debug=True)

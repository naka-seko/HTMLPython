import pandas as pd

min_nenrei = 20 # 最小年齢
max_nenrei = 35 # 最大年齢
# 年齢を入力する関数
def input_nenrei():
  while True:
    try:
      # min_nenrei～max_nenreiの範囲で入力を促す
      # end_dispは表示用の文字列
      end_disp = f"(対象年齢（{min_nenrei}～{max_nenrei})以上は？)"
      in_nenrei = int(input(end_disp))
      if (in_nenrei < min_nenrei) or (in_nenrei > max_nenrei):
        continue
      else:
        return (in_nenrei)

    except ValueError:
      print("数字（整数）を入れて下さい。")

# テキストファイルから人事データを作成
jinji_data = {'名前': [], '年齢': [], '職業': []}
try:
  with open("jinji_data.txt", "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if not line or "," not in line:
        continue
      j_name, j_nenrei, j_occupation = line.split(",", 2)

      # データをjinji_dataに追加
      jinji_data['名前'].append(j_name.strip())
      jinji_data['年齢'].append(int(j_nenrei.strip()))
      jinji_data['職業'].append(j_occupation.strip())

except FileNotFoundError:
  print("jinji_data.txt が見つかりません。空のリストで開始します。")
except Exception as e_code:
  print(f"エラーが発生しました: {e_code}")

# DataFrameという形式に変換
jinji_df = pd.DataFrame(jinji_data)

# 年齢が、入力年齢以上の人を抽出
m_nenrei = input_nenrei()
older_than = jinji_df[jinji_df['年齢'] >= m_nenrei]

# 結果を表示
if older_than.empty:
  print("該当データなし")
else:
  print(older_than)

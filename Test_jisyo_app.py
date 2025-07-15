from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

# 初期値設定（ファイル名、辞書オブジェクト）
jisyo_text = "jisyo_fruit.txt"
english_words = {}

class MyHandler(BaseHTTPRequestHandler):
    # 辞書データの検索
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        # 辞書作成
        self.file_line_set()

        if parsed_path.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open("index.html", "r", encoding="utf-8") as file:
                    self.wfile.write(file.read().encode("utf-8"))
            except FileNotFoundError:
                self.wfile.write(b"Error: index.html Not Found")
            return  # 処理終了

        if parsed_path.path == "/search":
            word = query.get("word", [""])[0].strip().lower()

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()

            if word and word in english_words:
                response = {"meaning": english_words[word]}
            else:
                response = {"meaning": "見つかりません"}

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        else:
            print(f"404 Not Found: {parsed_path.path}")  # ログ出力
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    # ファイルの読み込んで、辞書作成
    def file_line_set(self):
        try:
            lines = self.file_read()
            for line in lines:
                line = line.strip()
                if not line or "," not in line:
                    continue
                english, japanese = line.split(",", 1)
                english_words[english.strip()] = japanese.strip()
        except FileNotFoundError:
            exit # 存在しない場合は何もしない

    # ファイルの読み込み
    def file_read(self):
        with open(jisyo_text, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return(lines)

    # ファイルの書き出し
    def file_write(self, t_mode):
        return open(jisyo_text, t_mode, encoding="utf-8")

    # ファイルの追加
    def File_add(self, word, meaning):
        try:
            # ファイルが存在する場合は内容をチェック
            lines = self.file_read()
            for line in lines:
                existing_word = line.split(",", 1)[0].strip().lower()
                if existing_word == word:
                    return  # 既に存在する場合は何もしない

            # 存在しなかった場合、追記
            files = self.file_write("a")
            files.write(f"{word},{meaning}\n")

        except FileNotFoundError:
            # ファイルが存在しない場合、新規作成して追加
            files = self.file_write("w")
            files.write(f"{word},{meaning}\n")

    # ファイルの更新
    def File_update(self,word,meaning):
        lines = self.file_read()
        files = self.file_write("w")
        for line in lines:
            if line.startswith(word + ","): # 対象英単語は更新
                files.write(f"{word},{meaning}\n")
            else:
                files.write(line)

    # ファイルの削除
    def File_delete(self,word):
        lines = self.file_read()
        files = self.file_write("w")
        for line in lines:
            if not line.startswith(word + ","): # 対象英単語は出力しない
                files.write(line)

    # 辞書の追加処理
    def do_POST_add(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        word = data.get("word", "").strip().lower()
        meaning = data.get("meaning", "").strip()

        if word in english_words and meaning:
            self.send_response(400)
            self.end_headers()
        else:
            english_words[word] = meaning
            # ファイルを追加
            self.File_add(word,meaning)
            self.send_response(200)
            self.end_headers()

    # 辞書の更新処理
    def do_POST_update(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        word = data.get("word", "").strip().lower()
        new_meaning = data.get("meaning", "").strip()

        if word in english_words and new_meaning:
            english_words[word] = new_meaning
            # ファイルを更新
            self.File_update(word,new_meaning)
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()

    # 辞書の削除処理
    def do_POST_delete(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        word = data.get("word", "").strip().lower()

        if word in english_words:
            del english_words[word]
            # ファイルを削除
            self.File_delete(word)
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()

    # 処理の振り分け
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        # 辞書作成
        self.file_line_set()

        if parsed_path.path == "/add":
            self.do_POST_add()

        elif parsed_path.path == "/update":
            self.do_POST_update()

        elif parsed_path.path == "/delete":
            self.do_POST_delete()

# サーバーの設定
server_address = ('', 8080)
httpd = HTTPServer(server_address, MyHandler)

print("HTTPサーバーが起動しました。 http://localhost:8080/index.html にアクセスしてね。")
httpd.serve_forever()

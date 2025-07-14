from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

# 辞書データを準備
english_words = {}
try:
    with open("jisyo_fruit.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue
            english, japanese = line.split(",", 1)
            english_words[english.strip()] = japanese.strip()
except FileNotFoundError:
    print("jisyo_fruit.txt が見つかりません。空の辞書で開始します。")

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        if parsed_path.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open("index.html", "r", encoding="utf-8") as file:
                    self.wfile.write(file.read().encode("utf-8"))
            except FileNotFoundError:
                self.wfile.write(b"Error: index.html Not Found")

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
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

#import os
#with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as file:#

# サーバーの設定
server_address = ('', 8080)
httpd = HTTPServer(server_address, MyHandler)

print("HTTPサーバーが起動しました！ http://localhost:8080/index.html にアクセスしてね。")
httpd.serve_forever()

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote_plus, parse_qs
from jinja2 import Environment, FileSystemLoader

storage_path = "storage/data.json"


class HTTPHandler(BaseHTTPRequestHandler):

    def send_html(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def do_GET(self):
        if self.path == "/":
            self.send_html("index.html")
        elif self.path == "/style.css":
            self.send_html("style.css")
        elif self.path == "/logo.png":
            self.send_html("logo.png")
        elif self.path == "/message.html":
            self.send_html("message.html")
        elif self.path == "/read":
            with open(storage_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                env = Environment(loader=FileSystemLoader("."))
                template = env.get_template("read.html")
                html = template.render(messages=data)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
        else:
            self.send_html("error.html", 404)

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = unquote_plus(post_data.decode("utf-8"))
            data_parse = parse_qs(data)
            username = data_parse["username"][0]
            message = data_parse["message"][0]

            try:
                with open(storage_path, "r", encoding="utf-8") as file:
                    messages = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                messages = {}

            messages[str(datetime.now())] = {
                "username": username,
                "message": message,
            }

            with open(storage_path, "w", encoding="utf-8") as file:
                json.dump(messages, file, ensure_ascii=False, indent=2)
                print(f"Message from {username}: {message}")
                self.send_response(303)
                self.send_header("Location", "/read")
                self.end_headers()

        else:
            self.send_html("error.html", 404)


server = HTTPServer(("", 3000), HTTPHandler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()

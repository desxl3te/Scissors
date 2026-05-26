import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
DIRECTORY = "/site"


class SiteHandler(SimpleHTTPRequestHandler):
    

    def send_error(self, code, message=None, explain=None):
        page = os.path.join(DIRECTORY, f"{code}.html")
        if os.path.isfile(page):
            try:
                with open(page, "rb") as fh:
                    body = fh.read()
            except OSError:
                body = None
            if body is not None:
                self.send_response(code, message)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    handler = partial(SiteHandler, directory=DIRECTORY)
    with ThreadingHTTPServer(("", PORT), handler) as httpd:
        print(f"Frontend: отдаём {DIRECTORY} на порту {PORT}")
        httpd.serve_forever()

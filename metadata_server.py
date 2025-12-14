from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
PORT = 80

FAKE_CREDS = b"""{
  "Code": "Success",
  "AccessKeyId": "FAKEACCESSKEY123",
  "SecretAccessKey": "FAKESECRETKEY456",
  "Token": "FAKETOKEN789"
}
"""

class MetadataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[META] {self.client_address} GET {self.path}")
        # Always return fake creds on any path (including "/")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(FAKE_CREDS)

    def log_message(self, fmt, *args):
        # Suppress default noisy logging
        return

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), MetadataHandler)
    print(f"[META] Fake metadata server on http://{HOST}:{PORT}/")
    server.serve_forever()
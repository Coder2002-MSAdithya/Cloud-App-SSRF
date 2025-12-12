from flask import Flask, request
from ssrf_lib import SSRFProtection
import requests

ssrf_protect = SSRFProtection(["169.254.169.254", "127.0.0.1"])
app = Flask(__name__)

@app.route('/resize')
def resize():
    url = request.args.get('url')
    if not url: return "No URL", 400
    
    if not ssrf_protect.is_safe(url):
        return "BLOCKED by SSRFProtection", 403
    
    try:
        print(f"[APP] FETCHING → {url}")
        resp = requests.get(url, timeout=5)
        return f"SUCCESS: {resp.content[:100].hex()}", 200
    except Exception as e:
        return f"Failed: {e}", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
from flask import Flask, request, Response, jsonify
from ssrf_lib import SSRFProtection
import requests
from io import BytesIO
from PIL import Image
import re
import time

app = Flask(__name__)
ssrf_protect = SSRFProtection(["169.254.169.254", "127.0.0.1"])


@app.route("/")
def index():
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Image Resizer / SSRF Demo</title>
      </head>
      <body>
        <h1>Image Resizer / SSRF Demo Service [Service 2]</h1>
        <p>
          This microservice fetches a URL provided by the client, inspects the response,
          and transforms it based on its type:
        </p>
        <ul>
          <li>JSON responses are returned as-is.</li>
          <li>HTML pages are summarized by their &lt;title&gt; tag.</li>
          <li>Images are processed and a negative is returned.</li>
          <li>Other content types are rejected as unknown.</li>
        </ul>
        <p>
          WARNING: This is intentionally configured with only IP-based SSRF protection
          for demonstration. It shows how DNS rebinding can bypass naive SSRF filters.
        </p>
        <p>Try: <code>/resize?url=http://example.com/</code></p>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")


def is_json_content(resp: requests.Response) -> bool:
    ctype = resp.headers.get("Content-Type", "").lower()
    return "application/json" in ctype or ctype.endswith("+json")


def is_html_content(resp: requests.Response) -> bool:
    ctype = resp.headers.get("Content-Type", "").lower()
    return "text/html" in ctype or "application/xhtml+xml" in ctype


def is_image_content(resp: requests.Response) -> bool:
    ctype = resp.headers.get("Content-Type", "").lower()
    return ctype.startswith("image/")


def extract_title(html_bytes: bytes) -> str | None:
    try:
        text = html_bytes.decode(errors="ignore")
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
        if m:
            # Collapse whitespace inside the title
            return " ".join(m.group(1).split()) + "\n"
        return None
    except Exception:
        return None


def negative_image(image_bytes: bytes) -> tuple[bytes, str]:
    """
    Compute a naive negative image:
      new_pixel = 255 - old_pixel (per channel)
    Returns (bytes, mime_subtype) where mime_subtype is e.g. 'jpeg', 'png'.
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    r, g, b, a = img.split()
    r = r.point(lambda v: 255 - v)
    g = g.point(lambda v: 255 - v)
    b = b.point(lambda v: 255 - v)
    neg = Image.merge("RGBA", (r, g, b, a))

    buf = BytesIO()
    # Default to PNG to preserve alpha; you could infer from original if desired.
    neg.save(buf, format="PNG")
    buf.seek(0)
    return buf.read(), "png"


@app.route("/resize")
def resize():
    url = request.args.get("url")
    if not url:
        return "[Service 2] No URL\n", 400

    # SSRF protection (IP-based)
    if not ssrf_protect.is_safe(url):
        return "[Service 2] BLOCKED by SSRFProtection\n", 403
    
    time.sleep(3)

    try:
        print(f"[Service 2] FETCHING → {url}")
        resp = requests.get(url, timeout=5, stream=True)
    except Exception as e:
        return f"[Service 2] Failed to fetch: {e}\n", 502

    # JSON → return as-is
    if is_json_content(resp):
        try:
            data = resp.json()
            return jsonify(data), 200
        except Exception:
            # Fallback: raw body if JSON parsing fails
            return Response(resp.content, mimetype=resp.headers.get("Content-Type", "application/json"))

    # HTML → extract <title>
    if is_html_content(resp):
        title = extract_title(resp.content)
        if title:
            return f"[Service 2] HTML title: {title}", 200
        return "[Service 2] HTML document has no detectable <title>\n", 200

    # Image → return negative
    if is_image_content(resp):
        try:
            neg_bytes, subtype = negative_image(resp.content)
            return Response(neg_bytes, mimetype=f"image/{subtype}")
        except Exception as e:
            return f"[Service 2] Failed to process image: {e}\n", 500

    # Unknown type
    return f"[Service 2] Unknown or unsupported Content-Type: {resp.headers.get('Content-Type')}\n", 400


if __name__ == "__main__":
    app.run(host="127.0.0.2", port=80, debug=False)
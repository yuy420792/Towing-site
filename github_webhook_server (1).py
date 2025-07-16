
from flask import Flask, request, jsonify
import base64
import requests
import os

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this in Render
REPO = "Towing-site"
OWNER = "yuy420792"
BRANCH = "main"
TARGET_PATH = "generated-site/index.html"

def get_file_sha():
    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{TARGET_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        return res.json().get("sha")
    return None

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    html_content = data.get("content")

    if not html_content:
        return jsonify({"error": "No HTML content provided"}), 400

    encoded = base64.b64encode(html_content.encode()).decode()
    sha = get_file_sha()

    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{TARGET_PATH}"
    payload = {
        "message": "Auto push from Render webhook",
        "content": encoded,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.put(api_url, headers=headers, json=payload)
    return jsonify({"status": res.status_code, "response": res.json()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

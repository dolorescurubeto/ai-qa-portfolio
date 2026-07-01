"""
Minimal banking chat UI for E2E Playwright tests.

Run:
  python chat_app.py
  Open http://127.0.0.1:5051
"""

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

REFERENCE = "Your checking account balance is $1,847.32."

RESPONSES = {
    "checking balance": "Your checking account balance is $1,847.32.",
    "checking wrong": "The balance in your checking account is $1,800.32.",
    "savings balance": "Your savings account balance is $5,200.00.",
    "transfer limit": "Your daily transfer limit on your checking account is $3,000.00.",
}

CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Demo Banking Chat</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; }
    #log { border: 1px solid #ccc; min-height: 120px; padding: 1rem; margin-bottom: 1rem; }
    .bot { color: #1a5276; margin: 0.5rem 0; }
    .user { color: #555; font-style: italic; }
    input { width: 70%; padding: 0.5rem; }
    button { padding: 0.5rem 1rem; }
  </style>
</head>
<body>
  <h1>Demo Banking Chat</h1>
  <p data-testid="hint">Ask about checking balance, savings, or transfer limit.</p>
  <div id="log" data-testid="chat-log"></div>
  <input id="query" data-testid="chat-input" placeholder="Type your question..." />
  <button id="send" data-testid="send-btn">Send</button>
  <script>
    const log = document.getElementById('log');
    const input = document.getElementById('query');
    document.getElementById('send').onclick = async () => {
      const q = input.value.trim();
      if (!q) return;
      log.innerHTML += '<div class="user">You: ' + q + '</div>';
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: q})
      });
      const data = await res.json();
      log.innerHTML += '<div class="bot" data-testid="bot-message">' + data.response + '</div>';
      input.value = '';
    };
  </script>
</body>
</html>
"""


def pick_response(query: str) -> str:
    q = query.lower()
    if "wrong" in q or "incorrect" in q:
        return RESPONSES["checking wrong"]
    if "savings" in q:
        return RESPONSES["savings balance"]
    if "transfer" in q or "limit" in q:
        return RESPONSES["transfer limit"]
    return RESPONSES["checking balance"]


@app.get("/")
def chat_page():
    return render_template_string(CHAT_HTML)


@app.post("/api/ask")
def ask():
    from flask import request

    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")
    return jsonify({"response": pick_response(query), "query": query})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5051, debug=False)

import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chatbot</title>
</head>
<body>
    <h2>Chatbot</h2>
    <input id="msg" placeholder="Mesajını yaz..." style="width:70%;padding:10px">
    <button onclick="send()">Gönder</button>
    <pre id="out"></pre>

<script>
async function send() {
    const message = document.getElementById("msg").value;
    const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message})
    });
    const data = await res.json();
    document.getElementById("out").textContent +=
        "\\nSen: " + message + "\\nBot: " + data.reply + "\\n";
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=message
    )

    return jsonify({"reply": response.text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

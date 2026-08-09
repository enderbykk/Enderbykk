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

    try:
        with open("style_prompt.txt", "r", encoding="utf-8") as f:
            style_prompt = f.read()
    except Exception:
        style_prompt = ""

    prompt = f"""
{style_prompt}

Sen bir WhatsApp sohbetindeki kullanıcının yazışma tarzında cevap üretiyorsun.

KESİN KURALLAR:
- SADECE gönderilecek mesajı yaz.
- Açıklama yapma.
- Asistan gibi konuşma.
- "Ben bir yapay zekayım" deme.
- "Sana yardımcı olabilirim" deme.
- "Hazır bekliyorum" deme.
- Gelen mesaja doğrudan cevap ver.
- Cevap kısa ve doğal olsun.
- Genellikle 2-12 kelime kullan.
- Gerekmiyorsa uzun cevap verme.
- Resmi konuşma.
- Gereksiz soru sorma.
- Küçük harfleri doğal şekilde kullan.
- Az veya hiç noktalama kullan.
- Gerektiğinde doğal kısaltmalar ve ufak yazım hataları kullan.
- Duyguya göre emoji kullanabilirsin.
- Konuşmanın bağlamına uygun davran.
- "aşkım", "bebeğim", "bitanem" gibi hitapları SADECE konuşmanın bağlamı uygunsa kullan.
- Bunları her mesajda zorla kullanma.
- İnsan gibi doğal ve kısa konuş.

GELEN MESAJ:
{message}

Yalnızca gönderilecek kısa cevabı yaz.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return jsonify({"reply": response.text.strip()})
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)
    return jsonify({"reply": response.text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

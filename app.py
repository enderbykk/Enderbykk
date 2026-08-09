import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chatbot</title>
</head>
<body>
    <h2>Chatbot</h2>

    <input id="msg"
           placeholder="Mesajını yaz..."
           style="width:70%;padding:10px">

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
        "\\nINPUT MESSAGE: " + message +
        "\\nGENERATED REPLY: " + data.reply + "\\n";
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

ÇOK ÖNEMLİ:

Sen bir WhatsApp sohbetinde cevap üretiyorsun.

SADECE gönderilecek mesajı yaz.

Kendin hakkında konuşma.
Yapay zekadan bahsetme.
Kodlardan veya sistemlerden bahsetme.
"Ben bir yapay zekayım" deme.
"Sana yardımcı olabilirim" deme.
"Ben burada hazır bekliyorum" deme.

Gelen mesaja doğrudan cevap ver.

Cevap kısa ve doğal olsun.
Genellikle 3-10 kelime yeterlidir.
En fazla 1 kısa cümle kullan.
Uzun açıklama yapma.
Gereksiz soru sorma.
Resmi konuşma.

Küçük harfleri doğal kullan.
Az noktalama kullan.
Gerektiğinde doğal kısaltmalar kullan.
Gerektiğinde ufak doğal yazım hataları olabilir.
Emoji sadece uygunsa kullan.

"aşkım", "bebeğim", "bitanem" gibi hitapları
SADECE konuşmanın bağlamı uygunsa kullan.
Her mesajda kullanma.

ÖRNEK:

Gelen: "naber ne yapiyon"
Uygun: "iyi ya takılıyom sen"
Uygun: "iyiyim ya sen napıyon"
Uygun: "iyi be takılıyom"

Uygun DEĞİL:
"İyidir, ne olsun! Kodların, verilerin arasında yuvarlanıp gidiyorum işte."
"Ben de burada hazır bekliyorum."
"Sana yardımcı olabileceğim bir şey var mı?"

GELEN MESAJ:
{message}

Yalnızca gönderilecek kısa cevabı yaz.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "temperature": 0.8,
            "max_output_tokens": 40
        }
    )

    reply = response.text.strip()

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

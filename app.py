from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "CE_HOD123"  # must match EXACTLY what you typed in Meta dashboard

@app.route("/webhook/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Invalid verification token", 403

    elif request.method == "POST":
        data = request.get_json()
        print("Incoming webhook:", data)
        return "Event received", 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)

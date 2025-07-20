from flask import Flask
import threading, time, requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!", 200

def run():
    app.run(host="0.0.0.0", port=8080)

def self_ping():
    while True:
        try:
            requests.get("https://YOUR-KOYEB-APP.koyeb.app/")
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(600)  # हर 10 मिनट में ping

def keep_alive():
    # Flask server start
    t = threading.Thread(target=run)
    t.start()
    # Self-ping start
    t2 = threading.Thread(target=self_ping)
    t2.st
  art()

from flask import Flask, jsonify, send_from_directory, request
import os
import sys
import threading

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.screener import scan_stocks
from src.sentiment import analyze_sentiment
from src.notifier import format_telegram_alert
from src.portfolio import calculate_portfolio_summary, add_holding, remove_holding
from src.ipo import get_active_ipos
from src.telegram_bot import start_telegram_bot_loop

app = Flask(__name__, static_folder="../static", static_url_path="", template_folder="../static")

# Start Telegram Bot Worker in background daemon thread for 100% free unified hosting
try:
    bot_thread = threading.Thread(target=start_telegram_bot_loop, daemon=True)
    bot_thread.start()
    print("🤖 Telegram Bot background thread started successfully!")
except Exception as e:
    print(f"Error launching Telegram Bot thread: {e}")

@app.route("/")
def index():
    return send_from_directory("../static", "index.html")

@app.route("/api/signals")
def get_signals():
    raw_signals = scan_stocks()
    enriched = []
    for sig in raw_signals:
        sent = analyze_sentiment(sig["symbol"])
        sig["sentiment"] = sent
        sig["formatted_alert"] = format_telegram_alert(sig, sent)
        enriched.append(sig)
    return jsonify({"status": "success", "count": len(enriched), "data": enriched})

@app.route("/api/ipo")
def get_ipo_api():
    ipos = get_active_ipos()
    return jsonify({"status": "success", "count": len(ipos), "data": ipos})

@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    summary = calculate_portfolio_summary()
    return jsonify({"status": "success", "data": summary})

@app.route("/api/portfolio/add", methods=["POST"])
def api_add_holding():
    payload = request.get_json() or {}
    sym = payload.get("symbol", "")
    qty = payload.get("quantity", 0)
    price = payload.get("buy_price", 0)
    
    if not sym or float(qty) <= 0 or float(price) <= 0:
        return jsonify({"status": "error", "message": "Invalid stock symbol, quantity or buy price."}), 400
        
    add_holding(sym, float(qty), float(price))
    updated = calculate_portfolio_summary()
    return jsonify({"status": "success", "data": updated})

@app.route("/api/portfolio/remove", methods=["POST"])
def api_remove_holding():
    payload = request.get_json() or {}
    sym = payload.get("symbol", "")
    if not sym:
        return jsonify({"status": "error", "message": "Symbol required"}), 400
        
    remove_holding(sym)
    updated = calculate_portfolio_summary()
    return jsonify({"status": "success", "data": updated})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

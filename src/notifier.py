import requests

def format_telegram_alert_html(signal: dict, sentiment: dict) -> str:
    """Formats technical signal and sentiment data into HTML-safe Telegram alert message."""
    sym = signal.get("symbol", "")
    price = signal.get("price", 0.0)
    sig_type = signal.get("signal_type", "NEUTRAL")
    action_badge = signal.get("action_badge", "🟡 HOLD")
    action_desc = signal.get("action_desc", "")
    conf = signal.get("confidence", 50)
    rsi = signal.get("rsi", 50)
    vol = signal.get("vol_ratio", 1.0)
    t1 = signal.get("target_1", 0.0)
    t2 = signal.get("target_2", 0.0)
    sl = signal.get("stop_loss", 0.0)
    
    sent_label = sentiment.get("label", "Neutral")
    
    emoji = "🟢" if "BUY" in action_badge else ("🔴" if "SELL" in action_badge or "WITHDRAW" in action_badge else "🟡")
    
    msg = f"""
{emoji} <b>NSE ACTION SIGNAL ALERT</b> {emoji}

📌 <b>Stock:</b> {sym}
💰 <b>ACTION DECISION:</b> {action_badge}
💵 <b>Current Price:</b> ₹{price}
📊 <b>Technical Signal:</b> {sig_type} (Confidence: {conf}%)
💡 <b>AI Insight:</b> {action_desc}
📈 <b>RSI (14):</b> {rsi} | <b>Volume Ratio:</b> {vol}x
📰 <b>News Sentiment:</b> {sent_label}

🎯 <b>Target 1:</b> ₹{t1}
🎯 <b>Target 2:</b> ₹{t2}
🛑 <b>Stop Loss:</b> ₹{sl} (Strict)
"""
    return msg.strip()

def format_telegram_alert(signal: dict, sentiment: dict) -> str:
    """Formats technical signal and sentiment data into a Telegram alert message."""
    return format_telegram_alert_html(signal, sentiment)

def send_telegram_notification(bot_token: str, chat_id: str, message: str) -> bool:
    """Optional helper to dispatch formatted alert message to actual Telegram Bot Chat."""
    if not bot_token or not chat_id:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        print(f"Telegram dispatch failed: {e}")
        return False

import os
import time
import requests
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.screener import scan_stocks
from src.sentiment import analyze_sentiment
from src.notifier import format_telegram_alert, format_telegram_alert_html
from src.portfolio import calculate_portfolio_summary, add_holding, remove_holding
from src.ipo import get_active_ipos

DEFAULT_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8993271292:AAFqmVh6MdUHMpyvOULWnAWP27qedY6L6PM")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8530348020")

def process_telegram_command(text: str, filepath: str = None) -> list:
    """Processes incoming mobile Telegram text command and returns list of HTML message strings to send."""
    parts = text.strip().split()
    if not parts:
        return ["Unknown command. Type /help to see available mobile commands."]
        
    cmd = parts[0].lower()
    
    if cmd in ["/start", "/help"]:
        return ["""
🤖 <b>INDIAN STOCK & IPO HIGH-PROFIT AI BOT</b> 🤖

📲 <b>Available Commands:</b>
• <code>/scan</code> - Scan NSE market for High-Profit BUY/SELL stock signals
• <code>/ipo</code> - Scan upcoming Indian IPOs for High Listing Gain opportunities (+30% to +80%)
• <code>/portfolio</code> - View live portfolio summary, value & profit/loss
• <code>/buy &lt;symbol&gt; &lt;qty&gt; &lt;price&gt;</code> - Record stock buy position
• <code>/sell &lt;symbol&gt;</code> - Close stock position
"""]

    elif cmd == "/ipo":
        ipos = get_active_ipos()
        if not ipos:
            return ["🔥 No active IPOs found right now."]
            
        messages = ["🚀 <b>HIGH LISTING GAIN IPO SCANNER RESULTS</b> 🚀\n"]
        for ipo in ipos:
            msg = f"""
📌 <b>IPO Name:</b> {ipo['name']} ({ipo['type']})
💰 <b>Issue Price:</b> ₹{ipo['issue_price']} | <b>GMP:</b> +₹{ipo['gmp_price']} (+{ipo['gmp_pct']}%)
🎯 <b>Est. Listing Price:</b> ₹{ipo['est_listing_price']}
📊 <b>Subscription Demand:</b> {ipo['subscription_x']}x Oversubscribed
💵 <b>Est. Profit per Lot:</b> ~₹{ipo['est_profit_per_lot']:,.2f}

<b>DECISION:</b> {ipo['badge']}
💡 {ipo['desc']}
"""
            messages.append(msg.strip())
        return messages

    elif cmd == "/portfolio":
        summary = calculate_portfolio_summary(filepath=filepath) if filepath else calculate_portfolio_summary()
        invested = summary["total_invested"]
        cur_val = summary["current_value"]
        pnl = summary["total_pnl"]
        pnl_pct = summary["pnl_pct"]
        holdings = summary["holdings"]
        
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        
        msg = f"""
💼 <b>YOUR LIVE PORTFOLIO SUMMARY</b> 💼

💰 <b>Total Invested:</b> ₹{invested:,.2f}
📈 <b>Current Value:</b> ₹{cur_val:,.2f}
{pnl_emoji} <b>Total P&L:</b> ₹{pnl:,.2f} ({pnl_pct:+.2f}%)

📌 <b>Active Holdings ({len(holdings)}):</b>
"""
        for h in holdings:
            h_emoji = "🟢" if h['pnl'] >= 0 else "🔴"
            msg += f"• <b>{h['symbol']}</b>: {h['quantity']} qty @ ₹{h['buy_price']} | Live: ₹{h['current_price']} ({h_emoji} ₹{h['pnl']:+.2f})\n"
            
        return [msg.strip()]

    elif cmd == "/scan":
        signals = scan_stocks()
        if not signals:
            return ["🔍 Market Scan complete. No active signals found at the moment."]
            
        messages = [f"⚡ <b>LIVE NSE MARKET SCAN RESULTS ({len(signals)} Stocks Scanned)</b> ⚡"]
        for sig in signals[:5]: # Top 5 stocks
            sent = analyze_sentiment(sig["symbol"])
            messages.append(format_telegram_alert_html(sig, sent))
        return messages

    elif cmd == "/buy":
        if len(parts) < 4:
            return ["⚠️ Usage: <code>/buy &lt;symbol&gt; &lt;quantity&gt; &lt;price&gt;</code> (Example: <code>/buy RELIANCE 10 1250</code>)"]
        sym = parts[1]
        try:
            qty = float(parts[2])
            price = float(parts[3])
            entry = add_holding(sym, qty, price, filepath=filepath) if filepath else add_holding(sym, qty, price)
            return [f"✅ <b>ADDED TO PORTFOLIO:</b> {entry['quantity']} shares of <b>{entry['symbol']}</b> @ ₹{entry['buy_price']:.2f}"]
        except ValueError:
            return ["⚠️ Invalid quantity or price format."]

    elif cmd == "/sell":
        if len(parts) < 2:
            return ["⚠️ Usage: <code>/sell &lt;symbol&gt;</code> (Example: <code>/sell RELIANCE</code>)"]
        sym = parts[1]
        success = remove_holding(sym, filepath=filepath) if filepath else remove_holding(sym)
        if success:
            return [f"✅ <b>CLOSED POSITION:</b> Removed <b>{sym}</b> from your portfolio."]
        else:
            return [f"⚠️ Stock <b>{sym}</b> not found in your portfolio holdings."]

    else:
        return ["Unknown command. Type /help to see available commands."]

def start_telegram_bot_loop(token: str = DEFAULT_BOT_TOKEN, chat_id: str = DEFAULT_CHAT_ID):
    """Background polling worker listening for mobile commands from Telegram API."""
    if not token:
        print("Telegram bot token not provided. Bot worker idle.")
        return
        
    target_chat_id = str(chat_id).strip() if chat_id else ""
    url = f"https://api.telegram.org/bot{token.strip()}"
    last_update_id = 0
    print(f"🤖 Starting Telegram Mobile Bot Worker (Target Chat ID: {target_chat_id})...")
    
    while True:
        try:
            get_updates_url = f"{url}/getUpdates?offset={last_update_id + 1}&timeout=10"
            resp = requests.get(get_updates_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for update in data.get("result", []):
                    last_update_id = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "")
                    sender_chat_id = str(message.get("chat", {}).get("id", ""))
                    
                    if text:
                        print(f"Received Telegram command: '{text}' from Chat ID: {sender_chat_id}")
                        replies = process_telegram_command(text)
                        for reply in replies:
                            send_url = f"{url}/sendMessage"
                            send_resp = requests.post(send_url, json={
                                "chat_id": sender_chat_id,
                                "text": reply,
                                "parse_mode": "HTML"
                            }, timeout=10)
                            print(f"Sent reply status: {send_resp.status_code}")
                            time.sleep(0.5) # Short delay between messages
        except Exception as e:
            print(f"Telegram polling error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    start_telegram_bot_loop()

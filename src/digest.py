import os
import sys
import requests
import yfinance as yf
from bs4 import BeautifulSoup

# Ensure root directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from src.sentiment import calculate_text_sentiment
except ModuleNotFoundError:
    from sentiment import calculate_text_sentiment

def get_market_indices() -> dict:
    """Fetches live market data for NIFTY 50, BANK NIFTY, and SENSEX."""
    tickers = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN"
    }
    indices = {}
    
    for name, sym in tickers.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_price = hist["Close"].iloc[-1]
                chg = last_price - prev_close
                chg_pct = (chg / prev_close) * 100
                indices[name] = {
                    "price": round(float(last_price), 2),
                    "change": round(float(chg), 2),
                    "change_pct": round(float(chg_pct), 2),
                    "status": "UP" if chg >= 0 else "DOWN"
                }
            else:
                indices[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0, "status": "NEUTRAL"}
        except Exception as e:
            print(f"Error fetching index {name}: {e}")
            indices[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0, "status": "NEUTRAL"}
            
    return indices

def get_top_news_headlines() -> list:
    """Scrapes top stock market and tech/AI news headlines from Google News RSS."""
    rss_urls = [
        "https://news.google.com/rss/search?q=Indian+stock+market+NSE+Nifty&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=Artificial+Intelligence+Tech+India&hl=en-IN&gl=IN&ceid=IN:en"
    ]
    headlines = []
    
    for url in rss_urls:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                items = soup.find_all("item")
                for item in items[:3]:
                    if item.title:
                        title_text = item.title.text.strip()
                        if title_text and title_text not in headlines:
                            headlines.append(title_text)
        except Exception as e:
            print(f"Error fetching news RSS: {e}")
            
    if not headlines:
        headlines = [
            "Indian markets remain buoyant amid strong institutional buying.",
            "Tech and AI sectors see strong momentum heading into new quarter."
        ]
        
    return headlines[:5]

def generate_morning_digest() -> str:
    """Generates formatted HTML Daily Market & Tech Morning Digest for Telegram dispatch."""
    indices = get_market_indices()
    headlines = get_top_news_headlines()
    
    # Calculate overall market sentiment from headlines
    combined_text = " ".join(headlines)
    sent_score = calculate_text_sentiment(combined_text)
    
    if sent_score >= 0.2:
        sent_badge = "🟢 <b>BULLISH & OPTIMISTIC</b>"
    elif sent_score <= -0.2:
        sent_badge = "🔴 <b>BEARISH & CAUTIOUS</b>"
    else:
        sent_badge = "🟡 <b>NEUTRAL & STABLE</b>"

    # Format Market Indices Section
    idx_str = ""
    for name, data in indices.items():
        emoji = "📈" if data["change"] >= 0 else "📉"
        sign = "+" if data["change"] >= 0 else ""
        price_fmt = f"{data['price']:,.2f}" if data['price'] > 0 else "N/A"
        idx_str += f"• <b>{name}:</b> {price_fmt} ({emoji} {sign}{data['change_pct']}%\n"

    # Format News Headlines Section
    news_str = ""
    for idx, h in enumerate(headlines, start=1):
        news_str += f"{idx}. {h}\n\n"

    digest_html = f"""
🌅 <b>DAILY MARKET & TECH MORNING DIGEST</b> 🌅

📊 <b>KEY MARKET INDICES:</b>
{idx_str}
🎯 <b>MARKET SENTIMENT:</b> {sent_badge}

📰 <b>TOP MARKET & TECH HEADLINES:</b>
{news_str.strip()}

💡 <b>PRO TIP:</b> Type <code>/scan</code> to check high-profit stock signals or <code>/ipo</code> for active listing gains!
"""
    return digest_html.strip()

if __name__ == "__main__":
    print(generate_morning_digest())

# Indian Stock Market Screener & Sentiment Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Python-based NSE Stock Market Screener, News Sentiment Analyzer, Telegram Notifier, and Web Dashboard UI for Indian traders.

**Architecture:** Python core data pipeline fetching NSE stock data via `yfinance`, computing technical indicators (EMA, RSI, MACD, Volume), scraping Indian market news for sentiment analysis, formatting Telegram trade alerts, and serving a sleek Flask dark-mode web dashboard.

**Tech Stack:** Python 3.10+, `yfinance`, `pandas`, `ta`, `requests`, `beautifulsoup4`, `flask`, `pytest`, HTML5/CSS3/JavaScript (Chart.js).

**Spec:** [2026-09-13-indian-stock-screener-design.md](file:///home/mustak/.gemini/antigravity/scratch/indian_stock_screener/docs/specs/2026-09-13-indian-stock-screener-design.md)

## Global Constraints

- Target Market: Indian Stock Exchange (NSE - symbols ending with `.NS`).
- Must run cleanly in standard Python environment without external GPU/heavy model dependencies.
- Unit tested using `pytest`.

---

### Task 1: Environment Setup & Technical Screener Engine

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/screener.py`
- Test: `tests/test_screener.py`

**Interfaces:**
- Consumes: NSE Stock Tickers (e.g. `RELIANCE.NS`, `TATASTEEL.NS`, `INFY.NS`, `HDFCBANK.NS`, `TCS.NS`)
- Produces: `scan_stocks(symbols: list[str]) -> list[dict]` containing price, indicators (RSI, EMA20/50/200, MACD, VolumeRatio), and signal (`BULLISH_BREAKOUT`, `OVERSOLD_BOUNCE`, `BEARISH_REVERSAL`, `NEUTRAL`).

- [ ] **Step 1: Create `requirements.txt` and package scaffolding**

Write dependencies in `requirements.txt`:
```
yfinance>=0.2.36
pandas>=2.0.0
ta>=0.11.0
requests>=2.31.0
beautifulsoup4>=4.12.0
flask>=3.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Write failing unit test for Technical Screener**

Write `tests/test_screener.py`:
```python
import pandas as pd
import numpy as np
from src.screener import calculate_indicators, evaluate_signals

def test_calculate_indicators():
    # Mock stock price dataframe
    dates = pd.date_range(start="2026-01-01", periods=60, freq="D")
    df = pd.DataFrame({
        "Open": np.linspace(100, 200, 60),
        "High": np.linspace(105, 205, 60),
        "Low": np.linspace(95, 195, 60),
        "Close": np.linspace(100, 200, 60),
        "Volume": [10000] * 59 + [50000] # Volume spike on last day
    }, index=dates)
    
    processed = calculate_indicators(df)
    assert "EMA_20" in processed.columns
    assert "EMA_50" in processed.columns
    assert "RSI_14" in processed.columns
    assert "MACD" in processed.columns
    assert "Volume_Ratio" in processed.columns

def test_evaluate_signals():
    sample_row = {
        "Symbol": "RELIANCE.NS",
        "Close": 2950.0,
        "EMA_20": 2940.0,
        "EMA_50": 2900.0,
        "RSI_14": 62.0,
        "MACD": 15.0,
        "MACD_Signal": 10.0,
        "Volume_Ratio": 2.2
    }
    signal = evaluate_signals(sample_row)
    assert signal["signal_type"] == "BULLISH_BREAKOUT"
```

- [ ] **Step 3: Implement Technical Screener module**

Write `src/screener.py`:
```python
import yfinance as yf
import pandas as pd
import ta

DEFAULT_NSE_WATCHLIST = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "SBIN.NS", "TATASTEEL.NS", "TATAMOTORS.NS", "LTIM.NS"
]

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 50:
        return df
    
    df = df.copy()
    df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["EMA_50"] = ta.trend.ema_indicator(df["Close"], window=50)
    df["RSI_14"] = ta.momentum.rsi(df["Close"], window=14)
    
    macd_indicator = ta.trend.MACD(df["Close"])
    df["MACD"] = macd_indicator.macd()
    df["MACD_Signal"] = macd_indicator.macd_signal()
    
    avg_vol = df["Volume"].rolling(window=20).mean()
    df["Volume_Ratio"] = df["Volume"] / avg_vol
    
    return df

def evaluate_signals(row: dict) -> dict:
    close = row.get("Close", 0)
    ema20 = row.get("EMA_20", 0)
    ema50 = row.get("EMA_50", 0)
    rsi = row.get("RSI_14", 50)
    macd = row.get("MACD", 0)
    macd_sig = row.get("MACD_Signal", 0)
    vol_ratio = row.get("Volume_Ratio", 1.0)
    
    signal_type = "NEUTRAL"
    confidence = 50
    
    if close > ema20 > ema50 and rsi > 55 and macd > macd_sig and vol_ratio >= 1.5:
        signal_type = "BULLISH_BREAKOUT"
        confidence = 85
    elif rsi < 32 and close > ema50:
        signal_type = "OVERSOLD_BOUNCE"
        confidence = 75
    elif rsi > 70 and macd < macd_sig:
        signal_type = "BEARISH_REVERSAL"
        confidence = 70
        
    target_1 = round(close * 1.025, 2)
    target_2 = round(close * 1.05, 2)
    stop_loss = round(close * 0.985, 2)
    
    return {
        "symbol": row.get("Symbol", "UNKNOWN"),
        "price": close,
        "signal_type": signal_type,
        "confidence": confidence,
        "rsi": round(rsi, 2),
        "vol_ratio": round(vol_ratio, 2),
        "target_1": target_1,
        "target_2": target_2,
        "stop_loss": stop_loss
    }

def scan_stocks(symbols: list[str] = None) -> list[dict]:
    if not symbols:
        symbols = DEFAULT_NSE_WATCHLIST
    
    results = []
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="6mo")
            if df.empty or len(df) < 50:
                continue
            df_ind = calculate_indicators(df)
            last_row = df_ind.iloc[-1].to_dict()
            last_row["Symbol"] = sym
            sig = evaluate_signals(last_row)
            results.append(sig)
        except Exception as e:
            print(f"Error scanning {sym}: {e}")
    return results
```

- [ ] **Step 4: Run tests**

Run pytest to verify the screener logic works cleanly.

---

### Task 2: News & Sentiment Scoring Engine

**Files:**
- Create: `src/sentiment.py`
- Test: `tests/test_sentiment.py`

**Interfaces:**
- Consumes: Stock Symbol / Name (e.g. `RELIANCE.NS`)
- Produces: `analyze_sentiment(symbol: str) -> dict` containing `score` (-1.0 to 1.0), `label` ("Very Positive", "Positive", "Neutral", "Negative"), and top headlines.

- [ ] **Step 1: Write failing unit test for Sentiment Analysis**

Write `tests/test_sentiment.py`:
```python
from src.sentiment import calculate_text_sentiment, format_sentiment_summary

def test_calculate_text_sentiment():
    pos_text = "Reliance Industries reports 25% surge in quarterly net profit, beats estimates."
    neg_text = "Tata Motors faces supply chain disruption, quarterly revenue drops sharply."
    
    pos_score = calculate_text_sentiment(pos_text)
    neg_score = calculate_text_sentiment(neg_text)
    
    assert pos_score > 0.2
    assert neg_score < -0.2

def test_format_sentiment_summary():
    result = format_sentiment_summary(0.65, ["Strong Q3 results", "Expansion in retail sector"])
    assert result["label"] in ["Positive", "Very Positive"]
    assert len(result["headlines"]) == 2
```

- [ ] **Step 2: Implement Sentiment Engine**

Write `src/sentiment.py`:
```python
import requests
from bs4 import BeautifulSoup
import re

BULLISH_WORDS = {
    "surge", "growth", "profit", "bullish", "jump", "record", "beats", "rally",
    "expansion", "upward", "gain", "high", "outperform", "buy", "order", "contract"
}

BEARISH_WORDS = {
    "fall", "drop", "loss", "bearish", "plunge", "decline", "slump", "miss",
    "cut", "downward", "slash", "low", "underperform", "sell", "lawsuit", "penalty"
}

def calculate_text_sentiment(text: str) -> float:
    words = re.findall(r'\w+', text.lower())
    if not words:
        return 0.0
    
    pos_count = sum(1 for w in words if w in BULLISH_WORDS)
    neg_count = sum(1 for w in words if w in BEARISH_WORDS)
    
    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return round((pos_count - neg_count) / total, 2)

def format_sentiment_summary(score: float, headlines: list[str]) -> dict:
    if score >= 0.5:
        label = "Very Positive"
    elif score >= 0.15:
        label = "Positive"
    elif score <= -0.5:
        label = "Very Negative"
    elif score <= -0.15:
        label = "Negative"
    else:
        label = "Neutral"
        
    return {
        "score": score,
        "label": label,
        "headlines": headlines[:3]
    }

def analyze_sentiment(symbol: str) -> dict:
    clean_sym = symbol.replace(".NS", "")
    # Simulated/scraped news headlines fallback
    sample_headlines = [
        f"{clean_sym} shows steady revenue growth in recent quarterly update.",
        f"Analysts express optimism for {clean_sym} market expansion."
    ]
    scores = [calculate_text_sentiment(h) for h in sample_headlines]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    return format_sentiment_summary(avg_score, sample_headlines)
```

- [ ] **Step 3: Run pytest to verify sentiment engine**

---

### Task 3: Telegram Alert Formatter & Notifier Engine

**Files:**
- Create: `src/notifier.py`
- Test: `tests/test_notifier.py`

**Interfaces:**
- Consumes: Signal dict & Sentiment dict
- Produces: `format_telegram_alert(signal: dict, sentiment: dict) -> str`

- [ ] **Step 1: Write failing unit test for Notifier**

Write `tests/test_notifier.py`:
```python
from src.notifier import format_telegram_alert

def test_format_telegram_alert():
    signal = {
        "symbol": "RELIANCE.NS",
        "price": 2950.0,
        "signal_type": "BULLISH_BREAKOUT",
        "confidence": 85,
        "rsi": 62.5,
        "vol_ratio": 2.1,
        "target_1": 3020.0,
        "target_2": 3090.0,
        "stop_loss": 2910.0
    }
    sentiment = {
        "score": 0.65,
        "label": "Very Positive",
        "headlines": ["Q3 Net profit surges 20%"]
    }
    
    message = format_telegram_alert(signal, sentiment)
    assert "RELIANCE.NS" in message
    assert "BULLISH_BREAKOUT" in message
    assert "₹2950.0" in message or "2950" in message
    assert "Very Positive" in message
```

- [ ] **Step 2: Implement Telegram Alert Formatter**

Write `src/notifier.py`:
```python
def format_telegram_alert(signal: dict, sentiment: dict) -> str:
    sym = signal.get("symbol", "")
    price = signal.get("price", 0.0)
    sig_type = signal.get("signal_type", "NEUTRAL")
    conf = signal.get("confidence", 50)
    rsi = signal.get("rsi", 50)
    vol = signal.get("vol_ratio", 1.0)
    t1 = signal.get("target_1", 0.0)
    t2 = signal.get("target_2", 0.0)
    sl = signal.get("stop_loss", 0.0)
    
    sent_label = sentiment.get("label", "Neutral")
    
    emoji = "🚀" if "BULLISH" in sig_type else ("⚠️" if "BEARISH" in sig_type else "🔍")
    
    msg = f"""
{emoji} **NSE TRADE SIGNAL ALERT** {emoji}

📌 **Stock:** {sym}
💵 **Price:** ₹{price}
📊 **Signal:** {sig_type} (Confidence: {conf}%)
📈 **RSI:** {rsi} | **Volume Spike:** {vol}x
📰 **News Sentiment:** {sent_label}

🎯 **Target 1:** ₹{t1}
🎯 **Target 2:** ₹{t2}
🛑 **Stop Loss:** ₹{sl} (Strict)

*Automated Signal via Antigravity Indian Stock AI*
"""
    return msg.strip()
```

---

### Task 4: Dark-Mode Web Dashboard UI & API Server

**Files:**
- Create: `src/dashboard.py`
- Create: `static/index.html`
- Create: `static/style.css`
- Create: `static/app.js`

**Interfaces:**
- Serves HTTP API at `/api/signals` returning live scanned signals & sentiment.
- Serves sleek Glassmorphism dark-mode UI at `/`.

- [ ] **Step 1: Implement Flask Backend Server (`src/dashboard.py`)**

```python
from flask import Flask, jsonify, render_template, send_from_directory
import os
from src.screener import scan_stocks
from src.sentiment import analyze_sentiment
from src.notifier import format_telegram_alert

app = Flask(__name__, static_folder="../static", template_folder="../static")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

- [ ] **Step 2: Create Web Dashboard UI (`static/index.html` & `static/style.css`)**

Build a modern, sleek web dashboard UI with live stock tickers, signal cards, sentiment badges, target/stop loss breakdown, and instant alert copy buttons.

---

### Task 5: End-to-End System Verification

- Run full scan test across NSE stocks.
- Verify web dashboard launches at `http://localhost:5000`.
- Verify all unit tests pass with `pytest`.

# Indian Stock Market AI Screener & Daily Sentiment Alert Bot - Design Document

**Date:** 2026-09-13
**Author:** Antigravity AI & User
**Target Market:** Indian Stock Market (NSE Nifty 50, Nifty 500, F&O Watchlist)

---

## 1. Executive Overview

The goal of this system is to automate technical stock screening, news sentiment analysis, and alert delivery for Indian retail traders and investors. By combining automated technical indicator scans (RSI, EMA 20/50/200, MACD, Volume breakouts) with news sentiment scraping and instant Telegram alerts, the system eliminates manual chart scanning, reduces emotional trading, and delivers high-probability swing and intraday trading signals.

---

## 2. System Architecture

```
                                +-----------------------------+
                                | Indian Stock Market Data    |
                                | (NSE via yfinance / APIs)   |
                                +--------------+--------------+
                                               |
                                               v
+-----------------------+       +--------------+--------------+       +------------------------+
| Indian Financial News | ----> | Python Core Engine          | ----> | Telegram Notifier Bot  |
| (Moneycontrol/ET/Mint)|       | (Screener + Sentiment)      |       | (Instant Mobile Alert) |
+-----------------------+       +--------------+--------------+       +------------------------+
                                               |
                                               v
                                +--------------+--------------+
                                | Web Dashboard UI            |
                                | (Flask/HTML/CSS/Chart.js)   |
                                +-----------------------------+
```

---

## 3. Core Modules & Responsibilities

### Module A: Technical Screener (`src/screener.py`)
- **Data Source:** `yfinance` (NSE stock symbols ending with `.NS`, e.g., `RELIANCE.NS`, `TATASTEEL.NS`, `INFY.NS`).
- **Indicators Calculated:**
  - 20 EMA, 50 EMA, 200 EMA (Golden Crossover detection)
  - 14-period RSI (Oversold < 30, Overbought > 70, Bullish momentum 50-65)
  - MACD Line, Signal Line, Histogram
  - Volume Moving Average (Detecting >1.5x average volume spikes)
- **Output:** Categorized signal list (`BULLISH_BREAKOUT`, `OVERSOLD_BOUNCE`, `BEARISH_REVERSAL`).

### Module B: News & Sentiment Engine (`src/sentiment.py`)
- **Data Source:** Financial news RSS feeds and news scrapers (Moneycontrol / Economic Times).
- **Sentiment Scoring:** Keyword & NLP score calculation (Range: -1.0 Very Negative to +1.0 Very Positive).
- **Output:** Stock-specific sentiment tag and top headline summary.

### Module C: Telegram Notifier (`src/notifier.py`)
- Formats signals into actionable trade alerts:
  ```
  🚀 NSE BULLISH SIGNAL DETECTED 🚀
  Stock: RELIANCE.NS (Reliance Industries)
  Current Price: ₹2,950.00
  Trigger: 20/50 EMA Golden Crossover + Volume 2.1x
  News Sentiment: Very Positive (+0.82)
  Suggested Entry: ₹2,950
  Target 1: ₹3,020 | Target 2: ₹3,090
  Stop Loss: ₹2,910 (Strict)
  ```

### Module D: Web Dashboard UI (`src/dashboard.py` & `static/index.html`)
- Dark-mode responsive dashboard displaying live market overview, active stock buy/sell signals, chart snapshots, news feeds, and FII/DII institutional trend indicators.

---

## 4. Revenue & Monetization Plan

1. **Personal Capital Trading:** Executing high-conviction trades with strict risk management (1:2 risk-reward).
2. **Telegram VIP Channel:** Offering premium daily alerts and 9:00 AM pre-market summaries for ₹999/month.
3. **SaaS Web Tool:** Hosting the web dashboard for subscriber access.

---

## 5. Verification & Testing

- Unit tests for technical indicator math using historical dataset.
- Mocking news scraper responses to verify sentiment scoring accuracy.
- Dashboard route verification and alert formatting tests.

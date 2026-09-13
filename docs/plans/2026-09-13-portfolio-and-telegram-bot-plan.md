# Personal Portfolio & Interactive Telegram Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a personal stock portfolio manager with live P&L tracking, web UI controls, and a 2-way mobile Telegram Bot that allows full remote control from phone.

**Architecture:** 
- `src/portfolio.py` manages persistent holdings (`data/portfolio.json`), calculating live values & P&L via `yfinance`.
- `src/telegram_bot.py` uses long-polling HTTP worker listening for commands (`/portfolio`, `/scan`, `/buy`, `/sell`) via Telegram Bot API (`Token: 8993271292`, `Chat ID: 8530348020`).
- `src/dashboard.py` exposes `/api/portfolio` endpoints.
- `static/index.html` renders a dedicated Portfolio P&L dashboard & trade entry modal.

**Tech Stack:** Python 3.12, Flask, yfinance, requests, HTML5/CSS3, JavaScript.

---

### Task 1: Portfolio Data & Engine Module (`src/portfolio.py`)

**Files:**
- Create: `data/portfolio.json`
- Create: `src/portfolio.py`
- Test: `tests/test_portfolio.py`

**Interfaces:**
- `get_portfolio_summary() -> dict` (returns total_invested, current_value, total_pnl, pnl_pct, holdings_list)
- `add_holding(symbol: str, qty: float, buy_price: float) -> dict`
- `remove_holding(symbol: str) -> bool`

- [ ] **Step 1: Write unit test for portfolio manager**
- [ ] **Step 2: Implement `src/portfolio.py`**
- [ ] **Step 3: Run pytest to verify portfolio math**

---

### Task 2: Interactive 2-Way Mobile Telegram Bot (`src/telegram_bot.py`)

**Files:**
- Create: `src/telegram_bot.py`
- Test: `tests/test_telegram_bot.py`

**Commands Handled:**
- `/start` or `/help` -> Show command list
- `/portfolio` -> Send live portfolio summary & profit/loss
- `/scan` -> Run technical & news screener and send top BUY/SELL picks
- `/buy <symbol> <qty> <price>` -> Add position to portfolio from phone
- `/sell <symbol>` -> Close position from phone

- [ ] **Step 1: Write unit test for command parser**
- [ ] **Step 2: Implement Telegram bot listener loop in `src/telegram_bot.py`**
- [ ] **Step 3: Run tests**

---

### Task 3: Portfolio Web Dashboard API & UI Integration

**Files:**
- Modify: `src/dashboard.py`
- Modify: `static/index.html`
- Modify: `static/style.css`
- Modify: `static/app.js`

**Features:**
- Add Portfolio Overview KPI card (Total Invested, Current Value, P&L)
- Add "My Holdings" table with live stock prices, P&L (₹ & %), and Action recommendation (SELL / HOLD / BUY)
- Add "Add Trade" modal dialog to record new buys directly from web

- [ ] **Step 1: Update `src/dashboard.py` with `/api/portfolio` routes**
- [ ] **Step 2: Update `static/index.html` with Portfolio section & trade modal**
- [ ] **Step 3: Update `static/style.css` for portfolio table and modal**
- [ ] **Step 4: Update `static/app.js` to render portfolio data and handle form submits**

---

### Task 4: End-to-End Verification & Server Launch

- [ ] **Step 1: Run full pytest suite**
- [ ] **Step 2: Launch Flask dashboard & Telegram Bot background process**
- [ ] **Step 3: Verify portfolio API & Telegram command response**

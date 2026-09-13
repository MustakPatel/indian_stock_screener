import os
import json
from datetime import datetime
import yfinance as yf

DEFAULT_PORTFOLIO_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "portfolio.json")
)

def load_holdings(filepath: str = DEFAULT_PORTFOLIO_FILE) -> list:
    """Loads holdings array from JSON storage file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading portfolio file {filepath}: {e}")
        return []

def save_holdings(holdings: list, filepath: str = DEFAULT_PORTFOLIO_FILE) -> bool:
    """Saves holdings array to JSON storage file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(holdings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving portfolio file {filepath}: {e}")
        return False

def add_holding(symbol: str, quantity: float, buy_price: float, filepath: str = DEFAULT_PORTFOLIO_FILE) -> dict:
    """Adds or updates a stock position in the portfolio."""
    sym = symbol.upper()
    if not sym.endswith(".NS") and not sym.endswith(".BO"):
        sym = f"{sym}.NS"
        
    holdings = load_holdings(filepath)
    existing = next((h for h in holdings if h["symbol"] == sym), None)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if existing:
        # Calculate average buy price
        total_qty = existing["quantity"] + quantity
        avg_price = round(((existing["quantity"] * existing["buy_price"]) + (quantity * buy_price)) / total_qty, 2)
        existing["quantity"] = total_qty
        existing["buy_price"] = avg_price
        existing["buy_date"] = today_str
        new_entry = existing
    else:
        new_entry = {
            "symbol": sym,
            "quantity": float(quantity),
            "buy_price": float(buy_price),
            "buy_date": today_str
        }
        holdings.append(new_entry)
        
    save_holdings(holdings, filepath)
    return new_entry

def remove_holding(symbol: str, filepath: str = DEFAULT_PORTFOLIO_FILE) -> bool:
    """Removes a stock position from the portfolio."""
    sym = symbol.upper()
    if not sym.endswith(".NS") and not sym.endswith(".BO"):
        sym = f"{sym}.NS"
        
    holdings = load_holdings(filepath)
    filtered = [h for h in holdings if h["symbol"] != sym]
    if len(filtered) < len(holdings):
        save_holdings(filtered, filepath)
        return True
    return False

def calculate_portfolio_summary(holdings: list = None, live_prices: dict = None, filepath: str = DEFAULT_PORTFOLIO_FILE) -> dict:
    """Calculates total invested, current market value, and P&L breakdown per stock."""
    if holdings is None:
        holdings = load_holdings(filepath)
        
    if not holdings:
        return {
            "total_invested": 0.0,
            "current_value": 0.0,
            "total_pnl": 0.0,
            "pnl_pct": 0.0,
            "holdings": []
        }
        
    # Fetch live market prices if not supplied
    if live_prices is None:
        live_prices = {}
        for h in holdings:
            sym = h["symbol"]
            try:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    live_prices[sym] = round(float(hist["Close"].iloc[-1]), 2)
                else:
                    live_prices[sym] = h["buy_price"]
            except Exception:
                live_prices[sym] = h["buy_price"]
                
    total_invested = 0.0
    current_value = 0.0
    enriched_holdings = []
    
    for h in holdings:
        sym = h["symbol"]
        qty = h["quantity"]
        buy_p = h["buy_price"]
        cur_p = live_prices.get(sym, buy_p)
        
        invested = round(qty * buy_p, 2)
        val = round(qty * cur_p, 2)
        pnl = round(val - invested, 2)
        pnl_pct = round((pnl / invested) * 100, 2) if invested > 0 else 0.0
        
        total_invested += invested
        current_value += val
        
        # Action Recommendation for Holding
        if pnl_pct >= 5.0:
            rec = "🟢 TAKE PROFIT / TARGET HIT"
        elif pnl_pct <= -2.0:
            rec = "🔴 EXIT / STOP LOSS HIT"
        else:
            rec = "🟡 HOLD"
            
        enriched_holdings.append({
            "symbol": sym,
            "quantity": qty,
            "buy_price": buy_p,
            "current_price": cur_p,
            "invested": invested,
            "current_value": val,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "buy_date": h.get("buy_date", "N/A"),
            "recommendation": rec
        })
        
    total_pnl = round(current_value - total_invested, 2)
    pnl_pct = round((total_pnl / total_invested) * 100, 2) if total_invested > 0 else 0.0
    
    return {
        "total_invested": round(total_invested, 2),
        "current_value": round(current_value, 2),
        "total_pnl": total_pnl,
        "pnl_pct": pnl_pct,
        "holdings": enriched_holdings
    }

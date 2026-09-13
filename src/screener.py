import yfinance as yf
import pandas as pd
import ta

DEFAULT_NSE_WATCHLIST = [
    # Core Heavyweights
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "SBIN.NS", "TATASTEEL.NS", "AXISBANK.NS", "LT.NS",
    # High-Profit Multibagger & Momentum Leaders (Defence, Railways, High Growth)
    "HAL.NS", "BEL.NS", "RVNL.NS", "IRFC.NS", "SUZLON.NS",
    "ZOMATO.NS", "TRENT.NS", "DIXON.NS", "BHEL.NS", "MAZDOCK.NS"
]

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates EMA 20, 50, RSI 14, MACD, and Volume Ratio for input price dataframe."""
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
    # Avoid division by zero
    df["Volume_Ratio"] = df["Volume"] / avg_vol.replace(0, 1)
    
    return df

def evaluate_signals(row: dict) -> dict:
    """Evaluates technical indicators to assign signal type, targets, stop loss, and actionable investment decision."""
    close = float(row.get("Close", 0))
    ema20 = float(row.get("EMA_20", 0))
    ema50 = float(row.get("EMA_50", 0))
    rsi = float(row.get("RSI_14", 50))
    macd = float(row.get("MACD", 0))
    macd_sig = float(row.get("MACD_Signal", 0))
    vol_ratio = float(row.get("Volume_Ratio", 1.0))
    
    signal_type = "NEUTRAL"
    confidence = 50
    action = "HOLD"
    action_badge = "🟡 HOLD / WATCH"
    action_desc = "Market consolidating; wait for a confirmed breakout or dip before allocating capital."
    
    if close > ema20 > ema50 and rsi > 55 and macd > macd_sig and vol_ratio >= 1.5:
        signal_type = "BULLISH_BREAKOUT"
        confidence = 85
        action = "BUY"
        action_badge = "🟢 PUT MONEY HERE (BUY)"
        action_desc = "Strong volume breakout above key moving averages. High probability swing buy setup."
    elif rsi < 32 and close > ema50:
        signal_type = "OVERSOLD_BOUNCE"
        confidence = 75
        action = "BUY"
        action_badge = "🟢 PUT MONEY HERE (BUY DIPS)"
        action_desc = "RSI oversold near major EMA support. Good risk-reward entry point."
    elif rsi > 70 and macd < macd_sig:
        signal_type = "BEARISH_REVERSAL"
        confidence = 75
        action = "SELL"
        action_badge = "🔴 WITHDRAW MONEY (SELL/EXIT)"
        action_desc = "Stock is overbought and losing momentum. Lock in profits or exit position."
    elif rsi < 35 and close < ema50:
        signal_type = "BEARISH_BREAKDOWN"
        confidence = 70
        action = "SELL"
        action_badge = "🔴 WITHDRAW MONEY (AVOID/EXIT)"
        action_desc = "Price breaking down below key moving averages. High risk of further decline."
    elif close > ema20 and rsi > 50:
        signal_type = "BULLISH_MOMENTUM"
        confidence = 65
        action = "BUY"
        action_badge = "🟢 PUT MONEY HERE (ACCUMULATE)"
        action_desc = "Positive trend momentum above 20 EMA."
        
    target_1 = round(close * 1.025, 2)
    target_2 = round(close * 1.05, 2)
    stop_loss = round(close * 0.985, 2)
    
    return {
        "symbol": row.get("Symbol", "UNKNOWN"),
        "price": round(close, 2),
        "signal_type": signal_type,
        "action": action,
        "action_badge": action_badge,
        "action_desc": action_desc,
        "confidence": confidence,
        "rsi": round(rsi, 2),
        "vol_ratio": round(vol_ratio, 2),
        "target_1": target_1,
        "target_2": target_2,
        "stop_loss": stop_loss
    }

from src.backtester import backtest_stock

def scan_stocks(symbols: list = None) -> list:
    """Scans watchlist of NSE symbols and returns evaluated signals with historical win-rate backtest."""
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
            
            # Attach 1-year historical win-rate backtest
            bt_res = backtest_stock(sym)
            sig["win_rate"] = bt_res["win_rate"]
            sig["total_backtest_trades"] = bt_res["total_trades"]
            sig["avg_backtest_return"] = bt_res["avg_return"]
            sig["verdict"] = bt_res["verdict"]
            sig["verdict_badge_class"] = bt_res["badge_class"]

            results.append(sig)
        except Exception as e:
            print(f"Error scanning {sym}: {e}")
    return results


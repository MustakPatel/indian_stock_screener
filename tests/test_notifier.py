import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.notifier import format_telegram_alert
except ModuleNotFoundError:
    from notifier import format_telegram_alert

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
    assert "2950" in message
    assert "Very Positive" in message
    assert "3020" in message
    assert "2910" in message

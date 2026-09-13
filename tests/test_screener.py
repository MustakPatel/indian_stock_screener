import os
import sys
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.screener import calculate_indicators, evaluate_signals
except ModuleNotFoundError:
    from screener import calculate_indicators, evaluate_signals

def test_calculate_indicators():
    # Generate 60 days of synthetic price data
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
    assert signal["confidence"] >= 75
    assert signal["target_1"] > 2950.0
    assert signal["stop_loss"] < 2950.0

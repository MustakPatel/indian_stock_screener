import pytest
from src.backtester import backtest_stock

def test_backtest_stock_structure():
    res = backtest_stock("ZOMATO.NS", period="3mo")
    assert "symbol" in res
    assert "win_rate" in res
    assert "total_trades" in res
    assert "verdict" in res
    assert isinstance(res["win_rate"], float) or isinstance(res["win_rate"], int)

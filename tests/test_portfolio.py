import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.portfolio import load_holdings, save_holdings, add_holding, remove_holding, calculate_portfolio_summary
except ModuleNotFoundError:
    from portfolio import load_holdings, save_holdings, add_holding, remove_holding, calculate_portfolio_summary

def test_load_and_save_holdings(tmp_path):
    test_file = tmp_path / "test_portfolio.json"
    data = [{"symbol": "RELIANCE.NS", "quantity": 10, "buy_price": 1200.0, "buy_date": "2026-09-01"}]
    
    save_holdings(data, filepath=str(test_file))
    loaded = load_holdings(filepath=str(test_file))
    
    assert len(loaded) == 1
    assert loaded[0]["symbol"] == "RELIANCE.NS"

def test_add_and_remove_holding(tmp_path):
    test_file = tmp_path / "test_portfolio.json"
    save_holdings([], filepath=str(test_file))
    
    add_holding("INFY.NS", 15, 1020.0, filepath=str(test_file))
    holdings = load_holdings(filepath=str(test_file))
    assert len(holdings) == 1
    assert holdings[0]["symbol"] == "INFY.NS"
    
    # Remove holding
    removed = remove_holding("INFY.NS", filepath=str(test_file))
    assert removed is True
    assert len(load_holdings(filepath=str(test_file))) == 0

def test_calculate_portfolio_summary():
    holdings = [{"symbol": "RELIANCE.NS", "quantity": 10, "buy_price": 1200.0, "buy_date": "2026-09-01"}]
    # Mock live price dictionary
    mock_prices = {"RELIANCE.NS": 1250.0}
    
    summary = calculate_portfolio_summary(holdings, live_prices=mock_prices)
    assert summary["total_invested"] == 12000.0
    assert summary["current_value"] == 12500.0
    assert summary["total_pnl"] == 500.0
    assert summary["pnl_pct"] == 4.17
    assert len(summary["holdings"]) == 1
    assert summary["holdings"][0]["pnl"] == 500.0

import pytest
from src.telegram_bot import process_telegram_command

def test_process_telegram_command_help():
    response = "\n".join(process_telegram_command("/help"))
    assert "/scan" in response
    assert "/portfolio" in response
    assert "/buy" in response

def test_process_telegram_command_buy_and_sell(tmp_path):
    test_file = tmp_path / "test_portfolio.json"
    
    # Test buy command
    buy_resp = "\n".join(process_telegram_command("/buy RELIANCE 10 1200", filepath=str(test_file)))
    assert "ADDED" in buy_resp.upper()
    assert "RELIANCE.NS" in buy_resp
    
    # Test portfolio command
    port_resp = "\n".join(process_telegram_command("/portfolio", filepath=str(test_file)))
    assert "PORTFOLIO" in port_resp.upper()
    
    # Test sell command
    sell_resp = "\n".join(process_telegram_command("/sell RELIANCE", filepath=str(test_file)))
    assert "CLOSED POSITION" in sell_resp.upper()

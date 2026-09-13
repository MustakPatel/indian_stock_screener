import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.digest import get_market_indices, get_top_news_headlines, generate_morning_digest

def test_get_market_indices():
    indices = get_market_indices()
    assert isinstance(indices, dict)
    assert "NIFTY 50" in indices
    assert "SENSEX" in indices
    assert "change_pct" in indices["NIFTY 50"]

def test_get_top_news_headlines():
    headlines = get_top_news_headlines()
    assert isinstance(headlines, list)
    assert len(headlines) > 0

def test_generate_morning_digest():
    digest = generate_morning_digest()
    assert isinstance(digest, str)
    assert "DAILY MARKET & TECH MORNING DIGEST" in digest
    assert "MARKET SENTIMENT" in digest

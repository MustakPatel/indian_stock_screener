import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.sentiment import calculate_text_sentiment, format_sentiment_summary, analyze_sentiment
except ModuleNotFoundError:
    from sentiment import calculate_text_sentiment, format_sentiment_summary, analyze_sentiment

def test_calculate_text_sentiment():
    pos_text = "Reliance Industries reports 25% surge in quarterly net profit, beats estimates."
    neg_text = "Tata Motors faces supply chain disruption, quarterly revenue drops sharply."
    
    pos_score = calculate_text_sentiment(pos_text)
    neg_score = calculate_text_sentiment(neg_text)
    
    assert pos_score > 0.2
    assert neg_score < -0.2

def test_format_sentiment_summary():
    result = format_sentiment_summary(0.65, ["Strong Q3 results", "Expansion in retail sector"])
    assert result["label"] in ["Positive", "Very Positive"]
    assert len(result["headlines"]) == 2

def test_analyze_sentiment_fallback():
    res = analyze_sentiment("RELIANCE.NS")
    assert "score" in res
    assert "label" in res
    assert "headlines" in res

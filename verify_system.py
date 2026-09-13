import sys
import os

# Add root folder to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.screener import scan_stocks, evaluate_signals
from src.sentiment import analyze_sentiment
from src.notifier import format_telegram_alert

def run_verification():
    print("==================================================")
    print("🇮🇳 RUNNING END-TO-END INDIAN STOCK SCREENER VERIFICATION")
    print("==================================================")
    
    # 1. Test Signal Evaluation
    test_data = {
        "Symbol": "RELIANCE.NS",
        "Close": 2950.0,
        "EMA_20": 2940.0,
        "EMA_50": 2900.0,
        "RSI_14": 62.5,
        "MACD": 15.0,
        "MACD_Signal": 10.0,
        "Volume_Ratio": 2.1
    }
    signal = evaluate_signals(test_data)
    print(f"\n[1/3] Evaluated Signal for RELIANCE.NS:")
    print(f"      Signal Type: {signal['signal_type']}")
    print(f"      Target 1: ₹{signal['target_1']} | Target 2: ₹{signal['target_2']} | Stop Loss: ₹{signal['stop_loss']}")
    assert signal['signal_type'] == "BULLISH_BREAKOUT"
    
    # 2. Test Sentiment Scoring
    sent = analyze_sentiment("RELIANCE.NS")
    print(f"\n[2/3] News Sentiment Analysis:")
    print(f"      Sentiment Score: {sent['score']} ({sent['label']})")
    print(f"      Top Headline: {sent['headlines'][0] if sent['headlines'] else 'N/A'}")
    assert 'label' in sent
    
    # 3. Test Telegram Alert Formatting
    alert_msg = format_telegram_alert(signal, sent)
    print(f"\n[3/3] Generated Telegram Alert Message:\n")
    print(alert_msg)
    assert "RELIANCE.NS" in alert_msg
    assert "BULLISH_BREAKOUT" in alert_msg
    
    print("\n✅ ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_verification()

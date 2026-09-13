import pytest
from src.ipo import get_active_ipos, evaluate_ipo_recommendation

def test_evaluate_ipo_recommendation():
    # High GMP IPO
    ipo_data = {
        "name": "Tata Tech EV IPO",
        "issue_price": 500.0,
        "gmp_price": 250.0, # 50% GMP
        "subscription_x": 45.0
    }
    eval_res = evaluate_ipo_recommendation(ipo_data)
    assert eval_res["recommendation"] == "APPLY_FOR_HIGH_GAINS"
    assert eval_res["gmp_pct"] == 50.0
    assert "🟢" in eval_res["badge"]

def test_get_active_ipos():
    ipos = get_active_ipos()
    assert isinstance(ipos, list)
    assert len(ipos) > 0
    assert "name" in ipos[0]
    assert "recommendation" in ipos[0]

import pytest
from datetime import datetime, timedelta
from app.backend.risk import calculate_risk_score

def test_risk_score_calculation():
    now = datetime.utcnow()

    # High severity (3), High confidence (0.9), Recent (<30min), High cluster (5 neighbors)
    # Score = (1.5 * 3) + (0.6 * 0.9) + 0.5 + min(0.8, 0.2*5)
    # Score = 4.5 + 0.54 + 0.5 + 0.8 = 6.34
    score = calculate_risk_score(3, 0.9, now, 5)
    assert score == 6.34

def test_risk_score_decay():
    now = datetime.utcnow()
    old_time = now - timedelta(hours=3)

    # Severity 2, Conf 0.5, Old (0 boost), No cluster
    # Score = (1.5 * 2) + (0.6 * 0.5) + 0 + 0 = 3.0 + 0.3 = 3.3
    score = calculate_risk_score(2, 0.5, old_time, 0)
    assert score == 3.3

def test_cluster_cap():
    now = datetime.utcnow()
    # verify cluster boost caps at 0.8 (4 neighbors)
    score_4 = calculate_risk_score(1, 0, now, 4) # boost 0.8
    score_10 = calculate_risk_score(1, 0, now, 10) # boost 0.8

    assert score_4 == score_10

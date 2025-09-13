import pandas as pd
from datetime import datetime, timedelta
from src.forecasting.rules import direction_and_confidence, Thresholds, PredictCfg

def _df(direction="up"):
    now = datetime(2024,1,1,12,0,0)
    times = [now - timedelta(minutes=60) + timedelta(minutes=5*i) for i in range(12)]
    sent = [0.02]*12
    if direction == "up":
        sent[-4:] = [0.2]*4
    elif direction == "down":
        sent[-4:] = [-0.2]*4
    conf = [0.8]*12
    return pd.DataFrame({"datetime": times, "sentiment": [1 if s>0 else (-1 if s<0 else 0) for s in sent], "confidence": [abs(s) for s in sent]})

def test_direction_up():
    d, c, x = direction_and_confidence(_df("up"), Thresholds(0.03,0.02), PredictCfg(60,3))
    assert d == "UP" and 0 <= c <= 0.95

def test_direction_down():
    d, _, _ = direction_and_confidence(_df("down"), Thresholds(0.03,0.02), PredictCfg(60,3))
    assert d == "DOWN"

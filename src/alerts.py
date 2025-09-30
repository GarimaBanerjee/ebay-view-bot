from __future__ import annotations
import pandas as pd
from .utils import notify

def alert_ctr_drops(df: pd.DataFrame, threshold_drop: float=0.2) -> int:
    """
    df must have columns: Title, Click-Through Rate (as % or float).
    Triggers when CTR decreased by > threshold_drop (relative).
    For demo, we simply flag CTR < 0.5% as a 'drop' (customize with history later).
    """
    triggered = 0
    def to_float(x):
        try:
            s = str(x)
            return float(s.replace("%",""))/100 if "%" in s else float(s)
        except: return None

    df = df.copy()
    df["CTR_NUM"] = df["Click-Through Rate"].map(to_float)
    for _, r in df.iterrows():
        ctr = r.get("CTR_NUM")
        if ctr is not None and ctr < 0.005:   # < 0.5%
            title = str(r.get("Title") or "")[:120]
            notify("Low CTR detected", f"{title}\nCTR={ctr:.2%}")
            triggered += 1
    return triggered

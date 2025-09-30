from __future__ import annotations
import pandas as pd
import re
from pathlib import Path

TITLE_MIN, TITLE_MAX = 64, 80
STOP_WORDS = {"the","a","an","with","for","and","or"}

def audit_titles(df: pd.DataFrame, primary_kw: str | None = None) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        title = str(r.get("Title","")).strip()
        length = len(title)
        length_ok = TITLE_MIN <= length <= TITLE_MAX
        kw_ok = True
        if primary_kw:
            kw_ok = primary_kw.lower() in title.lower()
        stop_count = len([w for w in re.findall(r"[A-Za-z]+", title.lower()) if w in STOP_WORDS])
        rows.append({
            "ListingID": r.get("ListingID",""),
            "Title": title,
            "Length": length,
            "LengthOK": length_ok,
            "ContainsPrimaryKW": kw_ok,
            "StopWords": stop_count,
            "TitleSuggestion": suggest_title(title, primary_kw)
        })
    return pd.DataFrame(rows)

def suggest_title(title: str, primary_kw: str | None) -> str:
    t = re.sub(r"\s+", " ", title).strip()
    if primary_kw and primary_kw.lower() not in t.lower():
        t = f"{primary_kw} {t}"
    if len(t) > TITLE_MAX:
        t = t[:TITLE_MAX].rstrip()
    return t

def merge_audit(perf_df: pd.DataFrame, title_audit: pd.DataFrame) -> pd.DataFrame:
    merged = perf_df.merge(title_audit, on=["ListingID","Title"], how="left")
    score = 0
    merged["SEOScore"] = (
        (merged["LengthOK"].fillna(False).astype(int)*40) +
        (merged["ContainsPrimaryKW"].fillna(False).astype(int)*40) +
        (merged["StopWords"].fillna(0).rsub(5).clip(lower=0, upper=5)*4)  # up to +20
    )
    return merged

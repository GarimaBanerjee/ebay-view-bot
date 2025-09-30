import pandas as pd
from pathlib import Path

def ingest_report(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p)
    # Normalize expected columns
    rename_map = {
        "Listing ID": "ListingID", "listing_id":"ListingID",
        "Title":"Title","Impressions":"Impressions","Clicks":"Clicks","Sales":"Sales","Price":"Price",
        "Date":"Date","date":"Date"
    }
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    needed = ["Date","ListingID","Title","Impressions","Clicks","Sales","Price"]
    for col in needed:
        if col not in df.columns:
            df[col] = 0 if col in ["Impressions","Clicks","Sales"] else ""
    # Types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Impressions","Clicks","Sales"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["CTR"] = (df["Clicks"].astype(float) / df["Impressions"].replace(0, pd.NA)).fillna(0).round(4)
    return df

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    agg = (df
           .groupby(["ListingID","Title"], dropna=False)
           .agg(Impressions=("Impressions","sum"),
                Clicks=("Clicks","sum"),
                Sales=("Sales","sum"),
                AvgPrice=("Price","mean"))
           .reset_index())
    agg["CTR"] = (agg["Clicks"] / agg["Impressions"].replace(0, pd.NA)).fillna(0).round(4)
    return agg

def save_csv(df: pd.DataFrame, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

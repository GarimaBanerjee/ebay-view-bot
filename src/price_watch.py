from __future__ import annotations
import re
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from .utils import make_fetcher, normalize_space

PRICE_RE = re.compile(r"(\$|£|€)\s?\d{1,3}(?:[,\d]{3})*(?:\.\d{2})?")

def parse_price(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # Common patterns
    cands = [
        soup.select_one('[itemprop=price]'),
        soup.select_one('span[itemprop=price]'),
        soup.select_one('span#prcIsum'),
        soup.select_one('span.x-price-primary'),
        soup.select_one('div.x-price-section span'),
    ]
    for c in cands:
        if c and normalize_space(c.get_text()):
            return normalize_space(c.get_text())
    m = PRICE_RE.search(html or "")
    return m.group(0) if m else ""

def watch(csv_path: str, out_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    f = make_fetcher()
    rows = []
    for _, r in df.iterrows():
        url = r["url"]
        resp = f.get(url)
        if not resp or resp.status_code != 200:
            rows.append({"url": url, "sku": r.get("sku",""), "price_text": "", "ok": False})
            continue
        price_text = parse_price(resp.text)
        rows.append({"url": url, "sku": r.get("sku",""), "price_text": price_text, "ok": True})
    out = pd.DataFrame(rows)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    return out

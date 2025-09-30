from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from .utils import make_fetcher, normalize_space

MARKETS = {
    "US":"https://www.ebay.com/sch/i.html",
    "UK":"https://www.ebay.co.uk/sch/i.html",
    "DE":"https://www.ebay.de/sch/i.html",
    "AU":"https://www.ebay.com.au/sch/i.html"
}

def build_search_url(keyword: str, market: str="US") -> str:
    base = MARKETS.get(market.upper(), MARKETS["US"])
    qs = urllib.parse.urlencode({"_nkw": keyword})
    return f"{base}?{qs}"

def snapshot(keyword: str, market: str="US", limit: int=40) -> pd.DataFrame:
    url = build_search_url(keyword, market)
    f = make_fetcher()
    r = f.get(url)
    if not r or r.status_code != 200:
        raise RuntimeError(f"Failed to fetch search results: {url}")
    soup = BeautifulSoup(r.text, "lxml")
    results = []
    # Generic selectors used across eBay SERPs (may evolve over time)
    for i, item in enumerate(soup.select("li.s-item")[:limit], start=1):
        title_el = item.select_one("h3.s-item__title")
        link_el = item.select_one("a.s-item__link")
        price_el = item.select_one(".s-item__price")
        title = normalize_space(title_el.get_text()) if title_el else ""
        link = link_el.get("href") if link_el else ""
        price = normalize_space(price_el.get_text()) if price_el else ""
        if not title:
            continue
        results.append({"Position": i, "Title": title, "URL": link, "PriceText": price, "Keyword": keyword, "Market": market})
    return pd.DataFrame(results)

def save_csv(df: pd.DataFrame, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

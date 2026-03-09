#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from datetime import datetime, date, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.neste.lv/lv/content/degvielas-cenas"
CSV_PATH = Path("docs/data/fuel_prices.csv")

PRODUCTS = [
    "Neste Futura 95",
    "Neste Futura 98",
    "Neste Futura D",
    "Neste Pro Diesel",
]

def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FuelTracker/1.0; +https://github.com/)",
        "Accept-Language": "lv,en;q=0.9",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def extract_prices(html: str) -> dict[str, float]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    compact = re.sub(r"\s+", " ", text)

    prices: dict[str, float] = {}
    for product in PRODUCTS:
        pattern = re.escape(product) + r".{0,120}?(\d+[.,]\d{3})"
        match = re.search(pattern, compact, flags=re.IGNORECASE)
        if not match:
            idx = compact.lower().find(product.lower())
            if idx != -1:
                window = compact[idx: idx + 250]
                match2 = re.search(r"(\d+[.,]\d{3})", window)
                if match2:
                    match = match2
        if match:
            prices[product] = float(match.group(1).replace(",", "."))
    if not prices:
        raise RuntimeError("Could not find any prices on the page. The site structure may have changed.")
    return prices

def ensure_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["date", "timestamp_utc", "product", "price_eur_per_l", "source_url"],
            )
            writer.writeheader()

def load_existing_keys(path: Path) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    if not path.exists():
        return keys
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keys.add((row["date"], row["product"]))
    return keys

def append_rows(path: Path, prices: dict[str, float]) -> int:
    ensure_csv(path)
    existing = load_existing_keys(path)
    today = date.today().isoformat()
    now_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows_added = 0

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "timestamp_utc", "product", "price_eur_per_l", "source_url"],
        )
        for product, price in prices.items():
            key = (today, product)
            if key in existing:
                continue
            writer.writerow(
                {
                    "date": today,
                    "timestamp_utc": now_utc,
                    "product": product,
                    "price_eur_per_l": f"{price:.3f}",
                    "source_url": URL,
                }
            )
            rows_added += 1
    return rows_added

def main() -> None:
    html = fetch_html(URL)
    prices = extract_prices(html)
    rows_added = append_rows(CSV_PATH, prices)
    print(f"Found {len(prices)} prices. Added {rows_added} new rows to {CSV_PATH}.")

if __name__ == "__main__":
    main()

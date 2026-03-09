#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import pathlib
import re
import sys
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

URL = "https://www.neste.lv/lv/content/degvielas-cenas"
DATA_DIR = pathlib.Path("data")
CSV_PATH = DATA_DIR / "fuel_prices.csv"

FUEL_NAMES = [
    "Neste Futura 95",
    "Neste Futura 98",
    "Neste Futura D",
    "Neste Pro Diesel",
]

def fetch_html() -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NestePriceTracker/1.0; +https://github.com/)"
    }
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def extract_prices(html: str) -> Dict[str, float]:
    # First try with BeautifulSoup text scan. The prices are currently visible in the HTML.
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    prices: Dict[str, float] = {}

    for i, line in enumerate(lines):
        if line in FUEL_NAMES:
            for candidate in lines[i + 1 : i + 6]:
                m = re.fullmatch(r"(\d+\.\d{3})", candidate)
                if m:
                    prices[line] = float(m.group(1))
                    break

    # Fallback: regex against the raw HTML in case the visible text layout changes slightly.
    if len(prices) < 2:
        for fuel in FUEL_NAMES:
            pattern = re.compile(re.escape(fuel) + r".{0,300}?(\d+\.\d{3})", re.DOTALL)
            match = pattern.search(html)
            if match:
                prices[fuel] = float(match.group(1))

    if not prices:
        raise RuntimeError("Could not find any fuel prices on the page.")

    return prices

def read_existing_keys() -> set[tuple[str, str]]:
    if not CSV_PATH.exists():
        return set()
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {(row["date"], row["product"]) for row in reader}

def append_rows(prices: Dict[str, float]) -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    now_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    existing_keys = read_existing_keys()

    fieldnames = ["date", "timestamp_utc", "product", "price_eur_l", "source_url"]
    needs_header = not CSV_PATH.exists()

    added = 0
    with CSV_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()

        for product in FUEL_NAMES:
            if product not in prices:
                continue
            key = (today, product)
            if key in existing_keys:
                continue
            writer.writerow(
                {
                    "date": today,
                    "timestamp_utc": now_utc,
                    "product": product,
                    "price_eur_l": f"{prices[product]:.3f}",
                    "source_url": URL,
                }
            )
            added += 1
    return added

def main() -> int:
    html = fetch_html()
    prices = extract_prices(html)
    added = append_rows(prices)
    print("Scraped prices:")
    for name, price in prices.items():
        print(f" - {name}: {price:.3f} EUR/l")
    print(f"Added {added} new rows to {CSV_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

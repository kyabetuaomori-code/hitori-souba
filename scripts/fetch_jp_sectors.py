import json
from datetime import datetime, timezone

import yfinance as yf

SECTORS = [
    ("1617", "食品"),
    ("1618", "エネルギー資源"),
    ("1619", "建設・資材"),
    ("1620", "素材・化学"),
    ("1621", "医薬品"),
    ("1622", "自動車・輸送機"),
    ("1623", "鉄鋼・非鉄金属"),
    ("1624", "機械"),
    ("1625", "電機・精密"),
    ("1626", "情報通信・サービスその他"),
    ("1627", "電力・ガス"),
    ("1628", "運輸・物流"),
    ("1629", "商社・卸売"),
    ("1630", "小売"),
    ("1631", "銀行"),
    ("1632", "金融(除く銀行)"),
    ("1633", "不動産"),
]

OUTPUT_FILE = "sectors_jp.json"


def main():
    tickers = [f"{code}.T" for code, _ in SECTORS]
    data = yf.download(
        " ".join(tickers),
        period="3mo",
        interval="1d",
        progress=False,
        group_by="ticker",
    )

    sectors = {}
    for code, name in SECTORS:
        ticker = f"{code}.T"
        try:
            closes = data[ticker]["Close"].dropna()
        except KeyError:
            continue
        if closes.empty:
            continue

        series = [round(float(v), 1) for v in closes.tolist()]
        latest = series[-1]
        first = series[0]
        prev = series[-2] if len(series) > 1 else first
        change = round(latest - prev, 1)
        pct = round((latest - prev) / prev * 100, 2) if prev else 0
        change_3mo_pct = round((latest - first) / first * 100, 2) if first else 0

        sectors[code] = {
            "name": name,
            "series": series,
            "latest": latest,
            "change": change,
            "pct": pct,
            "change_3mo_pct": change_3mo_pct,
        }

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "period": "3mo",
        "sectors": sectors,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUTPUT_FILE} with {len(sectors)} sectors")


if __name__ == "__main__":
    main()

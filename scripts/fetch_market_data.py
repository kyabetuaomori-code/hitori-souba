import json
from datetime import datetime, timezone

import yfinance as yf

FX_MAJORS = [
    ("USDJPY", "JPY=X", "米ドル/円"),
    ("EURUSD", "EURUSD=X", "ユーロ/米ドル"),
    ("GBPUSD", "GBPUSD=X", "英ポンド/米ドル"),
    ("EURJPY", "EURJPY=X", "ユーロ/円"),
    ("GBPJPY", "GBPJPY=X", "英ポンド/円"),
    ("AUDUSD", "AUDUSD=X", "豪ドル/米ドル"),
    ("AUDJPY", "AUDJPY=X", "豪ドル/円"),
    ("USDCHF", "CHF=X", "米ドル/スイスフラン"),
    ("USDCAD", "CAD=X", "米ドル/カナダドル"),
    ("NZDUSD", "NZDUSD=X", "NZドル/米ドル"),
    ("EURGBP", "EURGBP=X", "ユーロ/英ポンド"),
]

FX_EM = [
    ("USDCNH", "CNY=X", "米ドル/人民元"),
    ("USDINR", "INR=X", "米ドル/インドルピー"),
    ("USDKRW", "KRW=X", "米ドル/韓国ウォン"),
    ("USDBRL", "BRL=X", "米ドル/ブラジルレアル"),
    ("USDMXN", "MXN=X", "米ドル/メキシコペソ"),
    ("USDZAR", "ZAR=X", "米ドル/南アフリカランド"),
    ("USDTRY", "TRY=X", "米ドル/トルコリラ"),
    ("USDIDR", "IDR=X", "米ドル/インドネシアルピア"),
    ("USDTHB", "THB=X", "米ドル/タイバーツ"),
    ("USDPHP", "PHP=X", "米ドル/フィリピンペソ"),
]

SECTORS_US = [
    ("XLK", "XLK", "テクノロジー"),
    ("XLF", "XLF", "金融"),
    ("XLE", "XLE", "エネルギー"),
    ("XLV", "XLV", "ヘルスケア"),
    ("XLY", "XLY", "一般消費財"),
    ("XLP", "XLP", "生活必需品"),
    ("XLI", "XLI", "資本財"),
    ("XLB", "XLB", "素材"),
    ("XLU", "XLU", "公益事業"),
    ("XLRE", "XLRE", "不動産"),
    ("XLC", "XLC", "コミュニケーション"),
]

SECTORS_JP = [
    ("1617", "1617.T", "食品"),
    ("1618", "1618.T", "エネルギー資源"),
    ("1619", "1619.T", "建設・資材"),
    ("1620", "1620.T", "素材・化学"),
    ("1621", "1621.T", "医薬品"),
    ("1622", "1622.T", "自動車・輸送機"),
    ("1623", "1623.T", "鉄鋼・非鉄金属"),
    ("1624", "1624.T", "機械"),
    ("1625", "1625.T", "電機・精密"),
    ("1626", "1626.T", "情報通信・サービスその他"),
    ("1627", "1627.T", "電力・ガス"),
    ("1628", "1628.T", "運輸・物流"),
    ("1629", "1629.T", "商社・卸売"),
    ("1630", "1630.T", "小売"),
    ("1631", "1631.T", "銀行"),
    ("1632", "1632.T", "金融(除く銀行)"),
    ("1633", "1633.T", "不動産"),
]

GROUPS = {
    "fx_majors": FX_MAJORS,
    "fx_em": FX_EM,
    "sectors_us": SECTORS_US,
    "sectors_jp": SECTORS_JP,
}

OUTPUT_FILE = "market_data.json"


def fetch_group(items):
    tickers = [t for _, t, _ in items]
    data = yf.download(
        " ".join(tickers),
        period="3mo",
        interval="1d",
        progress=False,
        group_by="ticker",
    )

    result = {}
    for code, ticker, name in items:
        try:
            if len(tickers) == 1:
                closes = data["Close"].dropna()
            else:
                closes = data[ticker]["Close"].dropna()
        except KeyError:
            continue
        if closes.empty:
            continue

        series = [round(float(v), 4) for v in closes.tolist()]
        latest = series[-1]
        first = series[0]
        prev = series[-2] if len(series) > 1 else first
        change = round(latest - prev, 4)
        pct = round((latest - prev) / prev * 100, 2) if prev else 0
        change_period_pct = round((latest - first) / first * 100, 2) if first else 0

        result[code] = {
            "name": name,
            "series": series,
            "latest": latest,
            "change": change,
            "pct": pct,
            "change_period_pct": change_period_pct,
        }
    return result


def main():
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "period": "3mo",
    }
    for key, items in GROUPS.items():
        output[key] = fetch_group(items)
        print(f"{key}: {len(output[key])}/{len(items)} fetched")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

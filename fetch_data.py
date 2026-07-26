"""
指数監視パネル用データ取得スクリプト
GitHub Actionsから定期実行し、data.json を更新する。

必要ライブラリ: yfinance
    pip install yfinance --break-system-packages
"""
import json
import datetime
import yfinance as yf

# 監視対象のティッカー
TICKERS = {
    "nikkei_futures": "NIY=F",   # 日経225先物 (CME)
    "usdjpy": "JPY=X",           # ドル円
    "vix": "^VIX",               # VIX指数
    "us10y": "^TNX",             # 米10年債利回り (実際の値の10倍で返る)
}

LABELS = {
    "nikkei_futures": "日経225先物",
    "usdjpy": "USD/JPY",
    "vix": "VIX",
    "us10y": "米10年債利回り",
}


def fetch_one(symbol: str):
    """直近2営業日分の終値を取得し、現在値と前日比を計算する"""
    hist = yf.Ticker(symbol).history(period="5d", interval="1d")
    if hist.empty or len(hist) < 2:
        return None
    last = hist["Close"].iloc[-1]
    prev = hist["Close"].iloc[-2]
    change = last - prev
    pct = (change / prev) * 100 if prev else 0
    return {"value": round(float(last), 2), "change": round(float(change), 2), "pct": round(float(pct), 2)}


def main():
    result = {}
    for key, symbol in TICKERS.items():
        data = fetch_one(symbol)
        if data is None:
            continue
        # 米10年債利回りは ^TNX が実値の10倍で返ってくるので調整
        if key == "us10y":
            data["value"] = round(data["value"] / 10, 2)
            data["change"] = round(data["change"] / 10, 2)
        result[key] = {"label": LABELS[key], **data}

    output = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "readings": result,
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

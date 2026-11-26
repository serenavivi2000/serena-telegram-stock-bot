
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STOCKS = {
    "2330.TW": "台積電",
    "2317.TW": "鴻海",
    "2454.TW": "聯發科",
    "2308.TW": "台達電"
}

def get_stock_price(symbol, name):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d"}

    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()["chart"]["result"][0]
    meta = data["meta"]

    price = meta.get("regularMarketPrice")
    previous = meta.get("chartPreviousClose") or meta.get("previousClose")

    if price is None or previous is None:
        raise ValueError("無法取得完整股價資料")

    change = price - previous
    percent = change / previous * 100

    return (
        f"📈 {name}（{symbol}）\n"
        f"最新價格：{price:.2f} 元\n"
        f"漲跌：{change:+.2f} 元\n"
        f"漲跌幅：{percent:+.2f}%"
    )

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
        timeout=20
    )
    response.raise_for_status()

def main():
    now = datetime.now(ZoneInfo("Asia/Taipei"))

    messages = [
        "📊 Serena 台灣股票主動通知",
        f"查詢時間：{now:%Y-%m-%d %H:%M:%S}",
        ""
    ]

    for symbol, name in STOCKS.items():
        try:
            messages.append(get_stock_price(symbol, name))
        except Exception as error:
            messages.append(f"⚠️ {name} 查詢失敗：{error}")

        messages.append("")

    send_telegram("\n".join(messages))
    print("Telegram 股票通知已送出！")

if __name__ == "__main__":
    main()

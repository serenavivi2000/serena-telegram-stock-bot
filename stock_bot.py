
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# 讀取 GitHub Secrets
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# 台灣股票清單
STOCKS = {
    "2330.TW": "台積電",
    "2317.TW": "鴻海",
    "2454.TW": "聯發科",
    "2308.TW": "台達電"
}

def get_stock_price(symbol, name):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    response = requests.get(
        url,
        params={"range": "1d", "interval": "1m"},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    result = data["chart"]["result"]

    if not result:
        raise ValueError("查無股票資料")

    meta = result[0]["meta"]

    price = meta.get("regularMarketPrice")
    previous = meta.get("chartPreviousClose")

    if previous is None:
        previous = meta.get("previousClose")

    if price is None or previous is None or previous == 0:
        raise ValueError("股價資料不完整")

    change = price - previous
    percent = change / previous * 100

    return (
        f"📈 {name}（{symbol}）\n"
        f"目前股價：{price:.2f}\n"
        f"漲跌金額：{change:+.2f}\n"
        f"漲跌幅：{percent:+.2f}%"
    )


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )
    response.raise_for_status()

    if not response.json().get("ok"):
        raise RuntimeError("Telegram 傳送失敗")


def main():
    now = datetime.now(ZoneInfo("Asia/Taipei"))
    messages = [
        "📊 台灣股票爬蟲通知",
        f"查詢時間：{now:%Y-%m-%d %H:%M:%S}",
        ""
    ]

    for symbol, name in STOCKS.items():
        try:
            messages.append(get_stock_price(symbol, name))
        except Exception as error:
            messages.append(
                f"⚠️ {name}（{symbol}）查詢失敗：{error}"
            )

        messages.append("")

    send_telegram("\n".join(messages))
    print("Telegram 股票通知已送出！")


if __name__ == "__main__":
    main()

import time
import requests

# 各取引所のAPIエンドポイント
EXCHANGE_APIS = {
    "Bitfinex": "https://api-pub.bitfinex.com/v2/ticker/tBTCUSD",
    "Binance": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
    "Coinbase": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
    "Kraken": "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
    "Huobi": "https://api.huobi.pro/market/detail/merged?symbol=btcusdt",
    "OKX": "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT",
    "KuCoin": "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT",
    "Gate.io": "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT",
    "Bitstamp": "https://www.bitstamp.net/api/v2/ticker/btcusd/",
    "Gemini": "https://api.gemini.com/v1/pubticker/btcusd",
    "Poloniex": "https://api.poloniex.com/markets/BTC_USDT/ticker",
    "Crypto.com": "https://api.crypto.com/v2/public/get-ticker?instrument_name=BTC_USDT"
}

# スリッページと手数料のパラメータ
SLIPPAGE_RATE = 0.001           # 0.1% 一般的な値
FEE_RATE = 0.002                # 0.2% 一般的な値
TRANSFER_FEE_RATE = 0.001       # 0.1% 手数料でBTC移動
DEFAULT_TRADE_VOLUME = 0.01     # [BTC]デフォルトの取引量
MIN_PROFIT_AMOUNT = 10.0        # [$]最小利益額 ($50)
INTERVAL = 7.0                  # [sec]取引間隔
NUM_TRADE = 50                  # [回] シミュレーション上の取引回数

# 初期資産
INITIAL_BALANCE = 100000        # [BTC]仮想通貨に置く初期資産
INITIAL_BTC = 1.0               # [$]仮想通貨に置く初期資産

# 資産状況を保持する辞書
exchange_balances = {exchange: {"USD": INITIAL_BALANCE, "BTC": INITIAL_BTC} for exchange in EXCHANGE_APIS}

def fetch_prices():
    """
    各取引所のBTC価格を取得し、辞書形式で返す。
    """
    prices = {}
    for exchange, url in EXCHANGE_APIS.items():
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if exchange == "Bitfinex":
                prices[exchange] = data[6]
            elif exchange == "Binance":
                prices[exchange] = float(data["price"])
            elif exchange == "Coinbase":
                prices[exchange] = float(data["data"]["amount"])
            elif exchange == "Kraken":
                prices[exchange] = float(data["result"]["XXBTZUSD"]["c"][0])
            elif exchange == "Huobi":
                prices[exchange] = float(data["tick"]["close"])
            elif exchange == "OKX":
                prices[exchange] = float(data["data"][0]["last"])
            elif exchange == "KuCoin":
                prices[exchange] = float(data["data"]["price"])
            elif exchange == "Gate.io":
                prices[exchange] = float(data[0]["last"])
            elif exchange == "Bitstamp":
                prices[exchange] = float(data["last"])
            elif exchange == "Gemini":
                prices[exchange] = float(data["last"])
            elif exchange == "Poloniex":
                prices[exchange] = float(data["close"])
            elif exchange == "Crypto.com":
                prices[exchange] = float(data["result"]["data"][0]["a"])
        except Exception as e:
            print(f"Error fetching price from {exchange}: {e}")
            prices[exchange] = None
    return prices

def calculate_threshold_difference(min_price, max_price, trade_volume):
    """
    必要なしきい値を計算。
    """
    buy_slippage = min_price * SLIPPAGE_RATE * trade_volume
    sell_slippage = max_price * SLIPPAGE_RATE * trade_volume
    buy_fee = min_price * FEE_RATE * trade_volume
    sell_fee = max_price * FEE_RATE * trade_volume
    return buy_slippage + sell_slippage + buy_fee + sell_fee

def execute_trade(buy_exchange, sell_exchange, trade_volume, min_price, max_price):
    """
    売買を実行し、資産を更新。
    :param buy_exchange: 購入取引所
    :param sell_exchange: 売却取引所
    :param trade_volume: 取引量 (BTC)
    :param min_price: 購入価格 (USD/BTC)
    :param max_price: 売却価格 (USD/BTC)
    :return: 成功時は純利益を返し、失敗時はエラーメッセージを返す。
    """
    global exchange_balances

    # 資金の計算
    cost = trade_volume * min_price * (1 + SLIPPAGE_RATE)  # 購入コスト (USD)
    revenue = trade_volume * max_price * (1 - SLIPPAGE_RATE)  # 売却収益 (USD)

    # エラーチェック: 残高不足の場合
    if exchange_balances[buy_exchange]["USD"] < cost:
        return f"Insufficient USD in {buy_exchange}. Required: {cost:.2f}, Available: {exchange_balances[buy_exchange]['USD']:.2f}"
    if exchange_balances[sell_exchange]["BTC"] < trade_volume:
        return f"Insufficient BTC in {sell_exchange}. Required: {trade_volume:.4f}, Available: {exchange_balances[sell_exchange]['BTC']:.4f}"

    # 資産を更新
    exchange_balances[buy_exchange]["USD"] -= cost
    exchange_balances[buy_exchange]["BTC"] += trade_volume

    exchange_balances[sell_exchange]["BTC"] -= trade_volume
    exchange_balances[sell_exchange]["USD"] += revenue

    # 純利益を計算して返す
    net_profit = revenue - cost
    return net_profit

def calculate_costs_and_revenue(min_price, max_price, trade_volume):
    """
    売買に関するコストと収益を計算。
    """
    buy_slippage = min_price * SLIPPAGE_RATE * trade_volume
    sell_slippage = max_price * SLIPPAGE_RATE * trade_volume
    buy_fee = min_price * FEE_RATE * trade_volume
    sell_fee = max_price * FEE_RATE * trade_volume
    cost = min_price * trade_volume + buy_slippage + buy_fee
    revenue = max_price * trade_volume - sell_slippage - sell_fee
    threshold_diff = buy_slippage + sell_slippage + buy_fee + sell_fee
    return cost, revenue, threshold_diff

def rebalance_btc():
    """
    BTC残高を平準化する。
    """
    global exchange_balances
    low_balances = {ex: bal["BTC"] for ex, bal in exchange_balances.items() if bal["BTC"] < DEFAULT_TRADE_VOLUME}
    high_balances = {ex: bal["BTC"] for ex, bal in exchange_balances.items() if bal["BTC"] > DEFAULT_TRADE_VOLUME}

    for low_exchange, low_btc in low_balances.items():
        for high_exchange, high_btc in high_balances.items():
            if high_btc > DEFAULT_TRADE_VOLUME:
                transfer_amount = min(DEFAULT_TRADE_VOLUME - low_btc, high_btc - DEFAULT_TRADE_VOLUME)
                transfer_fee = transfer_amount * TRANSFER_FEE_RATE

                # 更新
                exchange_balances[high_exchange]["BTC"] -= transfer_amount
                exchange_balances[low_exchange]["BTC"] += transfer_amount - transfer_fee

                print(f"Rebalanced {transfer_amount:.4f} BTC from {high_exchange} to {low_exchange} (Fee: {transfer_fee:.4f} BTC)")
                break

def calculate_net_profit(min_price, max_price, trade_volume):
    """
    純利益としきい値差を計算。
    """
    cost, revenue, threshold_diff = calculate_costs_and_revenue(min_price, max_price, trade_volume)
    net_profit = revenue - cost
    return net_profit, threshold_diff

def simulate_trades(num_trades=NUM_TRADE, interval=INTERVAL):
    """
    売買をシミュレーション。
    """
    initial_assets = calculate_total_assets(fetch_prices())
    print(f"Initial Total Assets: ${initial_assets:,.2f}")
    total_net_profit = 0  # 累積純利益

    for i in range(num_trades):
        print(f"\nTrade {i + 1}/{num_trades}")
        prices = fetch_prices()
        valid_prices = {ex: p for ex, p in prices.items() if p is not None}
        if not valid_prices:
            print("No valid price data available. Skipping trade.")
            time.sleep(interval)
            continue

        max_price = max(valid_prices.values())
        min_price = min(valid_prices.values())
        max_exchange = max(valid_prices, key=valid_prices.get)
        min_exchange = min(valid_prices, key=valid_prices.get)

        trade_volume = min(DEFAULT_TRADE_VOLUME, exchange_balances[min_exchange]["USD"] / min_price, exchange_balances[max_exchange]["BTC"])

        net_profit, _ = calculate_net_profit(min_price, max_price, trade_volume)

        print(f"Buy at {min_exchange} (${min_price:,.2f})")
        print(f"Sell at {max_exchange} (${max_price:,.2f})")
        print(f"Net Profit: ${net_profit:.2f}")
        # print(f"Threshold Difference: ${threshold_diff:.2f}")

        if net_profit >= MIN_PROFIT_AMOUNT:
            execute_trade(min_exchange, max_exchange, trade_volume, min_price, max_price)
            total_net_profit += net_profit
            print(f"Trade executed successfully! Net Profit: ${net_profit:.2f}")
            print("Balances:")
            for exchange, balance in exchange_balances.items():
                print(f"{exchange}: {balance['USD']:.2f} USD, {balance['BTC']:.2f} BTC")
        else:
            print(f"Trade skipped due to low profitability. Net Profit: ${net_profit:.2f}, Required: ${MIN_PROFIT_AMOUNT:.2f}")

        # 平準化処理 (条件に応じて実行)
        if i % 5 == 0 or any(bal["BTC"] < DEFAULT_TRADE_VOLUME for bal in exchange_balances.values()):
            rebalance_btc()

        time.sleep(interval)

    final_assets = calculate_total_assets(fetch_prices())
    print(f"\nFinal Total Assets: ${final_assets:,.2f}")
    print(f"Asset Change: ${final_assets - initial_assets:,.2f}")
    print(f"Total Net Profit: ${total_net_profit:.2f}")

def calculate_total_assets(prices):
    """
    総資産を計算 (USD換算)。
    """
    total_usd = 0
    for exchange, balance in exchange_balances.items():
        total_usd += balance["USD"]
        price = prices.get(exchange)
        if price is None:
            price = 0
        total_usd += balance["BTC"] * price  # BTCをUSDに換算
    return total_usd

if __name__ == "__main__":
    simulate_trades()

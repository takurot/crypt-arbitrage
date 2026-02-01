import time
import requests
import polars as pl
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fallback for dev environment where library might not be installed
try:
    from rust_backtester import Backtester
except ImportError:
    print("Error: rust_backtester not installed. Please run setup.")
    sys.exit(1)

# Exchange Endpoints
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
    "Crypto.com": "https://api.crypto.com/v2/public/get-ticker?instrument_name=BTC_USDT"
}

# Defaults
DEFAULT_TRADE_VOLUME = 0.01
INITIAL_BALANCE_USD = 100000.0
INITIAL_BALANCE_BTC = 1.0

def _fetch_price(exchange, url):
    """Helper function for fetching a single exchange price."""
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        price = None
        
        # Parsers
        if exchange == "Bitfinex": price = data[6]
        elif exchange == "Binance": price = float(data["price"])
        elif exchange == "Coinbase": price = float(data["data"]["amount"])
        elif exchange == "Kraken": price = float(data["result"]["XXBTZUSD"]["c"][0])
        elif exchange == "Huobi": price = float(data["tick"]["close"])
        elif exchange == "OKX": price = float(data["data"][0]["last"])
        elif exchange == "KuCoin": price = float(data["data"]["price"])
        elif exchange == "Gate.io": price = float(data[0]["last"])
        elif exchange == "Bitstamp": price = float(data["last"])
        elif exchange == "Gemini": price = float(data["last"])
        elif exchange == "Crypto.com": price = float(data["result"]["data"][0]["a"])
        
        return exchange, price
    except Exception:
        return exchange, None

def fetch_prices_snapshot():
    """Retrieve BTC prices from all exchanges in parallel."""
    prices = {}
    with ThreadPoolExecutor(max_workers=len(EXCHANGE_APIS)) as executor:
        futures = [executor.submit(_fetch_price, ex, url) for ex, url in EXCHANGE_APIS.items()]
        for future in as_completed(futures):
            ex, price = future.result()
            if price is not None:
                prices[ex] = price
    return prices

class ArbitrageStrategy:
    """
    Arbitrage Strategy that can be configured with different parameters.
    """
    def __init__(self, name, min_profit, slippage_rate=0.001):
        self.name = name
        self.min_profit = min_profit
        self.slippage_rate = slippage_rate
        
        # State
        self.prices = {}
        self.balances = {ex: {"USD": INITIAL_BALANCE_USD, "BTC": INITIAL_BALANCE_BTC} for ex in EXCHANGE_APIS}
        self.total_profit = 0.0
        self.trade_count = 0
        self.trades = []

        # Internal tracking
        self.last_ts = 0

    def on_tick(self, tick, ctx):
        # tick is a PyTick object.
        exchange = getattr(tick, 'exchange_name', None)
        if not exchange: return

        # Price is scaled i64 (1e8)
        price = tick.price / 1e8 

        self.prices[exchange] = price
        self.check_arbitrage(exchange)

    def check_arbitrage(self, current_exchange):
        if not self.prices: return

        # Check against all other exchanges (Simple logic: find global Min/Max)
        valid_prices = {k: v for k, v in self.prices.items() if v is not None}
        if len(valid_prices) < 2: return

        max_price = max(valid_prices.values())
        min_price = min(valid_prices.values())
        max_exchange = max(valid_prices, key=valid_prices.get)
        min_exchange = min(valid_prices, key=valid_prices.get)

        # Only trade if the current update potentially triggers an arb involving this exchange
        if min_exchange == current_exchange or max_exchange == current_exchange:
             self.execute_trade(min_exchange, max_exchange, min_price, max_price)

    def execute_trade(self, buy_exchange, sell_exchange, min_price, max_price):
         trade_volume = DEFAULT_TRADE_VOLUME
         
         # Calculate costs with configured slippage
         cost = trade_volume * min_price * (1 + self.slippage_rate)
         revenue = trade_volume * max_price * (1 - self.slippage_rate)
         
         if self.balances[buy_exchange]["USD"] < cost: return
         if self.balances[sell_exchange]["BTC"] < trade_volume: return
             
         net_profit = revenue - cost
         if net_profit > self.min_profit:
             # Execute
             self.balances[buy_exchange]["USD"] -= cost
             self.balances[buy_exchange]["BTC"] += trade_volume
             self.balances[sell_exchange]["BTC"] -= trade_volume
             self.balances[sell_exchange]["USD"] += revenue
             
             self.total_profit += net_profit
             self.trade_count += 1
             
             self.trades.append({
                 "strategy": self.name,
                 "buy_ex": buy_exchange,
                 "sell_ex": sell_exchange,
                 "buy_price": min_price,
                 "sell_price": max_price,
                 "profit": net_profit
             })

def main():
    parser = argparse.ArgumentParser(description="Crypto Arbitrage Simulator (Live Data)")
    parser.add_argument("--duration", type=int, default=30, help="Duration to collect data in seconds")
    parser.add_argument("--interval", type=int, default=5, help="Interval between snapshots in seconds")
    args = parser.parse_args()

    print(f"=== Crypto Arbitrage Simulator ===")
    print(f"Collecting live data for {args.duration}s (interval: {args.interval}s)...")
    
    ticks = []
    iterations = max(1, args.duration // args.interval)
    
    start_time = time.time_ns()
    
    try:
        for i in range(iterations): 
            print(f"  [{i+1}/{iterations}] Fetching snapshot...", end="\r")
            prices = fetch_prices_snapshot()
            ts = time.time_ns()
            count = 0
            for ex, price in prices.items():
                ticks.append({
                    "ts_exchange": ts,
                    "price": int(price * 1e8), 
                    "qty": int(1.0 * 1e8),
                    "side": 1,
                    "exchange_name": ex
                })
                count += 1
            print(f"  [{i+1}/{iterations}] Fetched {count} prices.       ")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopping data collection...")

    if not ticks:
        print("No data collected.")
        return

    print(f"\nData Collection Complete. {len(ticks)} ticks.")
    
    # Prepare Data
    df = pl.DataFrame(ticks).sort("ts_exchange")
    data_map = {"BTCUSDT": df.lazy()}
    
    # Initialize Backtester
    tester = Backtester(data=data_map, python_mode='tick')
    
    # Strategies
    scenarios = [
        {"name": "Conservative", "min_profit": 30.0, "slippage": 0.002},
        {"name": "Balanced",     "min_profit": 10.0, "slippage": 0.001},
        {"name": "Aggressive",   "min_profit": 5.0,  "slippage": 0.0005},
    ]
    
    strategies = [ArbitrageStrategy(s["name"], s["min_profit"], s["slippage"]) for s in scenarios]
    
    print(f"\nRunning Parallel Backtest for {len(strategies)} strategies...")
    start_optim = time.perf_counter()
    
    tester.run_many(strategies)
    
    elapsed = time.perf_counter() - start_optim
    print(f"Backtest finished in {elapsed:.4f}s")
    
    # Report
    print("\n" + "="*80)
    print(f"{'STRATEGY':<15} | {'PROFIT ($)':<12} | {'TRADES':<8} | {'SLIPPAGE':<8}")
    print("-" * 80)
    
    results = []
    for s in strategies:
        print(f"{s.name:<15} | ${s.total_profit:<11.2f} | {s.trade_count:<8} | {s.slippage_rate*100}%")
        results.extend(s.trades)
        
    print("=" * 80)
    
    if results:
        print("\nTop 5 Most Profitable Trades:")
        trades_df = pl.DataFrame(results).sort("profit", descending=True).head(5)
        print(trades_df)

if __name__ == "__main__":
    main()

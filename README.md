# Cryptocurrency Arbitrage Simulator

This repository contains a Python script for simulating cryptocurrency arbitrage across multiple exchanges. It fetches real-time BTC prices, calculates potential profit margins considering fees and slippage, and simulates buy/sell transactions to demonstrate how arbitrage opportunities can be leveraged.

---

## Features

- **Real-time price fetching**: Connects to major exchange APIs to retrieve the latest BTC/USD prices.
- **Profit calculation**: Accounts for slippage, trading fees, and transfer fees to calculate net profit.
- **Trade simulation**: Simulates buy and sell trades between exchanges to evaluate potential profits.
- **Portfolio rebalancing**: Maintains balanced BTC holdings across exchanges to optimize arbitrage opportunities.
- **Customizable parameters**: Allows adjustment of fees, trade volume, and simulation settings.

---

## Supported Exchanges

The script supports the following exchanges:

- Bitfinex
- Binance
- Coinbase
- Kraken
- Huobi
- OKX
- KuCoin
- Gate.io
- Bitstamp
- Gemini
- Poloniex
- Crypto.com

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Required libraries: `requests`

### Clone the repository

```bash
git clone https://github.com/takurot/crypt-arbitrage.git
cd crypt-arbitrage
```

### Install dependencies

```bash
pip install requests
```

---

## Usage

### Run the script

To start the arbitrage simulation, run:

```bash
python crypt-arbitrage.py
```

### Adjust settings

You can modify the following parameters in the script to customize the simulation:

- `SLIPPAGE_RATE`: Slippage percentage (default: `0.001` or 0.1%)
- `FEE_RATE`: Trading fee percentage (default: `0.002` or 0.2%)
- `TRANSFER_FEE_RATE`: BTC transfer fee percentage (default: `0.001` or 0.1%)
- `DEFAULT_TRADE_VOLUME`: Default trade volume in BTC (default: `0.01`)
- `MIN_PROFIT_AMOUNT`: Minimum profit in USD to execute trades (default: `$10`)
- `INTERVAL`: Time interval between trades in seconds (default: `7.0`)
- `NUM_TRADE`: Number of trades to simulate (default: `50`)

---

## Example Output

```plaintext
Initial Total Assets: $100,000.00

Trade 1/50
Buy at Coinbase ($29,800.00)
Sell at Binance ($30,100.00)
Net Profit: $20.00
Trade executed successfully! Net Profit: $20.00
Balances:
Coinbase: 9,970.00 USD, 1.01 BTC
Binance: 30,120.00 USD, 0.99 BTC
...

Final Total Assets: $100,020.00
Asset Change: $20.00
Total Net Profit: $20.00
```

---

## Code Overview

### `fetch_prices()`

Fetches real-time BTC prices from all supported exchanges and returns a dictionary of prices.

### `calculate_net_profit(min_price, max_price, trade_volume)`

Calculates the net profit of a potential trade considering slippage and fees.

### `execute_trade(buy_exchange, sell_exchange, trade_volume, min_price, max_price)`

Simulates the execution of a trade and updates the portfolio balances.

### `rebalance_btc()`

Balances BTC holdings across exchanges to optimize trading opportunities.

### `simulate_trades()`

Runs the main simulation loop for the specified number of trades.

---

## Notes

- **Simulation only**: This script is for educational purposes and should not be used for actual trading without significant modifications and thorough testing.
- **Market volatility**: Cryptocurrency prices can fluctuate rapidly, affecting profitability and execution.
- **API limitations**: Ensure compliance with exchange API rate limits to avoid restrictions.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the functionality or add support for more exchanges.

---

## Acknowledgments

Thanks to the developers of the supported exchanges' APIs for providing access to market data.

---

Feel free to customize this README further to fit your repository!

# Optimization Platform & Crypto Arbitrage Simulator

This repository hosts a high-performance trading strategy optimization platform and a cryptocurrency arbitrage simulator. It leverages a Rust-based backtesting engine (`rust_backtester`) for speed and efficiency, making it suitable for High-Frequency Trading (HFT) strategy development.

## Features

- **High-Performance Backtesting**: Powered by a Rust engine (`rust_backtester`) linked via PyO3.
- **Optimization Platform**: 
    - **Monte Carlo & Grid Search**: Automatically tune strategy parameters.
    - **Parallel Execution**: Run hundreds of strategy instances in a single pass over streaming data.
    - **Streaming Data**: Efficiently handles large datasets (e.g., millions of tick rows) using PyArrow and Polars.
- **Arbitrage Tool**: 
    - Real-time price fetching from 10+ major exchanges (Binance, Kraken, Coinbase, etc.).
    - Parallel execution to minimize latency.
    - Live arbitrage simulation using the backtesting engine.

## Prerequisites

- **Python 3.11+**
- **Rust (Cargo)**: Required to build `rust_backtester`.
- **Dependencies**: `polars`, `pyarrow`, `numpy`, `requests`, `toml`

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/takurot/crypt-arbitrage.git
   cd crypt-arbitrage
   ```

2. **Set up the environment**:
   ```bash
   # Create a virtual environment
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Build & Install the Rust Backtester
   # (Ensure you are in the root directory where setup.py or similar logic exists, 
   #  or manually build the rust_backtester wheel)
   maturin develop --release
   ```

   *(Note: The project currently treats `rust_backtester` as a local companion library. Ensure it is accessible in your PYTHONPATH or installed via `maturin` / `pip`.)*

## Usage

### 1. Live Arbitrage Simulator

Run the simulator to fetch live prices and simulate arbitrage trades in real-time.

```bash
python crypt-arbitrage.py --duration 60 --interval 2
```

- `--duration`: Total simulation time in seconds.
- `--interval`: Interval between price snapshots in seconds.

### 2. Strategy Optimization Platform

The platform enables backtesting complex strategies (e.g., OFI Momentum, Bollinger Mean Reversion) using historical data defined in exact configuration files.

**Running an Experiment:**

```bash
python optimizer/cli.py run e2e_config.toml
```

**Configuration (`e2e_config.toml` example):**

```toml
experiment_name = "OFI_Optimization"
strategy = "OFI_Momentum"

[data]
path = "data/BTCUSDT.csv"

[optimization]
method = "monte_carlo"
samples = 50

[parameters.threshold]
type = "float"
min = 1.0
max = 10.0
```

**Output:**

The CLI will output a ranked table of strategy performance, including Return on Investment (ROI), Max Drawdown, and Sharpe Ratio.

```text
===============================================================================================
RANK | STRATEGY                  | ROI      | MAX DD   | SHARPE | TRADES
-----------------------------------------------------------------------------------------------
#1   | Config_6                  |  11.68% |   8.21% |   0.15 | 29781 
#2   | Config_2                  |   9.88% |   9.02% |   0.12 | 22991 
...
```

## Project Structure

- `crypt-arbitrage.py`: Entrypoint for live arbitrage simulation.
- `optimizer/`: The main Python package for the optimization platform.
  - `engine.py`: Core logic for parameter generation and simulation loops.
  - `strategy/`: Strategy definitions (`base.py`, `ofi.py`, `bollinger.py`).
  - `cli.py`: Command-line interface.
  - `reporting.py`: Result formatting and export.
- `rust_backtester/`: (External/Linked) Rust source code for the high-performance engine.

## License

MIT

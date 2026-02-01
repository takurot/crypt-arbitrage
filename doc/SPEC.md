# Optimization Platform Specification for Crypto-HFT

## 1. Overview
This application is a high-performance **Strategy Research & Optimization Platform** built on top of `crypto-rs-backtester`. Its primary goal is to allow quantitative researchers to rapidly explore, optimize, and validate HFT (High-Frequency Trading) algorithms against massive historical datasets (tick-level data).

**Core Value Proposition**: "Fail Fast, Iterate Faster." 
By enabling the evaluation of hundreds of strategy variations in seconds/minutes, the platform facilitates:
- **Regime Adaptation**: Dynamic parameter tuning based on recent market conditions.
- **Robustness Testing**: Identifying stable parameter clusters rather than overfitted outliers.
- **Multi-Asset Validation**: Verifying logic across BTC, ETH, SOL, etc.

### 1.1 Scope & Non-Goals
**In Scope (MVP)**
- Offline backtesting and parameter optimization on historical tick data.
- Deterministic, reproducible experiments with persistent artifacts.
- Single-machine execution with parallel workers when supported.

**Out of Scope (MVP)**
- Live trading, exchange connectivity, or order routing.
- Portfolio-level allocation across assets (beyond multi-asset backtests).
- Distributed cluster execution.

### 1.2 Design Principles
- **Deterministic**: Fixed seeds produce identical results.
- **Streaming-First**: Datasets must be processed in bounded memory.
- **Inspectable**: Every run saves config, seed, metrics, and artifacts.
- **Composable**: Strategy logic is modular, discoverable, and testable.

## 2. System Architecture

### 2.1 Tech Stack
- **Core Engine**: `crypto-rs-backtester` (Rust) for high-speed order matching and state management.
- **Data Layer**: `Polars` + `PyArrow` for zero-copy streaming of massive datasets (CSV/Parquet).
- **Driver/Analytics**: Python for strategy logic definition, experiment orchestration, and result visualization.

### 2.2 Components
1.  **Strategy Registry**: A modular interface to define strategy logic (Signals, Execution).
2.  **Optimizer**: Generates parameter sets (Grid, Random/Monte Carlo, Genetic).
3.  **Runner**: Orchestrates the `Backtester` with Arrow streams and strategy instances.
4.  **Reporter**: Generates leaderboards, equity curves, and persistence reports (JSON/Markdown).
5.  **Experiment Manager**: Persists configs, seeds, metadata, and artifacts per run.

## 3. Key Features

### 3.1 Strategy Management
- **Interface**: A standard `BaseStrategy` class requiring `on_tick(batch, ctx)` implementation.
- **Lifecycle Hooks**: Optional `on_start(ctx)` and `on_finish(ctx)` for setup/teardown.
- **Parametrization**: Strategies must define their hyperparameters (e.g., `window`, `threshold`) in a schema that the Optimizer can read.
- **Registry**: Auto-discovery of strategy classes in the `strategies/` directory.

### 3.2 Optimization Modes
1.  **Grid Search** (`grid`): Exhaustive search over defined ranges. Best for few parameters.
2.  **Monte Carlo** (`monte_carlo`): Sampling from distributions (Uniform, Log-Uniform). Best for high-dimensional spaces.
3.  **Walk-Forward** (`walk_forward`, planned): Optimize on Period A, validate on Period B.

### 3.3 Data Handling
- **Multi-Format**: Support for CSV (current) and Parquet (preferred for faster I/O).
- **Streaming**: Strict streaming (batch iterator) to keep memory usage low regardless of dataset size (10GB+).
- **Data Contract**:
  - Required: `ts` (int64 timestamp), `bid_px`, `ask_px`, `bid_sz`, `ask_sz` for L1 quote data.
  - Optional: trade prints (`trade_px`, `trade_sz`, `trade_side`) and metadata (`symbol`, `exchange`).
  - Ordering: rows must be time-ordered within each batch.
- **Multi-Asset**: Easy switching between `BTCUSDT`, `ETHUSDT`, etc. via config.

### 3.4 Metrics & Evaluation
- **Core**: Total PnL, average trade PnL, win rate, trade count.
- **Risk**: Max Drawdown, Sharpe (annualized), volatility.
- **Robustness**: Cluster stability metrics and walk-forward validation scores.

### 3.5 Reproducibility & Artifacts
Each experiment saves:
- Input config (YAML) and resolved parameter grid/seed.
- Code version (git commit hash) and data checksum (optional).
- Metrics summary and per-trial results in `reports/<experiment_id>/`.

## 4. User Interface (CLI)

The application is command-line driven for ease of automation and server deployment.

```bash
# Example: Optimize OFI strategy on ETHUSDT using Monte Carlo
pybun run opt.py run \
  --strategy ofi \
  --data data/ETHUSDT.csv \
  --method monte_carlo \
  --samples 100 \
  --out reports/experiment_001
```

## 5. Configuration (YAML)

Experiments can be defined in reproducible YAML files.

```yaml
experiment_name: "OFI_Scalping_ETH_2024"

data:
  path: "data/ETHUSDT.csv"
  format: "csv"
  schema: "l1_quote"

strategy: "OFI_Momentum"

optimization:
  method: "monte_carlo"
  samples: 500
  seed: 42
  parallel_workers: 1 # Number of concurrent Rust engines (if supported)

parameters:
  window:
    type: "int"
    distribution: "log_uniform"
    min: 10
    max: 5000
    
  threshold:
    type: "float"
    distribution: "log_uniform"
    min: 0.1
    max: 50.0

constraints:
  min_trades: 100 # Ignore results with too few trades
```

## 6. Development Roadmap

### Phase 1: Foundation (Current Status)
- [x] Basic Python Wrapper for strategies.
- [x] Arrow Streaming Data Loader.
- [x] Simple Monte Carlo logic (`optimize_ofi.py`).

### Phase 2: Application Structure
- [ ] Refactor `optimize_ofi.py` into a generic `Optimizer` class.
- [ ] Create `StrategyRegistry` and move strategies to separate files.
- [ ] Implement YAML configuration parser and schema validation.
- [ ] Standardize data schema validation for L1 quotes.

### Phase 3: Advanced Analytics
- [ ] Calculate Max Drawdown, Sharpe Ratio (annualized).
- [ ] Heatmap visualization of parameter clusters (Python `seaborn` or `matplotlib`).
- [ ] "Best of Cluster" logic to pick the most robust parameter set automatically.

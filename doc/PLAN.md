# Implementation Plan: Crypto Optimization Platform

This document outlines the step-by-step plan to transform the current script-based repository into a robust, extensible Optimization Platform as defined in [SPEC.md](./SPEC.md). Steps are organized into Pull Requests (PRs) to keep reviews manageable and to preserve incremental stability.

## Phase 0: Alignment & Contracts

### PR 0: Data + Results Contracts
**Goal**: Lock down the contracts that everything else builds on.
- [ ] Align method naming (`grid`, `monte_carlo`, `walk_forward`) across CLI/config.
- [ ] Define data schema enums (e.g., `l1_quote`, `trades`) and validation helpers.
- [ ] Define result schema (metrics + per-trial outputs) and artifact layout under `reports/<experiment_id>/`.
- [ ] Add a minimal fixture dataset and a validation test.

## Phase 1: Structural Foundation

### PR 1: Package Structure & Strategy Interface
**Goal**: Establish a proper Python package structure and define the contract for all future strategies.
- [ ] Create `optimizer/` package directory.
- [ ] Define `optimizer/strategy/base.py`:
    - Abstract `BaseStrategy` class.
    - Abstract method `on_tick(batch, ctx)`.
    - Optional hooks: `on_start(ctx)`, `on_finish(ctx)`.
    - Standard methods `get_stats()` and `set_params(params: dict)`.
- [ ] Create `optimizer/data/` module:
    - Move `create_arrow_iterator` logic to `optimizer/data/loader.py`.
    - Enforce data schema validation.
- [ ] Add unit tests for `BaseStrategy` and loader schema validation.

### PR 2: Configuration & Registry System
**Goal**: Enable YAML-based configuration and automatic strategy discovery.
- [ ] Implement `optimizer/config.py`:
    - Pydantic models for `ExperimentConfig`, `StrategyConfig`, `OptimizationConfig`, `DataConfig`.
    - YAML parser + validation errors that point to exact fields.
- [ ] Implement `optimizer/strategy/registry.py`:
    - Decorator-based registration (`@register_strategy("name")`).
    - Dynamic loading of strategy classes from `optimizer/strategies/`.

## Phase 2: Core Engine

### PR 3: The Generic Optimizer
**Goal**: Replace logic in `optimize_ofi.py` with a generic engine.
- [ ] Create `optimizer/engine.py`:
    - `Optimizer` class.
    - Method `generate_params(config)`: Handles `grid` and `monte_carlo` logic with seeding.
    - Method `run(config)`: Sets up the `Backtester`, creates strategy instances, and runs the stream.
- [ ] Implement `MultiStrategyWrapper` inside the engine to support single-pass execution of multiple persistent instances.
- [ ] Add deterministic-run tests (fixed seed => identical results).

### PR 4: Strategy Migration
**Goal**: Port existing scripts to the new architecture.
- [ ] Migrate `OFI_Momentum` to `optimizer/strategies/ofi.py` using the new Registry.
- [ ] Migrate `BollingerReversion` to `optimizer/strategies/bollinger.py`.
- [ ] Ensure `EmaCrossStrategy` is available as a baseline.
- [ ] Verify new implementations yield identical results to legacy scripts (fixture-based regression test).

## Phase 3: Application Interface

### PR 5: CLI & Reporting
**Goal**: User-facing command line tool with reproducible outputs.
- [ ] Implement `main.py` (CLI entrypoint) using `argparse` or `click`.
    - Subcommand `run`: Executes an experiment from YAML.
    - Subcommand `list`: Lists available strategies.
- [ ] Implement `optimizer/reporting.py`:
    - Generate Console Table (Rich/Tabulate).
    - Export results to `reports/<experiment_id>/results.json`.
    - Save resolved config and best parameter set to YAML.

## Phase 4: Advanced Features (Post-MVP)

### PR 6: Analytics & Robustness
**Goal**: Deeper insight into strategy performance.
- [ ] Search for stable clusters (not just single best param).
- [ ] Add Max Drawdown and Sharpe Ratio to `BaseStrategy` stats.
- [ ] Add trade logging option (CSV export of all trades).

---

## Execution Checklist

- [ ] **Phase 0**: Alignment
    - [ ] PR 0
- [ ] **Phase 1**: Structure
    - [ ] PR 1
    - [ ] PR 2
- [ ] **Phase 2**: Engine
    - [ ] PR 3
    - [ ] PR 4
- [ ] **Phase 3**: Interface
    - [ ] PR 5

import time
import random
import numpy as np
import pyarrow as pa
import polars as pl
from typing import List, Dict, Any, Type, Optional

# Backtester import (with graceful fallback for development)
try:
    from rust_backtester import Backtester, BacktestResult
except ImportError:
    Backtester = None
    BacktestResult = None

from optimizer.config import ExperimentConfig, ParameterSpace, DataConfig
from optimizer.strategy.registry import StrategyRegistry
from optimizer.data.loader import create_arrow_iterator, FIXED_POINT

class MultiStrategyWrapper:
    """Wraps multiple strategy instances to run in a single pass."""
    def __init__(self, strategies: List[Any]):
        self.strategies = strategies
        
    def on_ticks(self, batch, ctx):
        # Extract numpy arrays ONCE per batch for performance
        prices = batch["price"].to_numpy().astype(np.float64) / FIXED_POINT
        qtys = batch["qty"].to_numpy().astype(np.float64) / FIXED_POINT
        sides = batch["side"].to_numpy().astype(np.int8)
        
        # Pass to all strategies
        # Optimizing this loop is critical for performance
        for s in self.strategies:
            s.on_ticks(prices, qtys, sides, ctx)

class Optimizer:
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.strategies: List[Any] = []
        
    def generate_params(self) -> List[Dict[str, Any]]:
        """Generate a list of parameter dictionaries based on config."""
        method = self.config.optimization.method
        samples = self.config.optimization.samples
        
        # Seed RNG
        seed = self.config.optimization.seed
        rng = random.Random(seed) if seed is not None else random.Random()
        
        param_sets = []
        
        # Grid Search logic (Simplified: just random sampling if not implemented full grid yet)
        # Note: True grid search requires Cartesian product logic. 
        # For now, let's assume 'grid' behaves like 'monte_carlo' if values aren't specified, 
        # or we follow the spec.
        
        # If method is 'monte_carlo' or 'grid' (treated as random for continuous ranges in this MVP)
        for _ in range(samples):
            params = {}
            for name, space in self.config.parameters.items():
                if space.values:
                    # Categorical / Discrete choice
                    params[name] = rng.choice(space.values)
                elif space.distribution == "uniform":
                    params[name] = rng.uniform(space.min, space.max)
                    if space.type == "int":
                        params[name] = int(params[name])
                elif space.distribution == "log_uniform":
                    # log-uniform sampling: 10^uniform(log10(min), log10(max))
                    import math
                    log_min = math.log10(space.min)
                    log_max = math.log10(space.max)
                    val = 10 ** rng.uniform(log_min, log_max)
                    params[name] = int(val) if space.type == "int" else float(val)
                elif space.distribution == "fixed":
                   params[name] = space.values[0] if space.values else space.min

            param_sets.append(params)
            
        return param_sets

    def run(self, verbose: bool = True):
        """Execute the optimization."""
        if Backtester is None:
            raise ImportError("rust_backtester library is required to run optimization.")
            
        # 1. Generate Parameters
        param_sets = self.generate_params()
        if verbose:
            print(f"🎲 Generated {len(param_sets)} parameter sets using {self.config.optimization.method}")
            
        # 2. Instantiate Strategies
        StrategyCls = StrategyRegistry.get(self.config.strategy)
        if not StrategyCls:
             # Try loading dynamically if module provided? 
             # For now assume registry is pre-filled or handled by CLI
             raise ValueError(f"Strategy '{self.config.strategy}' not found in registry.")
             
        self.strategies = []
        for i, params in enumerate(param_sets):
            strat = StrategyCls(name=f"Config_{i}")
            strat.set_params(params)
            self.strategies.append(strat)
            
        if verbose:
            print(f"🚀 Initialized {len(self.strategies)} strategy instances.")
            
        # 3. Setup Backtester
        # Dummy data for initialization
        dummy_df = pl.DataFrame({"ts_exchange":[0],"price":[0],"qty":[0],"side":[1],"symbol_id":[0]}).lazy()
        
        bt = Backtester(
            data={"BTCUSDT": dummy_df}, 
            python_mode="batch", 
            batch_ms=1000 
        )
        
        # 4. Stream Data
        # Creating wrapper
        wrapper = MultiStrategyWrapper(self.strategies)
        
        iterator = create_arrow_iterator(self.config.data.path)
        execution_schema = pa.schema([
            ("ts_exchange", pa.int64()), ("price", pa.int64()),
            ("qty", pa.int64()), ("side", pa.int8()), ("symbol_id", pa.int64()), 
        ])
        rb_reader = pa.RecordBatchReader.from_batches(execution_schema, iterator)
        
        start_time = time.perf_counter()
        
        # Call on_start hooks
        for s in self.strategies:
            s.on_start(None) # Context not fully available in simple mode yet
            
        bt.run_arrow(stream=rb_reader, strategy=wrapper)
        
        # Call on_finish hooks
        for s in self.strategies:
            s.on_finish(None)
            
        duration = time.perf_counter() - start_time
        
        if verbose:
            print(f"✅ Simulation Complete in {duration:.2f}s")
            
        # 5. Collect Results
        results = [s.get_stats() for s in self.strategies]
        return results

import unittest
from dataclasses import dataclass
from typing import Dict, Any

from optimizer.config import ExperimentConfig, OptimizationConfig, ParameterSpace, DataConfig
from optimizer.engine import Optimizer

# Mock Strategy for testing
from optimizer.strategy.base import BaseStrategy
from optimizer.strategy.registry import register_strategy

@register_strategy("MockTestStrategy")
class MockTestStrategy(BaseStrategy):
    def on_tick(self, batch, ctx):
        pass
    def get_stats(self):
        return {"roi": 1.0, "trades": 10, "params": self.params}

class TestOptimizer(unittest.TestCase):
    def setUp(self):
        self.config = ExperimentConfig(
            experiment_name="TestExp",
            data=DataConfig(path="dummy.csv"),
            strategy="MockTestStrategy",
            optimization=OptimizationConfig(method="grid", samples=5),
            parameters={
                "p1": ParameterSpace(type="int", min=1, max=10, distribution="uniform"),
                "p2": ParameterSpace(type="float", min=0.0, max=1.0, distribution="uniform")
            }
        )
        self.optimizer = Optimizer(self.config)

    def test_generate_params_grid(self):
        # Grid search logic check (simplistic check for now)
        self.config.optimization.method = "grid"
        # Grid not meant for uniform range usually, but ensuring it generates something
        params = self.optimizer.generate_params()
        self.assertTrue(len(params) > 0)
        self.assertIn("p1", params[0])

    def test_generate_params_monte_carlo(self):
        self.config.optimization.method = "monte_carlo"
        self.config.optimization.samples = 20
        params = self.optimizer.generate_params()
        self.assertEqual(len(params), 20)
        
        # Check constraints
        for p in params:
            self.assertTrue(1 <= p["p1"] <= 10)
            self.assertTrue(0.0 <= p["p2"] <= 1.0)
            
    def test_seeding_reproducibility(self):
        self.config.optimization.seed = 42
        params1 = self.optimizer.generate_params()
        
        self.optimizer = Optimizer(self.config) # Re-init
        params2 = self.optimizer.generate_params()
        
        self.assertEqual(params1, params2)

if __name__ == "__main__":
    unittest.main()

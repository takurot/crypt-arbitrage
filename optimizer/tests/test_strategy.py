import unittest
from optimizer.strategy.base import BaseStrategy
from optimizer.strategy.registry import StrategyRegistry, register_strategy

class TestStrategy(BaseStrategy):
    def on_tick(self, batch, ctx):
        pass
    def get_stats(self):
        return {"test": True}

class TestFoundation(unittest.TestCase):
    def test_base_strategy_instantiation(self):
        # Abstract class shouldn't be instantiated directly, but concrete one should
        strat = TestStrategy("Test")
        self.assertEqual(strat.name, "Test")
        self.assertEqual(strat.get_stats(), {"test": True})
        
    def test_params_update(self):
        strat = TestStrategy("Test")
        strat.set_params({"a": 1})
        self.assertEqual(strat.params["a"], 1)

    def test_registry(self):
        @register_strategy("MockStrategy")
        class MockStrategy(BaseStrategy):
            def on_tick(self, batch, ctx): pass
            def get_stats(self): return {}

        self.assertIn("MockStrategy", StrategyRegistry.list_strategies())
        cls = StrategyRegistry.get("MockStrategy")
        self.assertEqual(cls.__name__, "MockStrategy")

if __name__ == '__main__':
    unittest.main()

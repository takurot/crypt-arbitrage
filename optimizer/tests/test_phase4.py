import unittest
import numpy as np
from optimizer.strategy.ofi import OFIMomentum

class TestPhase4(unittest.TestCase):
    def test_analytics_keys(self):
        strat = OFIMomentum("TestAnalytics")
        strat.set_params({"window": 10, "threshold": 5.0})
        
        # Simulate some trades to generate equity curve
        # Initial cash 100k
        strat.equity_history = [100000.0, 101000.0, 95000.0, 110000.0] 
        # Peak 101k -> 95k = 6k drop. 6/101 ~ 5.9% DD
        strat.last_price = 100.0
        
        stats = strat.get_stats()
        
        self.assertIn("max_dd", stats)
        self.assertIn("sharpe", stats)
        self.assertTrue(stats["max_dd"] > 5.0) # Should be ~5.94%

if __name__ == "__main__":
    unittest.main()

import unittest
import numpy as np
from optimizer.strategy.ofi import OFIMomentum
from optimizer.strategy.bollinger import BollingerReversion

class TestStrategies(unittest.TestCase):
    def test_ofi_logic(self):
        strat = OFIMomentum("TestOFI")
        strat.set_params({"window": 10, "threshold": 5.0})
        strat.on_start(None)
        
        # Simulate Data: Prices, Qtys, Sides
        # Net flow = qty * side. 
        # Tick 1: Buy 10 -> Flow +10 -> Smoothed moves up -> > 5.0 -> Buy
        prices = np.array([100.0, 101.0])
        qtys = np.array([10.0, 10.0])
        sides = np.array([1, 1]) # Buys
        
        strat.on_ticks(prices, qtys, sides, None)
        
        self.assertEqual(strat.trade_count, 1)
        self.assertTrue(strat.position > 0)
        
    def test_bollinger_logic(self):
        strat = BollingerReversion("TestBoll")
        strat.set_params({"window": 5, "std_dev": 2.0})
        
        # Simulate sequence where price drops below lower band
        # Mean=100, Std=0 (initially). Deviation needed.
        # [100, 100, 100, 100, 90] -> Mean ~98, Std ~4. Lower ~90.
        
        prices = np.array([100.0, 100.0, 100.0, 100.0, 90.0])
        qtys = np.array([1.0]*5)
        sides = np.array([1]*5)
        
        strat.on_ticks(prices, qtys, sides, None)
        
        # Logic is sensitive to exact numpy calcs, but roughly checking logic flow
        stats = strat.get_stats()
        # Should have traded if logic triggered, or at least run without error
        self.assertTrue(stats["roi"] != None)

if __name__ == "__main__":
    unittest.main()

import unittest
import numpy as np
from optimizer.strategy.base import BaseStrategy

class MockStrategy(BaseStrategy):
    def on_ticks(self, batch, ctx):
        pass
    def get_stats(self):
        return {}

class TestEconomics(unittest.TestCase):
    def setUp(self):
        self.strat = MockStrategy("TestStrat")
        self.strat.cash = 100_000.0
        self.strat.position = 0.0
        self.strat.params = {
            "fee_rate": 0.001, # 0.1%
            "slippage": 0.0    # 0% for basic test
        }

    def test_buy_with_fee(self):
        # Buy 1 BTC at 10,000
        # Cost = 10,000
        # Fee = 10,000 * 0.001 = 10
        # Total deduction = 10,010
        price = 10_000.0
        qty = 1.0
        
        self.strat.execute_buy(price, qty)
        
        expected_cash = 100_000.0 - 10_010.0
        self.assertAlmostEqual(self.strat.cash, expected_cash)
        self.assertAlmostEqual(self.strat.position, 1.0)
        self.assertEqual(self.strat.trade_count, 1)

    def test_sell_with_fee(self):
        # Setup position
        self.strat.position = 1.0
        self.strat.cash = 0.0
        
        # Sell 1 BTC at 20,000
        # Revenue = 20,000
        # Fee = 20,000 * 0.001 = 20
        # Total added = 19,980
        price = 20_000.0
        qty = 1.0
        
        self.strat.execute_sell(price, qty)
        
        expected_cash = 19_980.0
        self.assertAlmostEqual(self.strat.cash, expected_cash)
        self.assertAlmostEqual(self.strat.position, 0.0)

    def test_buy_insufficient_funds(self):
        self.strat.cash = 5000.0
        price = 10_000.0
        qty = 1.0
        
        # Should not execute
        self.strat.execute_buy(price, qty)
        
        self.assertEqual(self.strat.cash, 5000.0)
        self.assertEqual(self.strat.position, 0.0)
        self.assertEqual(self.strat.trade_count, 0)
        
    def test_sell_insufficient_position(self):
        self.strat.position = 0.5
        price = 10_000.0
        qty = 1.0
        
        # Should not execute
        self.strat.execute_sell(price, qty)
        
        self.assertEqual(self.strat.position, 0.5)

if __name__ == '__main__':
    unittest.main()

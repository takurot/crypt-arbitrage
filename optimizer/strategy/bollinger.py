import numpy as np
from optimizer.strategy.base import BaseStrategy
from optimizer.strategy.registry import register_strategy

@register_strategy("BollingerReversion")
class BollingerReversion(BaseStrategy):
    """
    Bollinger Bands Mean Reversion Strategy.
    """
    def __init__(self, name: str = "Bollinger"):
        super().__init__(name)
        self.params.update({
            "window": 200,
            "std_dev": 2.0
        })
        
        self.last_price = 0.0

    def on_start(self, ctx):
        pass

    def on_ticks(self, prices, qtys, sides, ctx):
        self.last_price = prices[-1]
        
        # Simple Logic: Compute rolling stats on the *current batch*
        window = int(self.params["window"])
        k = self.params.get("std_dev", 2.0)
        
        if len(prices) < window:
            return
            
        recent = prices[-window:]
        mean = np.mean(recent)
        std = np.std(recent)
        
        upper = mean + (k * std)
        lower = mean - (k * std)
        current = prices[-1]
        
        trade_qty = 1.0
        
        if current < lower and self.position <= 0:
            self.execute_buy(current, trade_qty)
        elif current > upper and self.position >= 0:
            self.execute_sell(current, trade_qty)
            
    def get_stats(self):
        # Use simple stats for now, can implement equity tracking like OFI if needed
        equity = self.cash + (self.position * self.last_price)
        pnl = equity - self.initial_value
        return {
            "name": self.name,
            "window": self.params["window"],
            "std_dev": self.params["std_dev"],
            "roi": (pnl/self.initial_value)*100,
            "trades": self.trade_count
        }

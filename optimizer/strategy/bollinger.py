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
        self.params = {
            "window": 200,
            "std_dev": 2.0
        }
        
        self.position = 0.0
        self.cash = 100_000.0
        self.initial_value = 100_000.0
        self.trade_count = 0
        
        # Rolling buffer state could be handled better in production
        # For this implementation, we calculate on batch if possible, or maintain simple state
        # Since 'batch' logic in Python for 5M rows is usually "process whole chunk", 
        # we might need a persistent buffer if batch size < window.
        # But for high performance vectorization, we often assume batch >> window.
        self.last_price = 0.0

    def on_start(self, ctx):
        pass

    def on_ticks(self, prices, qtys, sides, ctx):
        self.last_price = prices[-1]
        
        # Simple Logic: Compute rolling stats on the *current batch*
        # Limitation: This resets every batch, which is imperfect for streaming but OK for high-throughput MVP
        # IF the batch size is large enough (e.g. 100k).
        
        window = int(self.params["window"])
        k = self.params["std_dev"]
        
        # We need at least 'window' size history. 
        # For simplicity in this ported version, we use the batch average if batch < window (warmup)
        # or just the last 'window' prices of the batch
        
        if len(prices) < window:
            return
            
        # Recent slice
        recent = prices[-window:]
        mean = np.mean(recent)
        std = np.std(recent)
        
        upper = mean + (k * std)
        lower = mean - (k * std)
        current = prices[-1]
        
        trade_qty = 1.0
        
        if current < lower and self.position <= 0:
            self._buy(current, trade_qty)
        elif current > upper and self.position >= 0:
            self._sell(current, trade_qty)
            
    def _buy(self, price, qty):
        cost = price * qty
        if self.cash >= cost:
            self.cash -= cost
            self.position += qty
            self.trade_count += 1
            
    def _sell(self, price, qty):
        revenue = price * qty
        if self.position >= qty:
            self.position -= qty
            self.cash += revenue
            self.trade_count += 1

    def get_stats(self):
        equity = self.cash + (self.position * self.last_price)
        pnl = equity - self.initial_value
        return {
            "name": self.name,
            "window": self.params["window"],
            "std_dev": self.params["std_dev"],
            "roi": (pnl/self.initial_value)*100,
            "trades": self.trade_count
        }

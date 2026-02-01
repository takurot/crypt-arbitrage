import numpy as np
from optimizer.strategy.base import BaseStrategy
from optimizer.strategy.registry import register_strategy

@register_strategy("OFI_Momentum")
class OFIMomentum(BaseStrategy):
    """
    Order Flow Imbalance (OFI) Momentum Strategy.
    
    Params:
        window (int): Decay window for OFI metric.
        threshold (float): Signal threshold.
    """
    def __init__(self, name: str = "OFI"):
        super().__init__(name)
        # Defaults
        self.params = {
            "window": 100,
            "threshold": 5.0
        }
        
        # State
        self.ofi_sum = 0.0
        self.decay = 0.0
        self.position = 0.0
        self.cash = 100_000.0
        self.initial_value = 100_000.0
        self.trade_count = 0
        self.last_price = 0.0

    def on_start(self, ctx):
        w = int(self.params["window"])
        if w < 2:
            self.decay = 0.0
        else:
            self.decay = 1.0 - (1.0 / w)
            
    def execute_buy(self, price, qty):
        cost = price * qty
        if self.cash >= cost:
            self.cash -= cost
            self.position += qty
            self.trade_count += 1
            
    def execute_sell(self, price, qty):
        revenue = price * qty
        if self.position >= qty:
            self.position -= qty
            self.cash += revenue
            self.trade_count += 1

    def on_ticks(self, prices, qtys, sides, ctx):
        # prices, qtys, sides are numpy arrays (float, float, int)
        self.last_price = prices[-1]

        # Net Flow for this batch

        # Net Flow for this batch
        net_flow = np.sum(qtys * sides)
        
        # Update Smoothed OFI
        self.ofi_sum = (self.ofi_sum * self.decay) + net_flow
        
        trade_qty = 1.0
        threshold = self.params["threshold"]
        
        # Momentum Logic
        if self.ofi_sum > threshold and self.position <= 0:
            self.execute_buy(self.last_price, trade_qty)
            
        elif self.ofi_sum < -threshold and self.position >= 0:
            self.execute_sell(self.last_price, trade_qty)
            
        # Track Equity for Analytics
        current_equity = self.cash + (self.position * self.last_price)
        self.equity_history.append(current_equity)

    def get_stats(self):
        equity = self.cash + (self.position * self.last_price)
        pnl = equity - self.initial_value
        max_dd = self.calculate_drawdown(self.equity_history)
        
        # Simple Sharpe (assuming per-batch returns)
        # In real world, need time-based returns.
        returns = np.diff(self.equity_history) / self.equity_history[:-1] if len(self.equity_history) > 1 else []
        sharpe = np.mean(returns) / np.std(returns) if len(returns) > 0 and np.std(returns) > 0 else 0.0
        
        return {
            "name": self.name,
            "window": self.params["window"],
            "threshold": self.params["threshold"],
            "pnl": pnl,
            "roi": (pnl/self.initial_value)*100,
            "max_dd": max_dd,
            "sharpe": sharpe * np.sqrt(252*1440), # Annualized approximation (very rough)
            "trades": self.trade_count
        }

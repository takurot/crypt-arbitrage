from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Strategies must implement:
      - on_start(ctx): Setup (optional)
      - on_tick(batch, ctx): Core logic
      - on_finish(ctx): Teardown (optional)
      - get_stats(): Return performance metrics
      - set_params(params): Update hyperparameters
    """
    
    def __init__(self, name: str = "Strategy"):
        self.name = name
        self.params: Dict[str, Any] = {"fee_rate": 0.0, "slippage": 0.0}
        self.trade_count = 0
        self.cash = 100_000.0
        self.position = 0.0
        self.initial_value = 100_000.0
        self.equity_history: List[float] = [] # Track equity per batch for analytics
        
    def on_start(self, ctx: Any) -> None:
        """Called before the backtest starts."""
        pass
        
    def execute_buy(self, price: float, qty: float) -> bool:
        """
        Execute a buy order with fee deduction.
        Returns True if successful, False if insufficient funds.
        """
        fee_rate = self.params.get("fee_rate", 0.0)
        cost = price * qty
        fee = cost * fee_rate
        total_cost = cost + fee
        
        if self.cash >= total_cost:
            self.cash -= total_cost
            self.position += qty
            self.trade_count += 1
            return True
        return False

    def execute_sell(self, price: float, qty: float) -> bool:
        """
        Execute a sell order with fee deduction.
        Returns True if successful, False if insufficient position.
        """
        fee_rate = self.params.get("fee_rate", 0.0)
        revenue = price * qty
        fee = revenue * fee_rate
        net_revenue = revenue - fee
        
        if self.position >= qty:
            self.position -= qty
            self.cash += net_revenue
            self.trade_count += 1
            return True
        return False
        
    @abstractmethod
    def on_ticks(self, batch: Any, ctx: Any) -> None:
        """
        Called on every data batch.
        
        Args:
            batch: An Arrow RecordBatch or dictionary of numpy arrays.
            ctx: The execution context (provides submit_order, etc).
        """
        pass
        
    def calculate_drawdown(self, equity_curve: list) -> float:
        """Helper to calculate Max Drawdown %."""
        if not equity_curve: return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for val in equity_curve:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_dd:
                max_dd = dd
        return max_dd * 100.0
        
    def on_finish(self, ctx: Any) -> None:
        """Called after the backtest ends."""
        pass
        
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Return a dictionary of performance statistics."""
        pass
        
    def set_params(self, params: Dict[str, Any]) -> None:
        """Update strategy hyperparameters."""
        self.params.update(params)
        # Allow subclasses to react to param changes if needed

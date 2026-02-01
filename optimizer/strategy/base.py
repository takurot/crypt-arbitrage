from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

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
        self.params: Dict[str, Any] = {}
        
    def on_start(self, ctx: Any) -> None:
        """Called before the backtest starts."""
        pass
        
    @abstractmethod
    def on_tick(self, batch: Any, ctx: Any) -> None:
        """
        Called on every data batch.
        
        Args:
            batch: An Arrow RecordBatch or dictionary of numpy arrays.
            ctx: The execution context (provides submit_order, etc).
        """
        pass
        
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

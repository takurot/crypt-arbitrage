from typing import Dict, Type, Optional
from optimizer.strategy.base import BaseStrategy

class StrategyRegistry:
    _strategies: Dict[str, Type[BaseStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a strategy class."""
        def decorator(strategy_cls: Type[BaseStrategy]):
            cls._strategies[name] = strategy_cls
            return strategy_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseStrategy]]:
        """Get a strategy class by name."""
        return cls._strategies.get(name)

    @classmethod
    def load_strategy_from_module(cls, module_path: str):
        """Dynamically import a module to trigger registration."""
        import importlib
        try:
            importlib.import_module(module_path)
            # print(f"Loaded strategy module: {module_path}")
        except ImportError as e:
            print(f"Failed to load strategy module {module_path}: {e}")

    @classmethod
    def list_strategies(cls):
        """List all registered strategy names."""
        return list(cls._strategies.keys())

def discover_strategies():
    """Import all modules in optimizer.strategy to trigger registration."""
    import pkgutil
    import importlib
    import os
    
    # Get the directory of this package
    package_dir = os.path.dirname(__file__)
    
    # Scan for modules
    for _, name, _ in pkgutil.iter_modules([package_dir]):
        if name == "base" or name == "registry":
            continue
        try:
            importlib.import_module(f"optimizer.strategy.{name}")
        except Exception as e:
            print(f"Failed to auto-discover strategy {name}: {e}")

# Alias for ease of use
register_strategy = StrategyRegistry.register

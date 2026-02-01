from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import tomllib

@dataclass
class DataConfig:
    path: str
    format: str = "csv"
    schema_type: str = "l1_quote"

@dataclass
class ParameterSpace:
    type: str = "int" # int, float
    distribution: str = "uniform" # uniform, log_uniform, fixed
    min: Optional[float] = None
    max: Optional[float] = None
    values: Optional[List[Any]] = None

@dataclass
class OptimizationConfig:
    method: str = "grid"
    samples: int = 10
    seed: Optional[int] = None
    parallel_workers: int = 1

@dataclass
class ExperimentConfig:
    experiment_name: str
    data: DataConfig
    strategy: str
    optimization: OptimizationConfig
    parameters: Dict[str, ParameterSpace]
    constraints: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: str) -> 'ExperimentConfig':
        with open(path, "rb") as f:
            data = tomllib.load(f)
        
        # Manual parsing/mapping since we don't have Pydantic
        # This is accurate enough for MVP
        
        d_conf = DataConfig(**data.get("data", {}))
        
        opt_data = data.get("optimization", {})
        opt_conf = OptimizationConfig(**opt_data)
        
        params_map = {}
        for k, v in data.get("parameters", {}).items():
            params_map[k] = ParameterSpace(**v)
            
        return cls(
            experiment_name=data.get("experiment_name", "unnamed"),
            data=d_conf,
            strategy=data.get("strategy"),
            optimization=opt_conf,
            parameters=params_map,
            constraints=data.get("constraints", {})
        )

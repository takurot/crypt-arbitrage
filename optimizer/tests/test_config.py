import unittest
import os
import tempfile
from optimizer.config import ExperimentConfig

TOML_CONTENT = """
experiment_name = "TestExp"
strategy = "TestStrategy"

[data]
path = "data/test.csv"
format = "csv"

[optimization]
method = "monte_carlo"
samples = 50
seed = 42

[parameters]
    [parameters.window]
    type = "int"
    distribution = "log_uniform"
    min = 10.0
    max = 500.0

    [parameters.threshold]
    type = "float"
    distribution = "uniform"
    min = 0.5
    max = 5.0
"""

class TestConfig(unittest.TestCase):
    def test_load_toml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix=".toml", delete=False) as tmp:
            tmp.write(TOML_CONTENT)
            tmp_path = tmp.name
            
        try:
            config = ExperimentConfig.from_toml(tmp_path)
            self.assertEqual(config.experiment_name, "TestExp")
            self.assertEqual(config.strategy, "TestStrategy")
            self.assertEqual(config.optimization.samples, 50)
            self.assertEqual(config.parameters["window"].max, 500.0)
        finally:
            os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()

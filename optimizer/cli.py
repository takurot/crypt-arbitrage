import argparse
import sys
import os
from optimizer.config import ExperimentConfig
from optimizer.engine import Optimizer
from optimizer.reporting import Reporter
from optimizer.strategy.registry import discover_strategies

def main():
    # Auto-load strategies
    discover_strategies()

    parser = argparse.ArgumentParser(description="Crypto Strategy Optimization Platform")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Run Command
    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("config", help="Path to TOML configuration file")
    
    # Check args
    args = parser.parse_args()
    
    if args.command == "run":
        if not os.path.exists(args.config):
            print(f"Error: Config file '{args.config}' not found.")
            sys.exit(1)
            
        print(f"⚙️  Loading configuration from {args.config}...")
        try:
            config = ExperimentConfig.from_toml(args.config)
        except Exception as e:
            print(f"Error parsing config: {e}")
            sys.exit(1)
            
        print(f"🔬 Starting Experiment: {config.experiment_name}")
        
        # Initialize Optimizer
        opt = Optimizer(config)
        
        # Run
        try:
            results = opt.run(verbose=True)
        except Exception as e:
            print(f"Execution failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
        # Report
        reporter = Reporter(config.experiment_name)
        reporter.print_console(results)
        reporter.save_json(results)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

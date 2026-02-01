import json
import os
from typing import List, Dict, Any
from datetime import datetime

class Reporter:
    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
        self.report_dir = f"reports/{experiment_id}"
        os.makedirs(self.report_dir, exist_ok=True)

    def print_console(self, results: List[Dict[str, Any]]):
        """Print a nice table to console."""
        if not results:
            print("No results to report.")
            return

        # Sort by ROI descending
        sorted_res = sorted(results, key=lambda x: x.get('roi', -999), reverse=True)
        top_5 = sorted_res[:15]

        print("\n" + "="*95)
        print(f"{'RANK':<4} | {'STRATEGY':<25} | {'ROI':<8} | {'MAX DD':<8} | {'SHARPE':<6} | {'TRADES':<6}")
        print("-" * 95)
        
        for i, res in enumerate(top_5):
            roi = res.get('roi', 0.0)
            trades = res.get('trades', 0)
            max_dd = res.get('max_dd', 0.0)
            sharpe = res.get('sharpe', 0.0)
            
            name = res.get('name', 'Unknown')
            if len(name) > 25: name = name[:22] + "..."
            
            print(f"#{i+1:<3} | {name:<25} | {roi:>6.2f}% | {max_dd:>6.2f}% | {sharpe:>6.2f} | {trades:<6}")
        print("=" * 80)
        
        if sorted_res:
            best = sorted_res[0]
            print(f"\n🏆 WINNER: {best.get('name')} -> ROI: {best.get('roi', 0):.2f}%")

    def save_json(self, results: List[Dict[str, Any]]):
        path = os.path.join(self.report_dir, "results.json")
        data = {
            "experiment_id": self.experiment_id,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"📄 Saved results to {path}")

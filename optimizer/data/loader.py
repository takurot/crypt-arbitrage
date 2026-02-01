import os
import polars as pl
import pyarrow as pa
from typing import Iterator

# Constant for scaled integers (price * 1e8)
FIXED_POINT = 100_000_000

def create_arrow_iterator(csv_path: str, batch_size: int = 100_000) -> Iterator[pa.RecordBatch]:
    """
    Stream a CSV file as Arrow RecordBatches with the specific schema required by the Rust engine.
    
    Schema:
        - ts_exchange (int64): Timestamp in nanoseconds (or ms depending on engine config)
        - price (int64): Scaled price (val * 1e8)
        - qty (int64): Scaled quantity (val * 1e8)
        - side (int8): 1 (Buy/TakerBuy) or -1 (Sell/TakerSell)
        - symbol_id (int64): 0 for single asset
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
        
    print(f"📂 Streaming data from {csv_path}...")
    reader = pl.read_csv_batched(csv_path, batch_size=batch_size)
    
    batch_count = 0
    total_processed = 0
    
    while True:
        batches = reader.next_batches(1)
        if not batches:
            break
        
        chunk_df = batches[0]
        rows = len(chunk_df)
        total_processed += rows
        batch_count += 1
        
        # Transformation Logic
        # Assumes standard header with time, price, quantity, isbuyermaker
        # Adjust logic if schema differs
        
        exprs = [
            (pl.col("time") * 1_000_000).cast(pl.Int64).alias("ts_exchange"), # ms timestamp -> ns? Check engine expectation. 
            # Previous scripts used * 1_000_000 on 'time'. If 'time' is ms, this makes it ns.
            
            (pl.col("price") * FIXED_POINT).cast(pl.Int64).alias("price"),
            (pl.col("quantity") * FIXED_POINT).cast(pl.Int64).alias("qty"),
            
            # isbuyermaker=1 -> Maker is Buyer -> Taker is Seller (Side -1)
            pl.when(pl.col("isbuyermaker") == 1)
              .then(pl.lit(-1, dtype=pl.Int8))
              .otherwise(pl.lit(1, dtype=pl.Int8))
              .alias("side"),
              
            pl.lit(0, dtype=pl.Int64).alias("symbol_id")
        ]
        
        try:
            transformed_df = chunk_df.select(exprs)
            table = transformed_df.to_arrow()
            for batch in table.to_batches():
                yield batch
        except Exception as e:
            print(f"Error processing batch {batch_count}: {e}")
            raise e

    print(f"✅ Finished streaming {total_processed:,} rows.")

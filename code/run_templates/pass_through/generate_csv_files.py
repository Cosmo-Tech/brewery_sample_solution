import csv
import random
import string
import argparse
import sys
import os
import time

# --- Configuration / Profiles ---

CATEGORIES = ["Electronics", "Clothing", "Home", "Books", "Toys", "Industrial", "Health"]
STATUSES = ["New", "Processing", "Shipped", "Delivered", "Returned", "Cancelled"]

def get_schema_columns(shape):
    """
    Defines the consistent schema for Wide vs Narrow shapes.
    Returns a list of (column_name, python_type_example) tuples.
    """
    # Common columns for joins and aggregations
    columns = [
        ("id", int),
        ("created_at", str),
        ("category", str),        # Low cardinality for GROUP BY
        ("status", str),          # Low cardinality for GROUP BY
        ("foreign_key", int),     # For JOINs
    ]
    
    if shape == "wide":
        # Wide: Simulate ERP/Salesforce data (Many columns)
        # 100 numeric metrics, 20 text descriptors
        for i in range(100):
            columns.append((f"metric_{i:03d}", float))
        for i in range(20):
            columns.append((f"desc_{i:02d}", str))
            
    elif shape == "narrow":
        # Narrow: Simulate IoT/Log stream (Few columns, high volume potential)
        columns.append(("sensor_val_1", float))
        columns.append(("sensor_val_2", float))
        columns.append(("log_message", str))
        
    return columns

# --- Data Generation ---

def random_string(length=20):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_row(shape, row_id):
    """Produces a dictionary matching the schema."""
    row = {
        "id": row_id,
        "created_at": "2023-10-27 10:00:00", # simplified for CSV
        "category": random.choice(CATEGORIES),
        "status": random.choice(STATUSES),
        "foreign_key": random.randint(1, 5000),
    }
    
    if shape == "wide":
        # Generate metrics
        for i in range(100):
            row[f"metric_{i:03d}"] = round(random.random() * 1000, 4)
        # Generate descriptors
        for i in range(20):
            row[f"desc_{i:02d}"] = random_string(10)
            
    elif shape == "narrow":
        row["sensor_val_1"] = round(random.uniform(20.0, 80.0), 2)
        row["sensor_val_2"] = round(random.uniform(0.0, 1.0), 4)
        row["log_message"] = random_string(40)
        
    return row

# --- Utilities ---

def parse_size(size_str):
    """Parses '1GB', '500MB', '10KB' into bytes."""
    s = size_str.strip().upper()
    if s.endswith("GB"):
        return int(float(s[:-2]) * 1024**3)
    elif s.endswith("MB"):
        return int(float(s[:-2]) * 1024**2)
    elif s.endswith("KB"):
        return int(float(s[:-2]) * 1024)
    else:
        return int(s)

def print_ddl(shape, table_name="benchmark_table"):
    """Generates PostgreSQL CREATE TABLE statement."""
    schema = get_schema_columns(shape)
    print(f"-- SQL DDL for '{shape}' profile")
    print(f"CREATE TABLE IF NOT EXISTS {table_name} (")
    lines = []
    for col, type_example in schema:
        pg_type = "TEXT"
        if type_example == int:
            pg_type = "INTEGER"
        elif type_example == float:
            pg_type = "DOUBLE PRECISION"
        lines.append(f"    {col} {pg_type}")
    print(",\n".join(lines))
    print(");")

def estimate_row_size(shape, samples=50):
    """Estimates average row size in bytes to calculate target row count."""
    from io import StringIO
    
    # Setup writer
    cols = [c[0] for c in get_schema_columns(shape)]
    dummy_io = StringIO()
    writer = csv.DictWriter(dummy_io, fieldnames=cols)
    writer.writeheader()
    start = dummy_io.tell()
    
    for i in range(samples):
        writer.writerow(generate_row(shape, i))
        
    end = dummy_io.tell()
    return (end - start) / samples

def generate_file(filename, target_size_str, shape):
    target_bytes = parse_size(target_size_str)
    avg_row_size = estimate_row_size(shape)
    
    # Calculate rows
    fieldnames = [c[0] for c in get_schema_columns(shape)]
    # Header size
    header_size = sum(len(f) for f in fieldnames) + len(fieldnames)
    
    data_bytes_needed = max(0, target_bytes - header_size)
    estimated_rows = int(data_bytes_needed / avg_row_size) if avg_row_size > 0 else 0

    print(f"--- Configuration ---")
    print(f"File:   {filename}")
    print(f"Shape:  {shape.upper()} ({len(fieldnames)} cols)")
    print(f"Target: {target_size_str} (~{estimated_rows:,} rows)")
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        rows_written = 0
        start_time = time.time()
        
        for i in range(estimated_rows):
            row = generate_row(shape, i)
            writer.writerow(row)
            rows_written += 1
            
            # Simple progress indicator only for large files
            if estimated_rows > 100000 and rows_written % 50000 == 0:
                sys.stdout.write(f"\rProgress: {rows_written:,} rows...")
                sys.stdout.flush()
                
    elapsed = time.time() - start_time
    try:
        actual_size = os.path.getsize(filename)
        print(f"\nDone! Generated {actual_size / (1024**2):.2f} MB in {elapsed:.2f}s")
    except OSError:
        print(f"\nDone! (Size check failed)")

# --- Main ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CSV datasets.")
    
    parser.add_argument("output", nargs="?", help="Output CSV filename (ignored if --flow is used)")
    parser.add_argument("--size", default="10MB", help="Target size (e.g., 10MB, 1GB). Default: 10MB")
    parser.add_argument("--shape", choices=["wide", "narrow"], default="narrow", help="Data shape.")
    parser.add_argument("--ddl", action="store_true", help="Print PostgreSQL CREATE TABLE statement and exit.")
    parser.add_argument("--flow", action="store_true", help="Generate full series of test files (sizes 10KB to 1GB, both shapes).")
    
    args = parser.parse_args()

    # 1. DDL Mode
    if args.ddl:
        print_ddl(args.shape)
        sys.exit(0)

    # 2. Flow Mode (Batch Generation)
    if args.flow:
        sizes = ["10KB", "100KB", "1MB", "10MB", "100MB", "200MB", "500MB", "1GB"]
        shapes = ["wide", "narrow"]
        
        print(f"Starting FLOW generation mode...")
        print(f"Sizes: {sizes}")
        print(f"Shapes: {shapes}\n")
        
        total_start = time.time()
        
        for s in sizes:
            for sh in shapes:
                filename = f"dataset_{s}_{sh}.csv"
                generate_file(filename, s, sh)
                print("-" * 40)
                
        print(f"\nBatch generation complete in {time.time() - total_start:.2f}s")
        sys.exit(0)

    # 3. Single File Mode
    if not args.output:
        print("Error: output filename is required (unless using --flow or --ddl)")
        parser.print_help()
        sys.exit(1)

    generate_file(args.output, args.size, args.shape)
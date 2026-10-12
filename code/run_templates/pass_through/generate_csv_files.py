import csv
import io
import json
import os
import random
import string
import time

# Plan: see generate_csv_files_refactor.md
SEED_BLOCK_SIZE = 1 * 1024**2  # real random rows are generated only up to this size
WRITE_BUFFER_SIZE = 4 * 1024**2
PROGRESS_EVERY_BYTES = 1024**3

CATEGORIES = ["Electronics", "Clothing", "Home", "Books", "Toys", "Industrial", "Health"]
STATUSES = ["New", "Processing", "Shipped", "Delivered", "Returned", "Cancelled"]


def get_schema_columns(shape):
    """Returns a list of (column_name, python_type) tuples for the given shape."""
    columns = [
        ("id", int),
        ("created_at", str),
        ("category", str),
        ("status", str),
        ("foreign_key", int),
    ]

    if shape == "wide":
        for i in range(100):
            columns.append((f"metric_{i:03d}", float))
        for i in range(20):
            columns.append((f"desc_{i:02d}", str))
    elif shape == "narrow":
        columns.append(("sensor_val_1", float))
        columns.append(("sensor_val_2", float))
        columns.append(("log_message", str))
    else:
        raise ValueError(f"Unknown shape '{shape}', expected 'wide' or 'narrow'")

    return columns


def random_string(length=20):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_row(shape, row_id):
    """Produces a dictionary matching the schema."""
    row = {
        "id": row_id,
        "created_at": "2023-10-27 10:00:00",
        "category": random.choice(CATEGORIES),
        "status": random.choice(STATUSES),
        "foreign_key": random.randint(1, 5000),
    }

    if shape == "wide":
        for i in range(100):
            row[f"metric_{i:03d}"] = round(random.random() * 1000, 4)
        for i in range(20):
            row[f"desc_{i:02d}"] = random_string(10)
    elif shape == "narrow":
        row["sensor_val_1"] = round(random.uniform(20.0, 80.0), 2)
        row["sensor_val_2"] = round(random.uniform(0.0, 1.0), 4)
        row["log_message"] = random_string(40)

    return row


def parse_size(size_str):
    """Parses '1GB', '500MB', '10KB' into bytes."""
    s = str(size_str).strip().upper()
    if s.endswith("GB"):
        return int(float(s[:-2]) * 1024**3)
    if s.endswith("MB"):
        return int(float(s[:-2]) * 1024**2)
    if s.endswith("KB"):
        return int(float(s[:-2]) * 1024)
    return int(s)


def build_header(fieldnames):
    buf = io.StringIO(newline="")
    csv.writer(buf).writerow(fieldnames)
    return buf.getvalue().encode("utf-8")


def build_seed_block(shape, fieldnames, max_bytes):
    """Generates random rows and returns them as bytes holding whole rows only, at most max_bytes."""
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    row_id = 0
    while buf.tell() < max_bytes:
        writer.writerow(generate_row(shape, row_id))
        row_id += 1

    data = buf.getvalue().encode("utf-8")
    if len(data) > max_bytes:
        data = data[: data.rfind(b"\n", 0, max_bytes) + 1]
    return data


def generate_file(filename, target_size_str, shape, folder="."):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    target_bytes = parse_size(target_size_str)
    fieldnames = [c[0] for c in get_schema_columns(shape)]
    header = build_header(fieldnames)

    print("--- Configuration ---")
    print(f"File:   {filepath}")
    print(f"Shape:  {shape.upper()} ({len(fieldnames)} cols)")
    print(f"Target: {target_size_str} ({target_bytes:,} bytes)")

    start_time = time.time()
    seed_limit = min(target_bytes - len(header), SEED_BLOCK_SIZE)
    block = build_seed_block(shape, fieldnames, seed_limit) if seed_limit > 0 else b""

    written = 0
    next_progress = PROGRESS_EVERY_BYTES
    with open(filepath, "wb", buffering=WRITE_BUFFER_SIZE) as f:
        f.write(header)
        written += len(header)

        if block:
            while written + len(block) <= target_bytes:
                f.write(block)
                written += len(block)
                if written >= next_progress:
                    print(f"Progress: {written / 1024**3:.1f} GB written")
                    next_progress += PROGRESS_EVERY_BYTES

            # Fill the remainder with whole rows only
            tail = block[: target_bytes - written]
            tail = tail[: tail.rfind(b"\n") + 1]
            f.write(tail)

    elapsed = time.time() - start_time
    actual_size = os.path.getsize(filepath)
    print(f"Done! Generated {actual_size / 1024**2:.2f} MB in {elapsed:.2f}s")


if __name__ == "__main__":
    with open(os.path.join(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"], "parameters.json")) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.load(f)}

    size = parameters.get("csv_file_size", "10MB")
    shape = parameters.get("csv_file_shape", "wide")

    generate_file("data_output.csv", size, shape, os.environ["CSM_OUTPUT_ABSOLUTE_PATH"])

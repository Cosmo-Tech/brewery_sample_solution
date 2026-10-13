"""Stream a local CSV file into an existing PostgreSQL table with COPY ... FROM STDIN.

Python only reads bytes and forwards them: PostgreSQL parses the CSV and converts the values
into the column types declared on the table. SQLite is not involved.

The load runs in a single transaction. csm_run_id is not read from the CSV: it is set as the
transaction-local setting `csm.run_id`, which the table default reads
(csm_run_id text NOT NULL DEFAULT current_setting('csm.run_id')), as in create_table_dataset_wide.sql.

Connection settings are loaded by coal's `Configuration()`, in this order:
1. the TOML file given by CONFIG_FILE_PATH (or /mnt/coal/coal-config.toml in the cluster), [postgres] section;
2. otherwise the env vars POSTGRES_HOST_URI, POSTGRES_HOST_PORT, POSTGRES_DB_NAME, POSTGRES_DB_SCHEMA,
   POSTGRES_USER_NAME, POSTGRES_USER_PASSWORD, CSM_PSQL_FORCE_PASSWORD_ENCODING.

Requires psycopg 3, which is not a coal dependency yet.

Example (run from the repository root):
    uv run --no-project --with-editable . --with "psycopg[binary]" python local/ingest_csv_copy.py \
        local/dataset_10KB_wide.csv --table dataset_wide --run-id run-test-1
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

import psycopg
from psycopg import sql

from cosmotech.coal.postgresql.utils import PostgresUtils
from cosmotech.coal.utils.configuration import Configuration

CHUNK_SIZE = 8 * 1024 * 1024
LOG_EVERY_BYTES = 128 * 1024 * 1024


def postgres_configuration(configuration: Configuration) -> Configuration:
    """Return a configuration exposing `.postgres`, taken from the toml `[[outputs]]` postgres entry, else from env vars."""
    for output in configuration.safe_get("outputs") or []:
        if output.get("type") == "postgres":
            return Configuration({"postgres": output["conf"]["postgres"]})
    return Configuration(Configuration.CONVERSION_DICT)


def connect(configuration: Configuration | None = None, autocommit: bool = False) -> psycopg.Connection:
    """Connect with the coal-built URI and point search_path to the configured schema."""
    psql = PostgresUtils(postgres_configuration(configuration or Configuration()))
    conn = psycopg.connect(psql.full_uri, autocommit=autocommit)
    conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(psql.db_schema)))
    return conn


def read_header(csv_path: Path) -> list[str]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))


def ingest_csv(csv_path: Path, table: str, run_id: str, dry_run: bool = False) -> int:
    columns = read_header(csv_path)
    total_bytes = csv_path.stat().st_size
    copy_stmt = sql.SQL("COPY {table} ({columns}) FROM STDIN WITH (FORMAT csv, HEADER true)").format(
        table=sql.Identifier(table),
        columns=sql.SQL(", ").join(sql.Identifier(c) for c in columns),
    )

    start = time.perf_counter()
    sent = 0
    next_log = LOG_EVERY_BYTES
    with connect(autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('csm.run_id', %s, true)", (run_id,))
            with cur.copy(copy_stmt) as copy, open(csv_path, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    copy.write(chunk)
                    sent += len(chunk)
                    if sent >= next_log:
                        elapsed = time.perf_counter() - start
                        print(f"  {sent / 1e6:,.0f}/{total_bytes / 1e6:,.0f} MB ({sent / 1e6 / elapsed:,.0f} MB/s)")
                        next_log += LOG_EVERY_BYTES
            rows = cur.rowcount

            cur.execute(
                sql.SQL("SELECT count(*) FROM {} WHERE csm_run_id = %s").format(sql.Identifier(table)), (run_id,)
            )
            rows_for_run = cur.fetchone()[0]

        if dry_run:
            conn.rollback()
        else:
            conn.commit()

    elapsed = time.perf_counter() - start
    print(
        f"{'Rolled back (dry run)' if dry_run else 'Committed'}: {rows:,} rows copied, "
        f"{rows_for_run:,} rows with csm_run_id={run_id!r} in the table, "
        f"{total_bytes / 1e6:,.1f} MB in {elapsed:.2f}s ({total_bytes / 1e6 / elapsed:,.1f} MB/s)"
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--table", required=True, help="Existing table, resolved in POSTGRES_DB_SCHEMA")
    parser.add_argument("--run-id", default=os.environ.get("CSM_RUN_ID"), help="Defaults to CSM_RUN_ID")
    parser.add_argument("--dry-run", action="store_true", help="Do the whole load, then roll back")
    args = parser.parse_args()

    if not args.run_id:
        parser.error("--run-id is required (or set CSM_RUN_ID)")
    if not args.csv_path.is_file():
        parser.error(f"{args.csv_path} is not a file")

    ingest_csv(args.csv_path, args.table, args.run_id, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())

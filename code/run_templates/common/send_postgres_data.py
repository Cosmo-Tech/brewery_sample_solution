import argparse
import os
import psycopg2
import psycopg2.extras
import json
import glob
from cosmotech.coal.utils.logger import LOGGER
from csv import DictReader
import pathlib

parser = argparse.ArgumentParser(description='Send csv data to postgres')
parser.add_argument('--source-folder', help='result file source folder', required=True)
parser.add_argument('--postgres-host', help='Postgresql host name', required=True)
parser.add_argument('--postgres-port', help='Postgresql port', required=False, default=5432)
parser.add_argument('--postgres-db', help='Postgresql database name', required=True)
parser.add_argument('--postgres-schema', help='Postgresql database name', required=True)
parser.add_argument('--postgres-user', help='Postgresql connection user name', required=True)
parser.add_argument('--postgres-password', help='Postgresql connection password', required=True)
parser.add_argument('--csm-organization-id', help='Cosmo Tech Organization ID', required=True)
parser.add_argument('--csm-workspace-id', help='Cosmo Tech Workspace ID', required=True)
parser.add_argument('--csm-runner-id', help='Cosmo Tech Runner ID', required=True)
parser.add_argument('--csm-run-id', help='Cosmo Tech Runner run ID', required=True)

args = parser.parse_args()
LOGGER.info(f"Listing files in source directory: {args.source_folder}")
LOGGER.info(glob.glob(f"{args.source_folder}/*"))

def esc(key):
    return key.replace(" ", "_").replace("-", "_").lower()

# https://www.postgresqltutorial.com/postgresql-python/
with psycopg2.connect(
    host=args.postgres_host,
    database=args.postgres_db,
    user=args.postgres_user,
    password=args.postgres_password,
    port=args.postgres_port
) as conn:
    with conn.cursor() as cur:
        source_dir = pathlib.Path(args.source_folder)
        for csv_path in source_dir.glob("*.csv"):
            with open(csv_path) as _f:
                dr = DictReader(_f)
                probe_name = csv_path.name.replace(".csv", "")
                probe_table_name=f"{esc(args.csm_run_id)}_{esc(probe_name)}"
                schema_table=f"{args.postgres_schema}.{probe_table_name}"
                probe_cols=", ".join([f"{esc(k)} TEXT" for k in dr.fieldnames])
                sql_create_table=f"""
                    CREATE TABLE IF NOT EXISTS {schema_table}  (
                      id serial PRIMARY KEY,
                      organization_id varchar(32),
                      workspace_id varchar(32),
                      runner_id varchar(32),
                      run_id varchar(32),
                      {probe_cols}
                    );
                """
                LOGGER.info(f"creating table [cyan bold]{schema_table}[/]")
                cols=esc("organization_id,workspace_id,runner_id,run_id," + ",".join(dr.fieldnames))
                LOGGER.info(f"  - Column list: {cols}")
                cur.execute(sql_create_table)
                conn.commit()
#                 cur.execute(f"""
#                     CREATE INDEX IF NOT EXISTS run_id_index ON {schema_table}(run_id)
#                 """)
#                 conn.commit()
#                 cur.execute(f"""
#                     CREATE INDEX IF NOT EXISTS run_path_index ON {schema_table}(organization_id, workspace_id, runner_id, run_id)
#                 """)
#                 conn.commit()

                LOGGER.info("  - preparing data")
                data = []

                for row in dr:
                    n_row = [args.csm_organization_id, args.csm_workspace_id, args.csm_runner_id, args.csm_run_id]
                    for k, v in row.items():
                        n_row.append(v)
                    data.append(tuple(n_row))

                LOGGER.info(f"  - Sending {len(data)} rows")
                sql_insert=f"INSERT INTO {schema_table} ({cols}) VALUES %s"
                psycopg2.extras.execute_values (
                    cur, sql_insert, data, template=None, page_size=100
                )
    conn.commit()


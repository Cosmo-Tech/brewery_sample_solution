import os
import urllib
import argparse
import psycopg2
from cosmotech.coal.utils.logger import LOGGER
from common import get_logger, get_api, get_authentication_header

LOGGER = get_logger()
api = get_api()


def get_arguments():
    parser = argparse.ArgumentParser(description="Update runner metadata")
    parser.add_argument("--table-prefix", help="RunnerMetadata table prefix", required=False, default="")
    parser.add_argument(
        "--postgres-host", help="Postgresql host name", required=False, default=os.environ.get("POSTGRES_HOST_URI")
    )
    parser.add_argument(
        "--postgres-port", help="Postgresql port", required=False, default=os.environ.get("POSTGRES_HOST_PORT")
    )
    parser.add_argument(
        "--postgres-db", help="Postgresql database name", required=False, default=os.environ.get("POSTGRES_DB_NAME")
    )
    parser.add_argument(
        "--postgres-schema",
        help="Postgresql database schema",
        required=False,
        default=os.environ.get("POSTGRES_DB_SCHEMA"),
    )
    parser.add_argument(
        "--postgres-user",
        help="Postgresql connection user name",
        required=False,
        default=os.environ.get("POSTGRES_USER_NAME"),
    )
    parser.add_argument(
        "--postgres-password",
        help="Postgresql connection user password",
        required=False,
        default=os.environ.get("POSTGRES_USER_PASSWORD"),
    )

    parser.add_argument(
        "--csm-organization-id",
        help="Cosmo Tech Organization ID",
        required=False,
        default=os.environ.get("CSM_ORGANIZATION_ID"),
    )
    parser.add_argument(
        "--csm-workspace-id",
        help="Cosmo Tech Workspace ID",
        required=False,
        default=os.environ.get("CSM_WORKSPACE_ID"),
    )
    parser.add_argument(
        "--csm-runner-id", help="Cosmo Tech Runner ID", required=False, default=os.environ.get("CSM_RUNNER_ID")
    )

    return parser.parse_args()


def main():
    args = get_arguments()
    runner = api.runner.get_runner(args.csm_organization_id, args.csm_workspace_id, args.csm_runner_id)

    schema_table = f"{args.postgres_schema}.{args.table_prefix}RunnerMetadata"
    sql_create_table = f"""
        CREATE TABLE IF NOT EXISTS {schema_table}  (
          id varchar(32) PRIMARY KEY,
          name varchar(256),
          last_run_id varchar(32),
          run_template_id varchar(32)
        );
    """
    sql_upsert = f"""
        INSERT INTO {schema_table} (id, name, last_run_id, run_template_id)
          VALUES(%s, %s, %s, %s)
          ON CONFLICT (id)
          DO
            UPDATE SET name = EXCLUDED.name, last_run_id = EXCLUDED.last_run_id;
    """

    with psycopg2.connect(
        host=args.postgres_host,
        database=args.postgres_db,
        user=args.postgres_user,
        password=urllib.parse.unquote(args.postgres_password),
        port=args.postgres_port,
    ) as conn:
        with conn.cursor() as cur:
            LOGGER.info(f"creating table [cyan bold]{schema_table}[/]")
            cur.execute(sql_create_table)
            conn.commit()
            LOGGER.info(f"adding/updating runner metadata")
            cur.execute(
                sql_upsert,
                (
                    runner.id,
                    runner.name,
                    runner.last_run_id,
                    runner.run_template_id,
                ),
            )
            conn.commit()
    LOGGER.info("Runner metadata table has been updated")


if __name__ == "__main__":
    main()

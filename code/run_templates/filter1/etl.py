import shutil
import os
import sys
import cosmotech_api
from cosmotech_api.model.dataset import Dataset
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1] / "etl_sub_dataset_by_filter"))

from twingraph import (
    parse_twingraph_json,
    create_csv_files_from_graph_content,
    upload_twingraph_zip_archive,
)
from common import get_logger, get_api

LOGGER = get_logger()


def main():
    LOGGER.info("Starting the ETL Run")
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    workspace_id = os.environ.get("CSM_WORKSPACE_ID")
    runner_id = os.environ.get("CSM_RUNNER_ID")
    api = get_api()

    runner = api["runner"].get_runner(
        organization_id=organization_id, workspace_id=workspace_id, runner_id=runner_id
    )
    subdataset_id = runner["dataset_list"][0]
    parent_dataset_id = runner["dataset_list"][1]
    graph_filter = {
        "key": "Thirsty",
        "value": (runner["parameters_values"][0]["value"] == "THIRSTY"),
    }
    filter1(
        api,
        organization_id,
        parent_dataset_id,
        subdataset_id,
        workspace_id,
        graph_filter,
    )
    LOGGER.info("ETL Run finished")


def filter1(
    api, organization_id, parent_dataset_id, subdataset_id, workspace_id, graph_filter
):
    LOGGER.info("Linking subdataset to workspace...")
    try:
        api["dataset"].link_workspace(organization_id, subdataset_id, workspace_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to create subdataset: {e}")
        raise e
    LOGGER.info("Subdataset linked and ready!")
    LOGGER.info("Query and filter dataset")

    node_query = [
        'OPTIONAL MATCH (n)'
        f"WHERE ( NOT EXISTS(n.{graph_filter['key']}) OR n.{graph_filter['key']} = {graph_filter['value']} ) "
        'RETURN n'
    ]
    # WARNING: the query can easily break the JSON to CSV conversion!
    edge_query = [
        "OPTIONAL MATCH (src)-[edge]->(dst) "
        f"WHERE ( NOT EXISTS(src.{graph_filter['key']}) OR src.{graph_filter['key']} = {graph_filter['value']} ) "
        f"       AND (NOT EXISTS(dst.{graph_filter['key']}) OR dst.{graph_filter['key']} = {graph_filter['value']} ) "
        f"RETURN edge, src, dst"
    ]

    nodes = api["dataset"].twingraph_query(
        organization_id, parent_dataset_id, node_query
    )
    edges = api["dataset"].twingraph_query(
        organization_id, parent_dataset_id, edge_query
    )
    LOGGER.info("Transform JSON to csv")

    graph_content = parse_twingraph_json(nodes, edges, "n", "edge", "src", "dst")
    create_csv_files_from_graph_content(graph_content, "twingraph_dump")
    shutil.make_archive("twingraph_dump", "zip", "twingraph_dump")
    LOGGER.info("Upload filtered csv to sub-dataset")
    upload_twingraph_zip_archive(organization_id, subdataset_id, "twingraph_dump.zip")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOGGER.error(f"An error ocurred during the creation of the sub-dataset: {e}")
        sys.exit(-1)

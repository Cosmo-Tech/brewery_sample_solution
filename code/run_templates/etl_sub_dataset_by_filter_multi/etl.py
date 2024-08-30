import json
import shutil
import os
import sys
import cosmotech_api

from common.common import get_logger, get_api
from common.twingraph import (
    parse_twingraph_json,
    create_csv_files_from_graph_content,
    upload_twingraph_zip_archive,
)

LOGGER = get_logger()


def main():
    LOGGER.info("Starting the ETL Run")
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    workspace_id = os.environ.get("CSM_WORKSPACE_ID")
    runner_id = os.environ.get("CSM_RUNNER_ID")
    api = get_api()

    runner = api["runner"].get_runner(organization_id=organization_id, workspace_id=workspace_id, runner_id=runner_id)
    # A webapp convention is that the first dataset is always the subdataset and
    # the second the parent dataset, see doc at:
    # https://github.com/Cosmo-Tech/azure-sample-webapp/blob/main/doc/datasetManager.md#subdataset-creation-scripts
    subdataset_id = runner.dataset_list[0]
    parent_dataset_id = runner.dataset_list[1]
    graph_filter_list = {}
    for element in runner.parameters_values:
        if element.get("parameter_id") == "etl_param_subdataset_filter_dynamic_customers_list":
            graph_filter_list = json.loads(element["value"])
            break
    etl_sub_dataset_by_filter_multi(
        api,
        organization_id,
        parent_dataset_id,
        subdataset_id,
        workspace_id,
        graph_filter_list,
    )
    LOGGER.info("ETL Run finished")


def etl_sub_dataset_by_filter_multi(
    api,
    organization_id,
    parent_dataset_id,
    subdataset_id,
    workspace_id,
    graph_filter_list,
):
    LOGGER.info("Linking subdataset to workspace...")
    try:
        api["dataset"].link_workspace(organization_id, subdataset_id, workspace_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to link subdataset with workspace: {e}")
        raise e
    LOGGER.info("Subdataset linked and ready!")
    LOGGER.info("Query and filter dataset")
    # get nodes without label :Customer OR nodes with label:Customer but with their property id is in the list X return
    # as n
    # get all edges where source AND target nodes do not have the label Customer or
    # if they do their property `id` is not in list X
    node_query = [f"MATCH (n) WHERE ( (NOT n:Customer) OR (n.id IN {graph_filter_list}) ) RETURN n"]
    edge_query = [
        f"MATCH (src)-[edge]->(dst) WHERE "
        f"( (NOT src:Customer) OR (src.id IN {graph_filter_list}) ) "
        "AND"
        f"( (NOT dst:Customer) OR (dst.id IN {graph_filter_list}) ) "
        "RETURN src, edge, dst"
    ]

    nodes = api["dataset"].twingraph_query(organization_id, parent_dataset_id, node_query)
    edges = api["dataset"].twingraph_query(organization_id, parent_dataset_id, edge_query)
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
        LOGGER.error(f"An error occurred during the creation of the sub-dataset: {e}")
        sys.exit(-1)

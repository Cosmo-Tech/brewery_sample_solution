import os
import sys
import cosmotech_api

from common.common import get_logger, get_api
from common.twingraph import copy_dataset_twingraph

LOGGER = get_logger()
api = get_api()


def main():
    LOGGER.info("Starting the ETL Run")
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    workspace_id = os.environ.get("CSM_WORKSPACE_ID")
    runner_id = os.environ.get("CSM_RUNNER_ID")
    runner = api.runner.get_runner(organization_id=organization_id, workspace_id=workspace_id, runner_id=runner_id)
    # A webapp convention is that the first dataset is always the subdataset and
    # the second the parent dataset, see doc at:
    # https://github.com/Cosmo-Tech/azure-sample-webapp/blob/main/doc/datasetManager.md#subdataset-creation-scripts
    subdataset_id = runner.dataset_list[0]
    parent_dataset_id = runner.dataset_list[1]
    graph_filter = {}
    for element in runner.parameters_values:
        if element.parameter_id == "etl_param_subdataset_filter_is_thirsty":
            graph_filter = {
                "key": "Thirsty",
                "value": (element.value == "THIRSTY"),
            }
            break
    etl_sub_dataset_by_filter_boolean(
        api,
        organization_id,
        parent_dataset_id,
        subdataset_id,
        workspace_id,
        graph_filter,
    )
    LOGGER.info("ETL Run finished")


def etl_sub_dataset_by_filter_boolean(
    api, organization_id, parent_dataset_id, subdataset_id, workspace_id, graph_filter
):
    LOGGER.info("Linking subdataset to workspace...")
    try:
        api.dataset.link_workspace(organization_id, subdataset_id, workspace_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to link subdataset with workspace: {e}")
        raise e
    LOGGER.info("Subdataset linked and ready!")
    LOGGER.info("Query and filter dataset")

    filter_key = graph_filter["key"]
    filter_value = graph_filter["value"]
    node_query = f"OPTIONAL MATCH (n) WHERE ( NOT EXISTS(n.{filter_key}) OR n.{filter_key} = {filter_value} ) RETURN n"
    # WARNING: the query can easily break the JSON to CSV conversion!
    edge_query = (
        "OPTIONAL MATCH (src)-[edge]->(dst) "
        f"WHERE ( NOT EXISTS(src.{filter_key}) OR src.{filter_key} = {filter_value} ) "
        f"       AND (NOT EXISTS(dst.{filter_key}) OR dst.{filter_key} = {filter_value} ) "
        "RETURN edge, src, dst"
    )

    copy_dataset_twingraph(organization_id, parent_dataset_id, subdataset_id, node_query, edge_query)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOGGER.error(f"An error occurred during the creation of the sub-dataset: {e}")
        sys.exit(-1)

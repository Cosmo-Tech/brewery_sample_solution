import os
import time
import cosmotech_api
from cosmotech_api.models.dataset_twin_graph_query import DatasetTwinGraphQuery
import common


LOGGER = common.get_logger()


def dump_twingraph_dataset_to_csv_files(organization_id, parent_dataset, dataset_id, folder_path):
    api = common.get_api()

    # dataset_twin_graph_query = cosmotech_api.DatasetTwinGraphQuery()

    # dataset_twin_graph_query = DatasetTwinGraphQuery()
    # query_get_all = dataset_twin_graph_query.from_dict({"query": "MATCH(n) OPTIONAL MATCH ()-[r]-() RETURN n, r"})

    # query_get_all = DatasetTwinGraphQuery("MATCH(n) OPTIONAL MATCH ()-[r]-() RETURN n, r")

    # query_get_all = DatasetTwinGraphQuery.from_json('{"query": "MATCH(n) OPTIONAL MATCH ()-[r]-() RETURN n, r"}')
    query_get_all = DatasetTwinGraphQuery.from_dict({"query": "MATCH(n) OPTIONAL MATCH ()-[r]-() RETURN n, r"})

    parent_dataset_id = parent_dataset["id"]

    try:
        # Return the result of a query made on the graph instance as a json
        LOGGER.info("Querying all nodes & edges from the twingraph...")
        query_start_time = time.time()
        api_response = api["dataset"].twingraph_query(organization_id, parent_dataset_id, query_get_all.to_dict())
        query_duration_in_seconds = time.time() - query_start_time
        LOGGER.info(f"Results received, query took {query_duration_in_seconds} seconds")

        # api_response = api["dataset"].twingraph_query(
        #     organization_id, parent_dataset_id, '"MATCH(n) OPTIONAL MATCH ()-[r]-() RETURN n, r;"'
        # )

        LOGGER.info(api_response)
    except cosmotech_api.ApiException as e:
        LOGGER.error(f"Failed to retrieve content of parent dataset with id {parent_dataset_id}: %s\n" % e)
        raise e


def compress_for_twingraph_upload(foldar_path):
    archive_path = os.path("twingraph_dump.zip")
    return archive_path

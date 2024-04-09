import os
import time
from functools import reduce
import cosmotech_api
import common


LOGGER = common.get_logger()


def dump_twingraph_dataset_to_csv_files(organization_id, parent_dataset, dataset_id, folder_path):
    api = common.get_api()
    parent_dataset_id = parent_dataset["id"]
    try:
        query_nodes = {"query": "OPTIONAL MATCH(n) RETURN n"}
        query_edges = {"query": "OPTIONAL MATCH(src)-[edge]->(dest) RETURN src, edge, dest"}
        LOGGER.info("Querying all nodes & edges from the twingraph...")
        fetch_start_time = time.time()
        res_nodes = api["dataset"].twingraph_query(organization_id, parent_dataset_id, query_nodes)
        res_edges = api["dataset"].twingraph_query(organization_id, parent_dataset_id, query_edges)
        fetch_duration_in_seconds = time.time() - fetch_start_time
        LOGGER.info(f"Results received, queries took {fetch_duration_in_seconds} seconds")
    except cosmotech_api.ApiException as e:
        LOGGER.error(f"Failed to retrieve content of parent dataset with id {parent_dataset_id}: %s\n" % e)
        raise e

    def parse_twingraph_json_item(content, data, item_key):
        item = data[item_key]
        item_id = item["id"]
        item_label = item["label"]
        item_type = item["type"]
        content_by_type = content[item_type] = content.get(item_type, {})
        content_by_label = content_by_type[item_label] = content_by_type.get(item_label, {})
        content_by_label[item_id] = content_by_label.get(item_id, item["properties"])
        return content

    def parse_node(content, data):
        return parse_twingraph_json_item(content, data, "n")  # key is defined by the cypher query

    def parse_edge(content, data):
        return parse_twingraph_json_item(content, data, "r")  # key is defined by the cypher query

    graph_content = reduce(parse_node, res_nodes, {})
    graph_content = reduce(parse_edge, res_edges, graph_content)
    LOGGER.info(graph_content)


def compress_for_twingraph_upload(foldar_path):
    archive_path = os.path("twingraph_dump.zip")
    return archive_path

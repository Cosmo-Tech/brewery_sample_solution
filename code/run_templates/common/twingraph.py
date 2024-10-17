import os
import csv
import time
import shutil
import requests
import tempfile
from functools import reduce
import cosmotech_api
from common.common import get_logger, get_api, get_authentication_header

LOGGER = get_logger()
api = get_api()


def parse_twingraph_json(nodes, edges, node_key, edge_key, src_key, dst_key):
    def parse_item(content, data, item_key):
        item = data.get(item_key)
        if item is None:
            return content
        item_id = item["id"]
        item_label = item["label"]
        item_type = item["type"]
        content_by_type = content[item_type] = content.get(item_type, {})
        content_by_label = content_by_type[item_label] = content_by_type.get(item_label, {})
        item_properties = content_by_label[item_id] = content_by_label.get(item_id, item["properties"])

        if item_type == "RELATION":
            item_properties["source"] = data[src_key]["properties"]["id"]
            item_properties["target"] = data[dst_key]["properties"]["id"]
        return content

    def parse_node(content, data):
        return parse_item(content, data, node_key)

    def parse_edge(content, data):
        return parse_item(content, data, edge_key)

    try:
        graph_content = reduce(parse_node, nodes, {})
        graph_content = reduce(parse_edge, edges, graph_content)
    except Exception as e:
        LOGGER.error(f"An error occurred while parsing the twingraph JSON representation: {e}")
        raise(e)
    return graph_content


def create_csv_files_from_graph_content(graph_content, folder_path):
    nodes_folder_path = os.path.join(folder_path, "Nodes")
    os.makedirs(nodes_folder_path, exist_ok=True)
    all_nodes = graph_content["NODE"]
    for node_type, wrapped_nodes in all_nodes.items():
        nodes = list(wrapped_nodes.values())
        if len(nodes) == 0:
            continue
        header = list(nodes[0].keys())
        # As of v3.0 of Cosmo Tech API, columns MUST start with the id column for nodes
        header.remove("id")
        header = ["id", *header]

        with open(os.path.join(nodes_folder_path, f"{node_type}.csv"), "w") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for node in nodes:
                id = node["id"]
                del node["id"]
                values = [id, *node.values()]
                writer.writerow(values)

    edges_folder_path = os.path.join(folder_path, "Edges")
    os.makedirs(edges_folder_path, exist_ok=True)
    all_edges = {}
    if "RELATION" in graph_content:
        all_edges = graph_content["RELATION"]

    for edge_type, wrapped_edges in all_edges.items():
        edges = list(wrapped_edges.values())
        if len(edges) == 0:
            continue
        header = list(edges[0].keys())
        # As of v3.0 of Cosmo Tech API, columns MUST start with "source,target,name" columns for edges
        if len(header) == 3:
            header = ["source", "target", "name"]
        else:
            header.remove("source")
            header.remove("target")
            header.remove("name")
            header = ["source", "target", "name", *header]

        with open(os.path.join(edges_folder_path, f"{edge_type}.csv"), "w") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for edge in edges:
                edge_name = edge["name"]
                edge_source = edge["source"]
                edge_target = edge["target"]
                del edge["name"]
                del edge["source"]
                del edge["target"]
                values = [edge_source, edge_target, edge_name, *edge.values()]
                writer.writerow(values)


def dump_twingraph_dataset_to_zip_archive(
    organization_id, dataset_id, folder_path, node_query_str=None, edge_query_str=None
):
    try:
        if node_query_str is None and edge_query_str is None:
            LOGGER.info("Querying all nodes & edges from the twingraph...")
        else:
            LOGGER.info("Sending custom queries to extract twingraph data...")
        if node_query_str is None:
            node_query_str = "OPTIONAL MATCH(n) RETURN n"
        if edge_query_str is None:
            edge_query_str = "OPTIONAL MATCH(src)-[edge]->(dst) RETURN src, edge, dst"

        fetch_start_time = time.time()
        res_nodes = api.dataset.twingraph_query(organization_id, dataset_id, {"query": node_query_str})
        res_edges = api.dataset.twingraph_query(organization_id, dataset_id, {"query": edge_query_str})
        fetch_duration_in_seconds = time.time() - fetch_start_time
        LOGGER.info(f"Results received, queries took {fetch_duration_in_seconds} seconds")
    except cosmotech_api.ApiException as e:
        LOGGER.error(f"Failed to retrieve content of target dataset '{dataset_id}': %s\n" % e)
        raise e

    # Note: the keys are defined in the cypher queries above
    graph_content = parse_twingraph_json(res_nodes, res_edges, "n", "edge", "src", "dst")
    create_csv_files_from_graph_content(graph_content, folder_path)

    output_file_path = os.path.join(folder_path, "twingraph_dump")
    output_file_path_with_format = os.path.join(folder_path, "twingraph_dump.zip")
    shutil.make_archive(output_file_path, "zip", folder_path)
    return output_file_path_with_format


def upload_twingraph_zip_archive(organization_id, dataset_id, zip_archive_path):
    try:
        api.dataset.update_dataset(organization_id, dataset_id, {"ingestionStatus": "NONE", "sourceType": "File"})
    except cosmotech_api.ApiException as e:
        LOGGER.error("Exception when changing twingraph type & status: %s\n" % e)
        raise e

    with open(zip_archive_path, "rb") as file:
        api_url = os.environ.get("CSM_API_URL")
        auth_headers = get_authentication_header()

        try:
            response = requests.post(
                f"{api_url}/organizations/{organization_id}/datasets/{dataset_id}",
                data=file,
                headers={"Content-Type": "application/octet-stream", **auth_headers},
            )
            imported_data = response.json()
            LOGGER.info(f"Imported data: {imported_data}")
        except cosmotech_api.ApiException as e:
            LOGGER.error("Exception when uploading twingraph archive: %s\n" % e)
            raise e

    LOGGER.info("Resetting sourceType & status of subdataset...")
    try:
        # Required delay to prevent some race condition, leading sometimes to the sourceType update being ignored
        time.sleep(2)
        api.dataset.update_dataset(organization_id, dataset_id, {"ingestionStatus": "SUCCESS", "sourceType": "ETL"})
    except cosmotech_api.ApiException as e:
        LOGGER.error("Exception when changing twingraph type & status: %s\n" % e)
        raise e


def copy_dataset_twingraph(org_id, src_dataset_id, dst_dataset_id, node_query=None, edge_query=None):
    '''
    Parameters:
      - org_id is the id of the organization containing the source and target datasets
      - src_dataset_id is the id of the dataset to copy
      - dst_dataset_id is the id of the dataset where the data will be copied
      - node_query (optional) is a string containing the cypher query to select the nodes to copy; nodes must be
        returned with the alias 'n' (default query: "OPTIONAL MATCH(n) RETURN n")
      - edge_query (optional) is a string containing the cypher query to select the edges to copy; edge data must be
        returned with the aliasas 'src, edge, dst' (default query:
        "OPTIONAL MATCH(src)-[edge]->(dst) RETURN src, edge, dst")
    '''
    with tempfile.TemporaryDirectory() as tmp_dir:
        twingraph_dump_dir_path = os.path.join(tmp_dir, "twingraph_dump")
        zip_archive_path = dump_twingraph_dataset_to_zip_archive(
            org_id, src_dataset_id, twingraph_dump_dir_path, node_query, edge_query)
        LOGGER.info(f"Twingraph extracted to {zip_archive_path}")
        LOGGER.info(f"Starting zip upload to existing dataset '{dst_dataset_id}'...")
        upload_twingraph_zip_archive(org_id, dst_dataset_id, zip_archive_path)

import csv
import json
import os
from zipfile import ZipFile
from azure.storage.blob import BlobClient

from cosmotech_api.model.dataset import Dataset
from common.common import get_logger, get_api

LOGGER = get_logger()


def main():
    LOGGER.info("Starting the ETL Run")
    api = get_api()
    runner_data = api.runner.get_runner(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        workspace_id=os.environ.get("CSM_WORKSPACE_ID"),
        runner_id=os.environ.get("CSM_RUNNER_ID"),
    )

    with open(os.path.join(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH"), "parameters.json")) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    print(parameters)

    LOGGER.info("All parameters are loaded")

    bars = list()

    bar = {
        "type": "Bar",
        "name": "MyBar",
        "params": f"""NbWaiters: {int(parameters["etl_param_num_waiters"])},"""
        + f"""RestockQty: {int(parameters["etl_param_restock_quantity"])},"""
        + f"""Stock: {int(parameters["etl_param_stock"])}""",
    }
    bars.append(bar)

    base_path = "."

    blob = BlobClient.from_connection_string(
        conn_str=parameters["etl_param_azure_storage_co_string"],
        container_name=parameters["etl_param_az_storage_container"],
        blob_name=parameters["etl_param_az_storage_path"],
    )
    with open(base_path + "/brewery_instance.zip", "wb") as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)

    with ZipFile(base_path + "/brewery_instance.zip") as zip:
        zip.extractall(base_path)

    base_path = base_path + "/reference"
    customers = list()
    with open(base_path + "/Nodes/Customer.csv") as _f:
        LOGGER.info("Found 'Customer' list")
        csv_r = csv.DictReader(_f)
        for row in csv_r:
            customer = {
                "type": "Customer",
                "name": row["id"],
                "params": f"Name: '{row['id']}',"
                f"Satisfaction: {row['Satisfaction']},"
                f"SurroundingSatisfaction: {row['SurroundingSatisfaction']},"
                f"Thirsty: {row['Thirsty']}",
            }
            customers.append(customer)

    satisfactions = list()
    with open(base_path + "/Edges/arc_Satisfaction.csv") as _f:
        LOGGER.info("Found 'Customer satisfaction' relation")
        csv_r = csv.DictReader(_f)
        for row in csv_r:
            satisfaction = {
                "type": "arc_Satisfaction",
                "source": row["source"],
                "target": row["target"],
                "name": row["name"],
                "params": "a: 'a'",
            }
            satisfactions.append(satisfaction)

    links = list()
    with open(base_path + "/Edges/Bar_vertex.csv") as _f:
        LOGGER.info("Found 'Bar vertex' relation")
        csv_r = csv.DictReader(_f)
        for row in csv_r:
            link = {
                "type": "bar_vertex",
                "source": row["source"],
                "target": row["target"],
                "name": row["name"],
                "params": "a: 'a'",
            }
            links.append(link)

    dataset = Dataset(ingestion_status="SUCCESS")
    api.dataset.update_dataset(os.environ.get("CSM_ORGANIZATION_ID"), runner_data.dataset_list[0], dataset)

    try:
        LOGGER.info("Erasing data from target Dataset")
        api.dataset.twingraph_query(
            organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
            dataset_id=runner_data.dataset_list[0],
            dataset_twin_graph_query={"query": "MATCH (n) DETACH DELETE n"},
        )
    except Exception:
        pass

    LOGGER.info("Writing entities into target Dataset")
    api.dataset.create_twingraph_entities(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        dataset_id=runner_data.dataset_list[0],
        type="node",
        graph_properties=bars + customers,
    )

    LOGGER.info("Writing relationshipss into target Dataset")
    api.dataset.create_twingraph_entities(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        dataset_id=runner_data.dataset_list[0],
        type="relationship",
        graph_properties=satisfactions + links,
    )

    api.dataset.update_dataset(
        os.environ.get("CSM_ORGANIZATION_ID"), runner_data['dataset_list'][0], Dataset(twincacheStatus="FULL")
    )

    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    main()

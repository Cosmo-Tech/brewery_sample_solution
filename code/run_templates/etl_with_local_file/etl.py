import csv
import json
import os
from zipfile import ZipFile

from cosmotech_api.model.dataset import Dataset
from common.common import get_logger, get_api

LOGGER = get_logger()


def get_zip_file_name(dir):
    for _, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".zip"):
                return file


def main():
    LOGGER.info("Starting the ETL Run")
    api = get_api()
    runner_api_instance = api["runner"]
    dataset_api_instance = api["dataset"]

    runner_data = runner_api_instance.get_runner(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        workspace_id=os.environ.get("CSM_WORKSPACE_ID"),
        runner_id=os.environ.get("CSM_RUNNER_ID"),
    )

    with open(os.path.join(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH"), "parameters.json")) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

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

    base_path = parameters["etl_param_bar_instance"]
    file_name = get_zip_file_name(base_path)
    with ZipFile(base_path + "/" + file_name) as zip:
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
    dataset_api_instance.update_dataset(os.environ.get("CSM_ORGANIZATION_ID"), runner_data.dataset_list[0], dataset)

    try:
        LOGGER.info("Erasing data from target Dataset")
        dataset_api_instance.twingraph_query(
            organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
            dataset_id=runner_data.dataset_list[0],
            dataset_twin_graph_query={"query": "MATCH (n) DETACH DELETE n"},
        )
    except Exception:
        pass

    LOGGER.info("Writing entities into target Dataset")
    dataset_api_instance.create_twingraph_entities(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        dataset_id=runner_data.dataset_list[0],
        type="node",
        graph_properties=bars + customers,
    )

    LOGGER.info("Writing relationshipss into target Dataset")
    dataset_api_instance.create_twingraph_entities(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        dataset_id=runner_data.dataset_list[0],
        type="relationship",
        graph_properties=satisfactions + links,
    )

    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    main()

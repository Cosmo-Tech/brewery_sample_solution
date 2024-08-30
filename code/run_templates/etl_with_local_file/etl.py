import json
import logging
import os

from zipfile import ZipFile
import csv
import glob

import cosmotech_api
from azure.identity import DefaultAzureCredential
from cosmotech_api.api.dataset_api import DatasetApi
from cosmotech_api.model.dataset import Dataset
from cosmotech_api.api.runner_api import RunnerApi
from rich.logging import RichHandler

LOGGER = logging.getLogger("my_etl_logger")

_format = "[ETL] %(message)s"

logging.basicConfig(
    format=_format,
    datefmt="[%Y/%m/%d-%X]",
    handlers=[RichHandler(rich_tracebacks=True,
                          omit_repeated_times=False,
                          show_path=False,
                          markup=True)])
LOGGER.setLevel(logging.INFO)


def get_zip_file_name(dir):
    for _, _, files in os.walk(dir):
        for file in files:
            if(file.endswith(".zip")):
                return file


def main():
    LOGGER.info("Starting the ETL Run")
    credentials = DefaultAzureCredential()
    scope = os.environ.get("CSM_API_SCOPE")
    access_token = credentials.get_token(scope).token
    configuration = cosmotech_api.Configuration(
        host=os.environ.get("CSM_API_URL"),
        discard_unknown_keys=True,
        access_token=access_token
    )

    with cosmotech_api.ApiClient(configuration) as api_client:
        runner_api_instance = RunnerApi(api_client)
        dataset_api_instance = DatasetApi(api_client)
        runner_data = runner_api_instance.get_runner(organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
                                                     workspace_id=os.environ.get("CSM_WORKSPACE_ID"),
                                                     runner_id=os.environ.get("CSM_RUNNER_ID"))

    with open(os.path.join(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH"), "parameters.json")) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    LOGGER.info("All parameters are loaded")

    bars = list()

    bar = {
        "type": "Bar",
        "name": "MyBar",
        "params": f"""NbWaiters: {int(parameters["etl_param_num_waiters"])},""" +
                  f"""RestockQty: {int(parameters["etl_param_restock_quantity"])},""" +
                  f"""Stock: {int(parameters["etl_param_stock"])}""",
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
                "name": row['id'],
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
                "source": row['source'],
                "target": row['target'],
                "name": row['name'],
                "params": f"a: 'a'"
            }
            satisfactions.append(satisfaction)

    links = list()
    with open(base_path + "/Edges/Bar_vertex.csv") as _f:
        LOGGER.info("Found 'Bar vertex' relation")
        csv_r = csv.DictReader(_f)
        for row in csv_r:
            link = {
                "type": "bar_vertex",
                "source": row['source'],
                "target": row['target'],
                "name": row['name'],
                "params": f"a: 'a'"
            }
            links.append(link)

    dataset = Dataset(ingestion_status="SUCCESS")
    dataset_api_instance.update_dataset(os.environ.get("CSM_ORGANIZATION_ID"), runner_data.dataset_list[0], dataset)

    try:
        LOGGER.info("Erasing data from target Dataset")
        dataset_api_instance.twingraph_query(
            organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
            dataset_id=runner_data.dataset_list[0],
            dataset_twin_graph_query={"query": "MATCH (n) DETACH DELETE n"})
    except e:
        pass

    LOGGER.info("Writing entities into target Dataset")
    dataset_api_instance.create_twingraph_entities(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        dataset_id=runner_data.dataset_list[0],
        type="node",
        graph_properties=bars + customers)

    LOGGER.info("Writing relationshipss into target Dataset")
    dataset_api_instance.create_twingraph_entities(
        organization_id=os.environ.get("CSM_ORGANIZATION_ID"),
        dataset_id=runner_data.dataset_list[0],
        type="relationship",
        graph_properties=satisfactions + links)

    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    main()

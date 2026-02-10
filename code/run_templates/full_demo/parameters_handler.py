import csv
import json
import itertools
import shutil
from pathlib import Path

from csv_handler import update_first_row_in_csv
from fetcher import fetch_dataset_file_path, fetch_parameter_file_path
from cosmotech.coal.utils.configuration import ENVIRONMENT_CONFIGURATION as EC
from cosmotech.orchestrator.utils.logger import get_logger

LOGGER = get_logger('parameter_handler')


def get_parameters():
    with open(
        Path(EC.cosmotech.parameters_absolute_path) / "parameters.json"
    ) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    LOGGER.info("Parameters loaded from JSON")
    return parameters


def fetch_customers_list():
    customers = []

    def extract_names_from_csv(csv_path: Path):
        names = []
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                names.append(row['Name'])
        return names

    try:
        customers_csv_path = fetch_parameter_file_path("customers_dynamic_table")
    except FileNotFoundError:
        customers_csv_path = fetch_dataset_file_path("Customer.csv")
    customers.extend(extract_names_from_csv(customers_csv_path))

    try:
        additionnal_customers_csv_path = fetch_parameter_file_path("additional_customers")
        customers.extend(extract_names_from_csv(additionnal_customers_csv_path))
    except FileNotFoundError:
        pass

    LOGGER.info(f"Fetched {len(customers)} customers from {customers_csv_path}")
    return customers


def generate_customers(customers: list):
    customer_csv_path = Path(EC.cosmotech.dataset_absolute_path) / "Customer.csv"
    with open(customer_csv_path, 'w', newline='') as f:
        fieldnames = ['id', 'Thirsty', 'Satisfaction', 'SurroundingSatisfaction']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for customer in customers:
            writer.writerow({
                'id': customer,
                'Thirsty': 'false',
                'Satisfaction': 100,
                'SurroundingSatisfaction': 100
            })
    LOGGER.info(f"Generated Customer.csv with {len(customers)} customers at {customer_csv_path}")


def generate_bar_to_customer_mapping(bar_name: str, customers: list):
    bar_vertex_csv_path = Path(EC.cosmotech.dataset_absolute_path) / "Bar_vertex.csv"
    with open(bar_vertex_csv_path, 'w', newline='') as f:
        fieldnames = ['source', 'target']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for customer in customers:
            writer.writerow({'source': bar_name, 'target': customer})
    LOGGER.info(f"Generated bar to customer mapping in {bar_vertex_csv_path}")


def generate_customers_to_customer_mapping(customers: list):
    arc_satisfaction_csv_path = Path(EC.cosmotech.dataset_absolute_path) / "arc_Satisfaction.csv"
    with open(arc_satisfaction_csv_path, 'w', newline='') as f:
        fieldnames = ['source', 'target']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, j in itertools.combinations(customers, 2):
            writer.writerow({'source': i, 'target': j})
            writer.writerow({'source': j, 'target': i})
    LOGGER.info(f"Generated customers to customer mapping in {arc_satisfaction_csv_path}")


def main():
    LOGGER.info("Starting parameter handler")

    # get_parameter from json
    parameters = get_parameters()

    # update dataset Bar.csv with param
    updated_values = {}
    if "nb_waiters" in parameters:
        updated_values["NbWaiters"] = parameters["nb_waiters"]
    if "restock_qty" in parameters:
        updated_values["RestockQty"] = parameters["restock_qty"]
    if "stock" in parameters:
        updated_values["Stock"] = parameters["stock"]
    updated_values["id"] = "MyBar"
    # copy initial Bar.csv to datasets path
    fetched_dataset_file_path = fetch_dataset_file_path("Bar.csv")
    bar_csv_path = Path(EC.cosmotech.dataset_absolute_path) / "Bar.csv"
    shutil.copy(fetched_dataset_file_path, bar_csv_path)
    first_row = update_first_row_in_csv(bar_csv_path, updated_values)
    LOGGER.info("Updated Bar.csv with parameters")

    # copy initial Customer.csv to datasets path
    fetched_dataset_file_path = fetch_dataset_file_path("Customer.csv")
    customer_csv_path = Path(EC.cosmotech.dataset_absolute_path) / "Customer.csv"
    shutil.copy(fetched_dataset_file_path, customer_csv_path)

    LOGGER.info("Updated Customer.csv with parameters")

    # fetch customers
    customers = fetch_customers_list()
    # generate Customer.csv
    generate_customers(customers)
    # generate bar_vertex
    generate_bar_to_customer_mapping(first_row["id"], customers)
    # generate arc_satisfaction
    generate_customers_to_customer_mapping(customers)


if __name__ == "__main__":
    main()

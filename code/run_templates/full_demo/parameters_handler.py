import csv
import json
import os
import itertools
from pathlib import Path

from cosmotech.coal.utils.configuration.Configuration import ENVIRONMENT_CONFIGURATION as EC
from cosmotech.orchestrator.utils.logger import get_logger

LOGGER = get_logger('parameter_handler')


def get_parameters():
    with open(
        Path(EC.cosmotech.parameters_absolute_path) / "parameters.json"
    ) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    LOGGER.info("Parameters loaded from JSON")
    return parameters


def update_first_row_in_csv(csv_path, updated_values):
    """
    Read a CSV file and change the first data row with new values.

    Args:
        csv_path: Path to the CSV file
        updated_values: Dictionary with column names as keys and new values
    """
    # Read the CSV file
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Update the first row with new values
    if rows:
        for key, value in updated_values.items():
            if key in rows[0]:
                rows[0][key] = value

    # Write back to the CSV file
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows[0]


def fetch_parameter_file_path(param_name: str) -> Path:
    for r, d, f in os.walk(EC.cosmotech.parameters_absolute_path):
        if param_name in r:
            return Path(r) / f[0]
    raise FileNotFoundError(f"Parameter file for {param_name} not found.")


def fetch_customers_list():
    customers = []

    def extract_names_from_csv(csv_path: Path):
        names = []
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                names.append(row['Name'])
        return names

    customers_csv_path = fetch_parameter_file_path("customers")
    customers.extend(extract_names_from_csv(customers_csv_path))

    additionnal_customers_csv_path = fetch_parameter_file_path("additional_customers")
    customers.extend(extract_names_from_csv(additionnal_customers_csv_path))

    LOGGER.info(f"Fetched {len(customers)} customers from {customers_csv_path}")
    return customers


def generate_bar_to_customer_mapping(bar_name: str, customers: list):
    bar_vertex_csv_path = Path(EC.cosmotech.datasets_absolute_path) / "Bar_vertex.csv"
    with open(bar_vertex_csv_path, 'w', newline='') as f:
        fieldnames = ['source', 'target']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for customer in customers:
            writer.writerow({'source': bar_name, 'target': customer})
    LOGGER.info(f"Generated bar to customer mapping in {bar_vertex_csv_path}")


def generate_customers_to_customer_mapping(customers: list):
    arc_satisfaction_csv_path = Path(EC.cosmotech.datasets_absolute_path) / "arc_Satisfaction.csv"
    with open(arc_satisfaction_csv_path, 'w', newline='') as f:
        fieldnames = ['source', 'target']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, j in itertools.combinations(customers, 2):
            writer.writerow({'source': customers[i], 'target': customers[j]})
            writer.writerow({'source': customers[j], 'target': customers[i]})
    LOGGER.info(f"Generated customers to customer mapping in {arc_satisfaction_csv_path}")


def main():
    LOGGER.info("Starting parameter handler")

    # get_parameter from json
    parameters = get_parameters()

    # update dataset Bar.csv with param
    updated_values = {}
    if "NbWaiters" in parameters:
        updated_values["NbWaiters"] = parameters["NbWaiters"]
    if "RestockQty" in parameters:
        updated_values["RestockQty"] = parameters["RestockQty"]
    if "Stock" in parameters:
        updated_values["Stock"] = parameters["Stock"]
    if "bar_name" in parameters:
        updated_values["bar_name"] = parameters["bar_name"]
    bar_csv_path = Path(EC.cosmotech.datasets_absolute_path) / "Bar.csv"
    first_row = update_first_row_in_csv(bar_csv_path, updated_values)
    LOGGER.info("Updated Bar.csv with parameters")

    # generate_Customers
    customers = fetch_customers_list()
    # generate bar_vertex
    generate_bar_to_customer_mapping(first_row["bar_name"], customers)
    # generate arc_satisfaction
    generate_customers_to_customer_mapping(customers)

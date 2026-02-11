import os
import json
import csv
from pathlib import Path

from cosmotech.coal.utils.logger import get_logger
from cosmotech.coal.utils.configuration import ENVIRONMENT_CONFIGURATION as EC
from cosmotech.coal.cosmotech_api.apis.dataset import DatasetApi
from cosmotech.coal.cosmotech_api.apis.runner import RunnerApi
from fetcher import fetch_dataset_file_path

LOGGER = get_logger('etl')


def filter_customers_file(customers_file_path, customers_to_keep):
    # Read all rows and filter
    with open(customers_file_path, "r") as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames
        filtered_rows = [row for row in reader if row[fieldnames[0]] in customers_to_keep]

    # Write back to the same file
    with open(customers_file_path, "w", newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_rows)

    return customers_file_path


def read_parameters():
    with open(
        Path(EC.cosmotech.parameters_absolute_path) / "parameters.json"
    ) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    LOGGER.info("Parameters loaded from JSON")
    return parameters


def main():
    # get input and outputdataset id from runner data
    runner_api = RunnerApi()
    runner_data = runner_api.get_runner_metadata()
    input_dataset_id = runner_data['datasets']['bases'][1]
    output_dataset_id = runner_data['datasets']['bases'][0]

    # list datasets files path
    input_dataset_files_path_list = []
    for dataset_file in os.listdir(Path(EC.cosmotech.dataset_absolute_path) / input_dataset_id):
        input_dataset_files_path_list.append(fetch_dataset_file_path(dataset_file, input_dataset_id))

    # extract parameter "etl_param_list_dynamic_customers"
    parameters = read_parameters()
    etl_param_list_dynamic_customers = parameters.get("etl_param_list_dynamic_customers", [])

    # filter content of the file "Customer.csv" to keep only the customers in the list
    customers_file_path = fetch_dataset_file_path("Customer.csv", input_dataset_id)
    filter_customers_file(customers_file_path, etl_param_list_dynamic_customers)

    # update output dataset with all datasets files, including the updated "Customer.csv"
    dataset_api = DatasetApi()
    dataset_api.upload_dataset_parts(
        output_dataset_id, [], input_dataset_files_path_list, replace_existing=True
    )
    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    main()

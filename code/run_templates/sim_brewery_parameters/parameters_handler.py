import os
import sys
from pathlib import Path
import csv
from tempfile import NamedTemporaryFile, TemporaryDirectory
import shutil
import glob
import json
from common.common import get_api, get_logger
from cosmotech.coal.cosmotech_api.connection import get_api_client
from cosmotech.coal.cosmotech_api.workspace import download_workspace_file

LOGGER = get_logger()
api = get_api()


def main():
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    workspace_id = os.environ.get("CSM_WORKSPACE_ID")
    data_folder = Path(os.environ["CSM_DATASET_ABSOLUTE_PATH"])

    parameters_folder = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
    json_parameters_file = parameters_folder / "parameters.json"
    if not json_parameters_file.exists():
        raise Exception(f"No parameters file in {parameters_file}")

    values = {
        "stock": 0,
        "restock_qty": 0,
        "nb_waiters": 0,
        "initial_stock_dataset": "",
    }
    expected_parameters = list(values.keys())
    LOGGER.info("Start parsing JSON parameters file")
    with open(json_parameters_file) as json_file:
        parameters = json.load(json_file)
        for parameter in parameters:
            parameter_name = parameter["parameterId"]
            parameter_value = parameter["value"]
            if parameter_name not in expected_parameters:
                LOGGER.warning(f"Unknown parameter {parameter_name}")
            else:
                LOGGER.info(f'Value for {parameter_name}: "{parameter_value}"')
                values[parameter_name] = parameter_value

    if values["initial_stock_dataset"] == "":
        LOGGER.info("\nInitial stock file not uploaded, skipping this part...")
    else:
        dataset_folder = parameters_folder / "initial_stock_dataset"
        dataset_files = os.listdir(dataset_folder)
        if not dataset_files:
            LOGGER.info(f'\nNo files in folder: "{dataset_folder}"')
        else:
            LOGGER.info(f"\nParsing rows of {dataset_files[0]}")
            with open(dataset_folder / dataset_files[0], "r") as initial_stock_file:
                dataset_reader = csv.reader(initial_stock_file)
                for row in dataset_reader:
                    values["stock"] = row[1]
                    break

    runner_data = api.runner.get_runner(
        organization_id=organization_id,
        workspace_id=workspace_id,
        runner_id=os.environ.get("CSM_RUNNER_ID"),
    )
    instance_dataset_id = runner_data.dataset_list[0]
    dataset = api.dataset.find_dataset_by_id(
        organization_id=organization_id,
        dataset_id=instance_dataset_id,
    )

    # Default path for ETL-generated datasets
    ws_file_path = f'datasets/{instance_dataset_id}/generated_brewery_instance.zip'
    if dataset.source_type == "None":
        try:
            ws_file_path = dataset.source.location
        except e:
            LOGGER.warning(f"Failed to get source.location from dataset {instance_dataset_id}, using default file path")

    LOGGER.info("Downloading instance dataset...")
    _file_content = api.workspace.download_workspace_file(organization_id, workspace_id, ws_file_path)

    with TemporaryDirectory() as tmp_dir:
        archive_path = os.path.join(tmp_dir, 'dataset.zip')
        with open(archive_path, "wb") as _file:
            _file.write(_file_content)

        LOGGER.info("Extracting instance dataset...")
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)
        shutil.unpack_archive(archive_path, data_folder)

    files = "\n".join([f" - {path}" for path in glob.glob(str(data_folder / "**"), recursive=True)])
    LOGGER.info(f"\nData files:\n{files}")

    temp_file = NamedTemporaryFile("w+t", newline="", delete=False)
    bar_file_path = data_folder / "Bar.csv"
    LOGGER.info("\nPatching dataset file Bar.csv with parameters values...")
    with open(bar_file_path, newline="") as bar_file:
        bar_reader = csv.reader(bar_file)
        bar_writer = csv.writer(temp_file)

        header = next(bar_reader)
        bar_writer.writerow(header)
        column_indices = {"stock": -1, "restock_qty": -1, "nb_waiters": -1}
        csv_column_mapping = {
            "Stock": "stock",
            "RestockQty": "restock_qty",
            "NbWaiters": "nb_waiters",
        }
        for index, column in enumerate(header):
            if column in csv_column_mapping:
                parameter_name = csv_column_mapping[column]
                column_indices[parameter_name] = index

        for row in bar_reader:
            for parameter_name, column_index in column_indices.items():
                if column_index == -1:
                    LOGGER.warning(f" - {parameter_name}: parameter never found in CSV header:")
                    LOGGER.warning(f'    - CSV header: "{header}"')
                    LOGGER.warning(f'    - column mapping: "{csv_column_mapping}"')
                    continue
                previous_value = row[column_index]
                new_value = values[parameter_name]
                row[column_index] = new_value
                LOGGER.info(f" - {parameter_name}: {previous_value} => {new_value}")
            bar_writer.writerow(row)

    temp_file.close()
    shutil.move(temp_file.name, bar_file_path)


if __name__ == "__main__":
    main()

import os
from zipfile import ZipFile
from pathlib import Path

from cosmotech.coal.utils.logger import get_logger
from cosmotech.coal.utils.configuration import Configuration
from cosmotech.coal.cosmotech_api.apis.runner import RunnerApi
from cosmotech.coal.cosmotech_api.apis.dataset import DatasetApi

LOGGER = get_logger('etl')


def get_zip_file_path(dir):
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".zip"):
                return Path(root) / file


def list_files(dir):
    for root, _, files in os.walk(dir):
        for file in files:
            yield Path(root) / file


def main():
    LOGGER.info("Starting the ETL Run")
    coal_config = Configuration()

    parameter_dir_path = Path(coal_config.cosmotech.parameters_absolute_path)
    extract_path = parameter_dir_path / "extract"
    with ZipFile(get_zip_file_path(parameter_dir_path)) as zip:
        zip.extractall(extract_path)

    runner_data = RunnerApi().get_runner_metadata()
    target_dataset_id = runner_data['datasets']['bases'][0]
    path_list_db = list_files(extract_path)
    datasetApi = DatasetApi()
    datasetApi.upload_dataset_parts(
        target_dataset_id, [], path_list_db, replace_existing=True
    )
    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    main()

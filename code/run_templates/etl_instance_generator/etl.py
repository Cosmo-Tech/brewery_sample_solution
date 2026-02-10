import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from cosmotech.coal.utils.logger import get_logger
from cosmotech.coal.utils.configuration import Configuration
from cosmotech.coal.cosmotech_api.apis.runner import RunnerApi
from cosmotech.coal.cosmotech_api.apis.dataset import DatasetApi
from generate_brewery_dataset import generate_brewery_dataset

LOGGER = get_logger('etl')


@dataclass
class GeneratorParameters:
    restock: str
    stock: str
    waiters: str
    satisfaction: str
    surrounding_satisfaction: str
    thirsty: str
    locale: str
    customers: str
    tables: str
    name: str = "brewery_instance"


def get_zip_file_name(dir):
    for _, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".zip"):
                return file


def main():
    LOGGER.info("Starting the ETL Run")
    coal_config = Configuration()

    with open(
        Path(coal_config.cosmotech.parameters_absolute_path) / "parameters.json"
    ) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}
    generator_parameters = GeneratorParameters(
        int(parameters["etl_param_restock_quantity"]),
        int(parameters["etl_param_stock"]),
        int(parameters["etl_param_num_waiters"]),
        int(parameters["etl_param_satisfaction"]),
        int(parameters["etl_param_surrounding_satisfaction"]),
        parameters["etl_param_thirsty"] == "THIRSTY",
        parameters["etl_param_locale"],
        int(parameters["etl_param_customers_count"]),
        int(
            parameters["etl_param_tables_count"],
        ),
    )
    LOGGER.info("All parameters are loaded")

    # When a runner is an ETL created by the webapp, the 1st item in datasetList is is a dataset created by the webapp
    # before starting the runner and is used as the target for the ETL
    runner_data = RunnerApi().get_runner_metadata(
        runner_id=coal_config.cosmotech.runner_id
    )
    target_dataset_id = runner_data['datasets']['bases'][0]
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate_brewery_dataset(generator_parameters, tmp_dir)
        path_tmp_dir = Path(tmp_dir)
        path_list_file = [
            path_tmp_dir / "arc_Satisfaction.csv",
            path_tmp_dir / "Bar_vertex.csv",
            path_tmp_dir / "Customer.csv",
        ]
        path_list_db = [path_tmp_dir / "Bar.csv"]
        DatasetApi().update_dataset_from_files(
            target_dataset_id, path_list_file, path_list_db
        )
    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    main()

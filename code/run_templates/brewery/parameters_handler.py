import json
import shutil
from pathlib import Path

from csv_handler import update_first_row_in_csv
from fetcher import fetch_parameter_file_path
from cosmotech.coal.utils.configuration import ENVIRONMENT_CONFIGURATION as EC
from cosmotech.orchestrator.utils.logger import get_logger

LOGGER = get_logger('parameters_handler')


def read_parameters():
    with open(
        Path(EC.cosmotech.parameters_absolute_path) / "parameters.json"
    ) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    LOGGER.info("Parameters loaded from JSON")
    return parameters


def main():
    LOGGER.info("Starting parameter handler")

    # get_parameter from json
    parameters = read_parameters()
    # update dataset Bar.csv with param
    updated_values = {}
    if "NbWaiters" in parameters:
        updated_values["NbWaiters"] = parameters["NbWaiters"]
    if "RestockQty" in parameters:
        updated_values["RestockQty"] = parameters["RestockQty"]
    if "Stock" in parameters:
        updated_values["Stock"] = parameters["Stock"]

    bar_data_path = Path(EC.cosmotech.dataset_absolute_path) / "Bar.csv"
    update_first_row_in_csv(bar_data_path, updated_values)
    LOGGER.info("Updated Bar.csv with parameters")

    # replace bar.csv if file is provided as parameter
    bar_param_path = fetch_parameter_file_path("initial_stock_dataset") / "initial_stock_dataset"
    if bar_data_path.exists():
        # replace dataset Bar.csv with parameter Bar.csv
        shutil.copy(bar_param_path, bar_data_path)
        LOGGER.info("Bar.csv replaced by given file")


if __name__ == "__main__":
    main()

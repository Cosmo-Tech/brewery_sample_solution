import json
import shutil
import csv
from pathlib import Path

from cosmotech.coal.utils.configuration import ENVIRONMENT_CONFIGURATION as EC
from cosmotech.orchestrator.utils.logger import get_logger

LOGGER = get_logger('parameters_handler')


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


def read_parameters():
    with open(
        Path(EC.cosmotech.parameters_absolute_path) / "parameters.json"
    ) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    LOGGER.info("Parameters loaded from JSON")
    return parameters


def fetch_parameter_file_path(param_name: str) -> Path:
    for r, d, f in os.walk(EC.cosmotech.parameters_absolute_path):
        if param_name in r:
            return Path(r) / f[0]
    raise FileNotFoundError(f"Parameter file for {param_name} not found.")


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

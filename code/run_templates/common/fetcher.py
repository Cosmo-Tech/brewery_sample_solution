import os
from pathlib import Path

from cosmotech.coal.utils.configuration import ENVIRONMENT_CONFIGURATION as EC


def fetch_dataset_file_path(dataset_name: str, dataset_id: str = "") -> Path:
    for r, d, f in os.walk(EC.cosmotech.dataset_absolute_path / dataset_id):
        if dataset_name in f:
            return Path(r) / dataset_name
    raise FileNotFoundError(f"File for {dataset_name} not found in {EC.cosmotech.dataset_absolute_path}.")


def fetch_parameter_file_path(param_name: str) -> Path:
    for r, d, f in os.walk(EC.cosmotech.parameters_absolute_path):
        if param_name in r:
            return Path(r) / f[0]
    raise FileNotFoundError(f"File for {param_name} not found in {EC.cosmotech.parameters_absolute_path}.")

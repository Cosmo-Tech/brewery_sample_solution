from cosmotech.orchestrator.utils.logger import get_logger
import shutil
import os
import pathlib
from cosmotech.coal.cosmotech_api.runner.datasets import download_dataset

LOGGER = get_logger("Brewery/DatasetV5")


ORG_ID = os.environ.get("CSM_ORGANIZATION_ID")
WS_ID = os.environ.get("CSM_WORKSPACE_ID")
RUNNER_ID = os.environ.get("CSM_RUNNER_ID")
RUN_ID = os.environ.get("CSM_RUN_ID")
SIM_DATA_PATH = os.environ["CSM_DATASET_ABSOLUTE_PATH"]

LOGGER.info("Downloading dataset content")

dataset_id = os.environ["CSM_DATASET_ID"]

_d_data = download_dataset(ORG_ID, WS_ID, dataset_id, False)

tmp_path = pathlib.Path(_d_data['folder_path'])

for _p in tmp_path.glob("*"):
    shutil.copy(_p, SIM_DATA_PATH)

LOGGER.info(f"Downloaded dataset {dataset_id}")
from cosmotech.orchestrator.utils.logger import get_logger
import shutil
import os
import pathlib
from cosmotech.coal.cosmotech_api.apis.dataset import DatasetApi

LOGGER = get_logger("Brewery/DatasetV5")


ORG_ID = os.environ.get("CSM_ORGANIZATION_ID")
WS_ID = os.environ.get("CSM_WORKSPACE_ID")
RUNNER_ID = os.environ.get("CSM_RUNNER_ID")
RUN_ID = os.environ.get("CSM_RUN_ID")
SIM_DATA_PATH = pathlib.Path(os.environ["CSM_DATASET_ABSOLUTE_PATH"])

LOGGER.info("Downloading dataset content")

dataset_id = os.environ["CSM_DATASET_ID"]
dataset_api = DatasetApi()
dataset_api.download_dataset(dataset_id)

shutil.copytree(SIM_DATA_PATH / dataset_id, "backup")
shutil.rmtree(SIM_DATA_PATH)
shutil.copytree("backup", SIM_DATA_PATH)

LOGGER.info(f"Downloaded dataset {dataset_id}")
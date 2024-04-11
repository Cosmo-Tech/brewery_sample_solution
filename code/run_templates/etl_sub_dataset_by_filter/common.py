import os
import logging
from rich.logging import RichHandler

import cosmotech_api
from azure.identity import DefaultAzureCredential
from cosmotech_api.api.dataset_api import DatasetApi
from cosmotech_api.api.runner_api import RunnerApi


LOGGER = logging.getLogger("my_etl_logger")
logging.basicConfig(
    format="[ETL] %(message)s",
    datefmt="[%Y/%m/%d-%X]",
    handlers=[RichHandler(rich_tracebacks=True, omit_repeated_times=False, show_path=False, markup=True)],
)
LOGGER.setLevel(logging.INFO)


def get_logger():
    return LOGGER


def get_api():
    credentials = DefaultAzureCredential()
    configuration = cosmotech_api.Configuration(
        host=os.environ.get("CSM_API_URL"),
        discard_unknown_keys=True,
        access_token=credentials.get_token(os.environ.get("CSM_API_SCOPE")).token,
    )

    with cosmotech_api.ApiClient(configuration) as api_client:
        dataset_api_instance = DatasetApi(api_client)
        runner_api_instance = RunnerApi(api_client)

    return {"dataset": dataset_api_instance, "runner": runner_api_instance}


def get_api_token():
    credentials = DefaultAzureCredential()
    return credentials.get_token(os.environ.get("CSM_API_SCOPE")).token

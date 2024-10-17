import os

from azure.identity import DefaultAzureCredential
from cosmotech_api.api.dataset_api import DatasetApi
from cosmotech_api.api.runner_api import RunnerApi
from cosmotech.coal.cosmotech_api.connection import get_api_client
from cosmotech.coal.utils.logger import get_logger as _get_logger


LOGGER = _get_logger("my_etl_logger")


def get_logger():
    return LOGGER


def get_api():
    api_client, api_client_name = get_api_client()
    LOGGER.info(f"Using API client '{api_client_name}'")

    dataset_api_instance = DatasetApi(api_client)
    runner_api_instance = RunnerApi(api_client)

    return {"dataset": dataset_api_instance, "runner": runner_api_instance}


def get_api_token():
    credentials = DefaultAzureCredential()
    return credentials.get_token(os.environ.get("CSM_API_SCOPE")).token


def get_authentication_header():
    api_client, api_client_name = get_api_client()
    api_key = os.environ.get("CSM_API_KEY")

    if api_key is not None:
        # Craft header with API key
        header_name = os.environ.get("CSM_API_KEY_HEADER", "X-CSM-API-KEY")
        return {header_name: api_key}

    # Craft header for Bearer token
    token = get_api_token()
    auth_value = f"Bearer {token}"
    return {"Authorization": auth_value}

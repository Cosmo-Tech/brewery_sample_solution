import os
from time import perf_counter
from cosmotech.orchestrator.utils.logger import get_logger
from cosmotech.coal.cosmotech_api.apis import DatasetApi
from generate_csv_files import generate_file

LOGGER = get_logger("TEST")
LOGGER.info("Generating data")

generate_file("10KB_wide.csv", "10KB", "wide")

D_NAME = "Test_data"
D_PATH = "10KB_wide.csv"

d_api = DatasetApi()

r1 = d_api.upload_dataset(D_NAME, list(), list((D_PATH,)))

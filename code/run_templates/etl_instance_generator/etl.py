import csv
import json
import os
import sys
import shutil
import tempfile
from dataclasses import dataclass

from cosmotech_api.model.dataset import Dataset
from common.common import get_logger, get_api
from generate_brewery_dataset import generate_brewery_dataset


LOGGER = get_logger()


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
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    api = get_api()

    runner_data = api.runner.get_runner(
        organization_id=organization_id,
        workspace_id=os.environ.get("CSM_WORKSPACE_ID"),
        runner_id=os.environ.get("CSM_RUNNER_ID"),
    )
    # When a runner is an ETL created by the webapp, the 1st item in datasetList is is a dataset created by the webapp
    # before starting the runner
    target_dataset_id = runner_data.dataset_list[0]

    with open(os.path.join(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH"), "parameters.json")) as f:
        parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}
    LOGGER.info("All parameters are loaded")

    generator_parameters = GeneratorParameters(
        int(parameters["etl_param_restock_quantity"]),
        int(parameters["etl_param_stock"]),
        int(parameters["etl_param_num_waiters"]),
        int(parameters["etl_param_satisfaction"]),
        int(parameters["etl_param_surrounding_satisfaction"]),
        parameters["etl_param_thirsty"] == "THIRSTY",
        parameters["etl_param_locale"],
        int(parameters["etl_param_customers_count"]),
        int(parameters["etl_param_tables_count"],)
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        generate_brewery_dataset(generator_parameters, tmp_dir)
        output_file_path = os.path.join(tmp_dir, "generated_brewery_instance")
        output_file_path_with_format = os.path.join(tmp_dir, "generated_brewery_instance.zip")
        shutil.make_archive(output_file_path, "zip", tmp_dir)
        LOGGER.info(f"Instance archive gerenated: {output_file_path_with_format}")

        ws_file_path = f'datasets/{target_dataset_id}/generated_brewery_instance.zip'
        LOGGER.info(f"Starting workspace file upload to {ws_file_path}...")
        ws_file = api.workspace.upload_workspace_file(organization_id,
                                                     os.environ.get("CSM_WORKSPACE_ID"),
                                                     output_file_path_with_format,
                                                     overwrite=True,
                                                     destination=ws_file_path)
        LOGGER.info("Workspace file has been uploaded")

    api.dataset.update_dataset(
        organization_id, target_dataset_id, {"ingestionStatus": "SUCCESS", "twincacheStatus":"FULL"}
    )
    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exception_type = type(e).__name__
        file_name = os.path.split(e.__traceback__.tb_frame.f_code.co_filename)[1]
        line_number = e.__traceback__.tb_lineno
        LOGGER.error(f"An error occured during the dataset generation: {exception_type}")
        LOGGER.error('%s' % e)
        sys.exit(-1)

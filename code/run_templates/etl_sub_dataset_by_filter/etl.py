# import json
import os
import sys

import common
from create_subdataset import create_subdataset


LOGGER = common.get_logger()


def main():
    LOGGER.info("Starting the ETL Run")
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    workspace_id = os.environ.get("CSM_WORKSPACE_ID")
    runner_id = os.environ.get("CSM_RUNNER_ID")

    api = common.get_api()
    runner = api['runner'].get_runner(organization_id=organization_id, workspace_id=workspace_id, runner_id=runner_id)
    parent_dataset_id = runner['dataset_list'][0]

    # LOGGER.info("Loading parameters")
    # with open(os.path.join(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH"), "parameters.json")) as f:
    #     parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}

    create_subdataset(organization_id, parent_dataset_id)
    # subdataset = create_subdataset(organization_id, parent_dataset_id, subdataset_details) # TODO

    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOGGER.error("An error occured during the creation of the sub-dataset: %s\n" % e)
        sys.exit(-1)

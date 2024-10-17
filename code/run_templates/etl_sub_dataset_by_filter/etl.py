import os
import sys

from common.common import get_logger, get_api
from create_subdataset import create_subdataset_into


LOGGER = get_logger()


def main():
    LOGGER.info("Starting the ETL Run")
    organization_id = os.environ.get("CSM_ORGANIZATION_ID")
    workspace_id = os.environ.get("CSM_WORKSPACE_ID")
    runner_id = os.environ.get("CSM_RUNNER_ID")

    runner = api.runner.get_runner(organization_id=organization_id, workspace_id=workspace_id, runner_id=runner_id)
    subdataset_id = runner.dataset_list[0]
    parent_dataset_id = runner.dataset_list[1]
    subdataset_details = {"name": runner.name, "description": runner.description}

    # TODO generate "queries" from parameters
    # LOGGER.info("Loading parameters")
    # with open(os.path.join(os.environ.get("CSM_PARAMETERS_ABSOLUTE_PATH"), "parameters.json")) as f:
    #     parameters = {d["parameterId"]: d["value"] for d in json.loads(f.read())}
    queries = None

    create_subdataset_into(
        organization_id,
        workspace_id,
        parent_dataset_id,
        subdataset_id,
        subdataset_details,
        queries,
    )
    LOGGER.info("ETL Run finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        LOGGER.error("An error occured during the creation of the sub-dataset: %s\n" % e)
        sys.exit(-1)

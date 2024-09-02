import time
import cosmotech_api

from common.common import get_logger, get_api
from common.twingraph import copy_dataset_twingraph

LOGGER = get_logger()


def load_env_variables():
    from dotenv import load_dotenv

    load_dotenv()
    # Example of .env file required to run this script
    # CSM_API_URL="https://dev.api.cosmotech.com/phoenix/v3-0"
    # CSM_API_SCOPE="http://dev.api.cosmotech.com/.default"
    # AZURE_TENANT_ID="<insert your tenant id here>"
    # AZURE_CLIENT_ID="<insert your client id here>"
    # AZURE_CLIENT_SECRET="<insert the client secret here>"
    # CSM_ORGANIZATION_ID="<insert your organization id here>"
    # CSM_WORKSPACE_ID="<insert your workspace id here>"


def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a subdataset from a parent dataset and a list of filter arguments."
    )
    parser.add_argument("-o", "--organization", help="Organization id", required=True)
    parser.add_argument("-w", "--workspace", help="Workspace id", required=True)
    parser.add_argument("-p", "--parent", help="Id of the parent dataset", required=True)
    parser.add_argument(
        "-s",
        "--subdataset",
        help="Id of the subdataset (leave undefined to create a new dataset)",
    )
    parser.add_argument("-n", "--name", help="Name of the created subdataset")
    parser.add_argument("-d", "--description", help="Description of the created subdataset")
    return parser.parse_args()


def get_dataset(organization_id, dataset_id):
    api = get_api()
    try:
        return api["dataset"].find_dataset_by_id(organization_id, dataset_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error(f"Failed to retrieve dataset with id {dataset_id}: %s\n" % e)
        raise e


def create_subdataset(organization_id, workspace_id, parent_dataset_id, subdataset_details, queries=None):
    api = get_api()
    queries = queries or [
        "OPTIONAL MATCH(n) RETURN n",
        "OPTIONAL MATCH(src)-[edge]->(dst) RETURN src, edge, dst",
    ]
    try:
        parent_dataset = get_dataset(organization_id, parent_dataset_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error(f"Failed to retrieve parent dataset with id {parent_dataset_id}: %s\n" % e)
        raise e

    LOGGER.info("Preparing creation of the subdataset...")
    parent_dataset_name = parent_dataset.name or ""
    parent_dataset_description = parent_dataset.description or parent_dataset_name  # Description filler
    subdataset_graph_query_as_dict = {
        "name": subdataset_details["name"] or f"Subdataset of {parent_dataset_name}",
        "description": subdataset_details["description"] or f"(Subdataset) {parent_dataset_description}",
        "queries": queries,
        "main": True,
    }

    LOGGER.info("Creating subdataset...")
    try:
        subdataset = api["dataset"].create_sub_dataset(
            organization_id, parent_dataset_id, subdataset_graph_query_as_dict
        )
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to create subdataset: %s\n" % e)
        raise e
    subdataset_id = subdataset.id
    LOGGER.info(f'Sub dataset created, its id is "{subdataset_id}"')

    time.sleep(2)  # Delay first status query to make sure back-end had time to init (see #SDCOSMO-1768 for example)
    LOGGER.info("Starting status polling...")
    ingestion_status = "PENDING"
    max_polling_count = 20
    polling_count = 0
    while polling_count < max_polling_count:
        polling_count += 1

        ingestion_status = api["dataset"].get_dataset_twingraph_status(organization_id, subdataset_id)
        LOGGER.info(ingestion_status)
        if ingestion_status != "PENDING":
            break
        time.sleep(5)

    if ingestion_status != "SUCCESS":
        LOGGER.error(
            f'Status of created subdataset is "{ingestion_status}". Please check dataset "{subdataset_id}"for details'
        )
        raise Exception("Subdataset creation failed")
    LOGGER.info("Subdataset content is ready")

    LOGGER.info("Linking subdataset to workspace...")
    try:
        api["dataset"].link_workspace(organization_id, subdataset_id, workspace_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to create subdataset: %s\n" % e)
        raise e

    subdataset_id = subdataset.id
    LOGGER.info(f"Subdataset ready! ({subdataset_id})")
    return (subdataset, parent_dataset)


def create_subdataset_into(
    organization_id,
    workspace_id,
    parent_dataset_id,
    subdataset_id,
    subdataset_details,
    queries,
):
    (tmp_subdataset, parent_dataset) = create_subdataset(
        organization_id, workspace_id, parent_dataset_id, subdataset_details, queries
    )

    # Note: this is a work-around for missing endpoint copyDataset in the API, or until a "target dataset id" can
    # be specified in the subdataset endpoint
    copy_dataset_twingraph(organization_id, tmp_subdataset.id, subdataset_id)

    # Delete temporary dataset only now that its content has been reuploaded
    tmp_subdataset_id = tmp_subdataset.id
    LOGGER.info(f'Deleting temporary dataset "{tmp_subdataset_id}"...')
    api = get_api()
    try:
        api["dataset"].delete_dataset(organization_id, tmp_subdataset_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error(f'Failed to delete temporary dataset with id "{tmp_subdataset_id}": %s\n' % e)
        raise e
    LOGGER.info("Temporary dataset removed")


if __name__ == "__main__":
    # Only when running locally: load .env file & parse script parameters
    load_env_variables()
    args = parse_arguments()

    queries = None  # TODO write queries

    subdataset_details = {"name": args.name, "description": args.description}
    if args.subdataset is None:
        create_subdataset(args.organization, args.workspace, args.parent, subdataset_details, queries)
    else:
        create_subdataset_into(
            args.organization,
            args.workspace,
            args.parent,
            args.subdataset,
            subdataset_details,
            queries,
        )

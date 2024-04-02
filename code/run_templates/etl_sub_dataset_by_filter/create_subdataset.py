import cosmotech_api
from cosmotech_api.model.sub_dataset_graph_query import SubDatasetGraphQuery

import common


LOGGER = common.get_logger()


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
        description='Create a subdataset from a parent dataset and a list of filter arguments.'
    )
    parser.add_argument("-o", "--organization", help="Organization id", required=True)
    parser.add_argument("-w", "--workspace", help="Workspace id", required=True)
    parser.add_argument("-p", "--parent", help="Id of the parent dataset", required=True)
    parser.add_argument("-n", "--name", help="Name of the created subdataset")
    parser.add_argument("-d", "--description", help="Description of the created subdataset")
    return parser.parse_args()


def create_subdataset(organization_id, workspace_id, parent_dataset_id, subdataset_details):
    api = common.get_api()

    try:
        parent_dataset = api['dataset'].find_dataset_by_id(organization_id, parent_dataset_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error(f"Failed to retrieve parent dataset with id {parent_dataset_id}: %s\n" % e)
        raise e

    LOGGER.info("Preparing creation of the subdataset...")
    parent_dataset_name = parent_dataset['name'] or ''
    parent_dataset_description = parent_dataset['description'] or parent_dataset_name  # Description filler
    subdataset_graph_query = SubDatasetGraphQuery(
        name=subdataset_details['name'] or f'Subdataset of {parent_dataset_name}',
        description=subdataset_details['description'] or f'(Subdataset) {parent_dataset_description}',
        queries=["MATCH (n) RETURN n"],
        main=True,
    )

    LOGGER.info("Creating subdataset...")
    try:
        subdataset = api['dataset'].create_sub_dataset(organization_id, parent_dataset_id, subdataset_graph_query)
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to create subdataset: %s\n" % e)
        raise e

    LOGGER.info("Linking subdataset to workspace...")
    try:
        api['dataset'].link_workspace(organization_id, subdataset['id'], workspace_id)
    except cosmotech_api.ApiException as e:
        LOGGER.error("Failed to create subdataset: %s\n" % e)
        raise e

    LOGGER.info(f"Subdataset ready! ({subdataset['id']})")
    return subdataset


if __name__ == "__main__":
    # Only when running locally: load .env file & parse script parameters
    load_env_variables()
    args = parse_arguments()
    subdataset_details = {"name": args.name, "description": args.description}
    dataset = create_subdataset(args.organization, args.workspace, args.parent, subdataset_details)

# Usage

When running locally, you will need a .env file with the following data (you may have to adapt the example values below):
```
CSM_API_URL="https://dev.api.cosmotech.com/phoenix/v3-1"
CSM_API_SCOPE="http://dev.api.cosmotech.com/.default"
AZURE_TENANT_ID="<insert your tenant id here>"
AZURE_CLIENT_ID="<insert your client id here>"
AZURE_CLIENT_SECRET="<insert the client secret here>"
CSM_ORGANIZATION_ID="<insert your organization id here>"
CSM_WORKSPACE_ID="<insert your workspace id here>"
```

This run template can be run locally with:
`python3 create_subdataset.py -o <organization_id> -p <parent_dataset_id> -w <workspace_id> -n "My Subdataset"`

If you already have a dataset created and want to write the content of the sub-dataset in it, you can use the `-s` parameter:
`python3 create_subdataset.py -o <organization_id> -p <parent_dataset_id> -w <workspace_id> -s <subdataset_id> -n "My Subdataset"`

For the full list of options, you can use `python3 create_subdataset.py --help`

# Create resources on tenant initialization:

## Pre-requisites

- install restish and jq
- configure restish for your tenant

## Tenant setup

### Organization

```
# Create organization (loop until a correct id is generated)
restish post -H content-type:application/yaml https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations < Organization.yaml | jq -r '.id'
# List all organization ids
restish get https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations | jq -r '.[].id'
# Delete unused organizations
restish delete https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<id of organization to delete>
```

### Solution

```
# Create solution (loop until a correct id is generated)
restish post -H content-type:application/yaml https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org_id>/solutions < Solution.yaml | jq -r '.id'
# List all solution ids
restish get https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org_id>/solutions | jq -r '.[].id'
# Delete unused solutions
restish delete https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org_id>/solutions/<id of solution to delete>
```

### Workspaces

```
# Create workspaces
restish post -H content-type:application/yaml https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org id>/workspaces < Workspace-dev0.yaml
restish post -H content-type:application/yaml https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org id>/workspaces < Workspace-dev1.yaml
restish post -H content-type:application/yaml https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org id>/workspaces < Workspace-dev2.yaml

# Or, do it in a loop and clean workspace afterwards
for i in {1..35}; do restish post -H content-type:application/yaml https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/o-064yp2y9jvp/workspaces < Workspace-dev0.yaml; done

# Dont forget to path the workspaces you want to keep with the 3 files Workspace-dev*.yaml
```

### Datasets

Repeat the instructions below for each workspace

```
# Add an env var with a valid bearer token
BEARER_TOKEN=""

# Take note of the id of the dataset that is created for the next command
curl "https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org id>/workspaces/<workspace id>/datasets" \
  -X POST \
  -H "Authorization: $BEARER_TOKEN" \
  -F datasetCreateRequest=@WorkspaceSolutionDataset.json

curl -v "https://aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/api/organizations/<org id>/workspaces/<workspace id>/datasets/<dataset id>/parts" \
  -X POST \
  -H "Authorization: $BEARER_TOKEN" \
  -F datasetPartCreateRequest=@WorkspaceSolutionDatasetPart.json -F file=@default_events.csv


```

# Cosmo Tech resources configuration

Please note that some operations described below require that you have the Platform.Admin role in the Cosmo Tech
platform.

## Organization

_If you already have an organization, you can skip this part and jump to the solution creation._

`POST` - `/organizations`

Use swagger to create a new organization based on the file [Organization.json](Organization.json). Keep the id of the
created organization, we may need it later.

## Solution

`POST` - `/organizations/{organization_id}/solutions`

Use swagger to register a new solution based on this file: [Solution.json](Solution.json). Keep the id of the created
solution, we may need it later.

## Workspace

`POST` - `/organizations/{organization_id}/workspaces`

Copy the content of the file [Workspace.json](Workspace.json), and adapt its content:

- **replace the `solutionId`** by the id of your solution
- **change the ids** of the PowerBI workspace, reports and pages

Use swagger to upload the new workspace description and register a new workspace. Keep the id of the created workspace,
we may need it later.

In the kubernetes cluster, you may have to **create a new secret** named from the pattern
`<organizationId>-<workspaceId>`. This is sometimes a requirement of the run templates, to set some environment
variables (e.g. the credentials of the posqtgresql database).

## Datasets

In this section, we will create two datasets that we can later use to create scenarios. First, we will start by the
**upload of ZIP archives as "workspace files"**. Then, we will **create two Dataset resources** pointing to the path where the workspace files have been uploaded.

### Workspace files

`POST` - `/organizations/{organization_id}/workspaces/{workspace_id}/files`

Use swagger to upload two workspace files.

First file:

- file to upload: [dataset1.zip](dataset1.zip)
- destination: `datasets/dataset1.zip`

Second file:

- file to upload: [dataset2.zip](dataset2.zip)
- destination: `datasets/dataset2.zip`

If the upload has succeeded, you should receive a response similar to:

```json
{
  "fileName": "datasets/dataset1.zip"
}
```

### Main datasets

`POST` - `/organizations/{organization_id}/datasets`

Use swagger to **create** a first dataset, based on the file [Dataset1.json](Dataset1.json), and keep the id of the created
dataset. Then, do the same with the content of the file [Dataset2.json](Dataset2.json), and keep the id of the second
dataset.

`PATCH` - `/organizations/{organization_id}/datasets/{dataset_id}`

Use swagger to **update each created dataset**, by reusing the same JSON files (this step is required to set the
values of `ingestionStatus` and `twincacheStatus`, that are not correctly set during the dataset creation).

`POST` - `/organizations/{organization_id}/datasets/{dataset_id}/link`

Finally, use swagger to **link the two created datasets to your workspace**.

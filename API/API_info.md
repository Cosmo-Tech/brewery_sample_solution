// Deployment of the simulator in the registry.

### Connect to the container registry:
```shell
az login
az acr login -n csmenginesdev
```
### Build the solution (with latest version of sdk and Debian 11) and push it to container repository:
```shell
csm clean
csm flow –-python
csm twin-engine docker release $version --registry csmenginesdev.azurecr.io/
```

### Cosmo Tech platform
- Organization: `O-gZYpnd27G7`
- Workspace: `w-po901kxqow13j`
- Solution: `sol-2wdr4gpzw94ql`
- Workspace key: `OptimBenchmarkWorkspace`
- Scenario: ``

### API
Platform URL : https://dev.api.cosmotech.com/
Swagger client id : 5e99835b-4ccd-4c16-84c7-e9796be10772

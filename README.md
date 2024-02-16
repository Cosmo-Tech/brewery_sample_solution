# Brewery sample solution

Branch release/0.0.x exists to support Cosmo Tech API v2.x
If you are using v3 of the API, consider using a brewery simulator version >= 1.0.0

## Build

With CoSMo Studio installed and csm available in your path, you can build the project with the commands:

```
csm clean
csm flow --docker
```

## Deploy

To create & publish a new simulator image, use:

```
az login
az acr login -n csmenginesdev
csm docker release --tag <x.y.z> --registry csmenginesdev.azurecr.io/
```

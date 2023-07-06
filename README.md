# Brewery sample solution

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

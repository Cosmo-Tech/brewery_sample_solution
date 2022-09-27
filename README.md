# Brewery sample solution

## Build

With CoSMo Studio installed and csm available in your path, you can build the project with the commands:

```
csm clean
csm flow
```

## Deploy

To create & publish a new simulator image, use:

```
az login
az acr login -n csmenginesdev
csm twin-engine docker release <x.y.z> --registry csmenginesdev.azurecr.io/
```

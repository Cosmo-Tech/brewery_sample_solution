# Brewery sample solution

## Build

With CoSMo Studio installed and csm available in your path, you can build the project with the commands:

```
csm clean
csm flow --docker
```

## Run simulation

Once the docker image is built, you can use it to list the available simulations with:

```
csm docker run --rm brewery_simulator -- -l
```

and run a local simulation (using the predefined tutorial data) with:

```
csm docker run --rm brewery_simulator -- -i BreweryTutorialSimulation
```

## Deploy

To publish a new simulator image, use:

```
az login
az acr login -n csmenginesdev
csm docker release --tag <x.y.z> --registry csmenginesdev.azurecr.io/
```

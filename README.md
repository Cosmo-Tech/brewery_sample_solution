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

## Run with run-orchestrator

Install dependencies and run
```
uv pip install -r code/requirements.txt
csm-orc run code/run_templates/minimal/run.json 
```


## Deploy

To publish a new simulator image, use:

```
az login
az acr login -n acrwarpwaadxdevdlrivo
csm docker release --tag 3.0.0-dev.3 --registry acrwarpwaadxdevdlrivo.azurecr.io/

az acr login -n acrsphinxd38ygr
csm docker release --tag 3.0.0-dev.3 --registry acrsphinxd38ygr.azurecr.io/
```

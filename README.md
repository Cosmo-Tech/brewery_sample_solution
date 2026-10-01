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
pip install -r code/requirements.txt
csm-orc run code/run_templates/minimal/run.json
```


## Deploy

Publish the new simulator image to the desired registries:

```
docker login aks-dev-joy.azure.platform.cosmotech.com -u <username>
csm docker release --tag brewery-x.y.z --registry aks-dev-joy.azure.platform.cosmotech.com/tenant-business-webapp/
```

## Release

- Make sure that the version is updated in Simulator/Simulator.sor.xml
- Make sure all tests pass, vulnerabilities and code issues are solved
- Run Jenkins job [Release-Brewery](https://jenkins.cosmotech.com/job/Solutions/job/Release-Brewery/)
import comets as co
import os
from CosmoTech_Acceleration_Library.Accelerators.adx_wrapper import ADXQueriesWrapper
import shutil
import pandas as pd
from pathlib import Path

# retrieving the csv from the adt
adt_folder = os.environ.get("CSM_DATASET_ABSOLUTE_PATH", None)
if os.path.isdir("/pkg/share/Simulation/Resource/CSVSimulationLoaders"):
    shutil.rmtree("/pkg/share/Simulation/Resource/CSVSimulationLoaders")
if adt_folder is not None:
    # Copy adt_folder (with files written by the parameters_handler) to folder /pkg/share/Simulation/Resource/CSVSimulationLoaders
    shutil.copytree(
        adt_folder,
        "/pkg/share/Simulation/Resource/CSVSimulationLoaders",
    )

# retrieving the parameter "targeted stock" from the web app
parametersPath = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
parametersFile = parametersPath / "parameters.csv"
df_parameters = pd.read_csv(parametersFile)
target = int(df_parameters["value"][0])


def encoder(parameters):
    return {
        "Model::{Entity}MyBar::@NbWaiters": parameters["NbWaiters"],
        "Model::{Entity}MyBar::@RestockQty": parameters["RestockQty"],
    }


def get_outcomes(simulator):
    outputs = simulator.get_outputs(["Model::{Entity}MyBar::@Stock"])
    stock = outputs["Model::{Entity}MyBar::@Stock"]
    return {"ObjectiveFunction": (stock - target) ** 2}


def main():
    simulator = co.CosmoInterface(simulator_path="BreweryDemoSimulationNext")

    optimtask = co.ModelTask(simulator, get_outcomes=get_outcomes, encode=encoder)

    space = [
        {
            "name": "NbWaiters",
            "type": "int",
            "bounds": [1, 12],
        },
        {
            "name": "RestockQty",
            "type": "int",
            "bounds": [1, 50],
        },
    ]

    opt = co.Optimization(
        space=space,
        task=optimtask,
        algorithm="CMAES",
        stop_criteria={"max_evaluations": 150},
        n_jobs=-2,
        maximize=False,
    )

    opt.run()

    # Running a simple simulation with the optimal decision variable
    simulator2 = co.CosmoInterface(
        simulator_path="BreweryDemoSimulationNext",
        amqp_consumer_address=os.environ.get("CSM_PROBES_MEASURES_TOPIC", None),
        simulation_name=os.environ.get("CSM_SIMULATION_VAR", "Simulation"),
    )
    print("là", os.environ.get("CSM_PROBES_MEASURES_TOPIC", None), flush=True)
    print("ici", os.environ.get("CSM_SIMULATION_ID"), flush=True)

    simulator2.initialize()
    optimal_decision_variable = {
        "Model::{Entity}MyBar::@NbWaiters": opt.results["Optimal variables"][
            "NbWaiters"
        ],
        "Model::{Entity}MyBar::@RestockQty": opt.results["Optimal variables"][
            "RestockQty"
        ],
    }
    simulator2.set_inputs(optimal_decision_variable)
    simulator2.run()
    simulator2.terminate()

    # Creating the dic of results that will be sent to adx
    opt_results = [
        {
            "NbWaiters": opt.results["Optimal variables"]["NbWaiters"],
            "RestockQty": opt.results["Optimal variables"]["RestockQty"],
            "ObjectiveFunction": opt.results["Optimal values"]["ObjectiveFunction"],
            "Target": target,
            "SimulationRun": str(os.environ.get("CSM_SIMULATION_ID", None)),
        }
    ]

    # retrieving the environment variable
    adx_parameters = {
        "uri": os.environ.get("AZURE_DATA_EXPLORER_RESOURCE_URI", None),
        "ingest-uri": os.environ.get("AZURE_DATA_EXPLORER_RESOURCE_INGEST_URI", None),
        "database": os.environ.get("AZURE_DATA_EXPLORER_DATABASE_NAME", None),
    }

    # creating the ADX connector
    adx_connector = ADXQueriesWrapper(
        database=adx_parameters["database"],
        cluster_url=adx_parameters["uri"],
        ingest_url=adx_parameters["ingest-uri"],
    )

    # Sending the results to ADX
    adx_connector.send_to_adx(
        dict_list=opt_results,
        table_name="Optimization_results",
        drop_by_tag=os.environ["CSM_SIMULATION_ID"],
    )


if __name__ == "__main__":
    main()

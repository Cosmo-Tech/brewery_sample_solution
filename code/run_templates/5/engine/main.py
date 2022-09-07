import comets as co
import os
from CosmoTech_Acceleration_Library.Accelerators.adx_wrapper import ADXQueriesWrapper


def encoder(parameters):
    return {
        "Model::{Entity}MyBar::@NbWaiters": parameters["NbWaiters"],
        "Model::{Entity}MyBar::@RestockQty": parameters["RestockQty"],
    }


def get_outcomes(simulator):
    outputs = simulator.get_outputs(["Model::{Entity}MyBar::@Stock"])
    stock = outputs["Model::{Entity}MyBar::@Stock"]
    return {"ObjectiveFunction": (stock - 40) ** 2}


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
        n_jobs=8,
        maximize=False,
    )

    opt.run()

    # Creating the dic of results that will be sent to adx
    opt_results = [
        {
            "NbWaiters": opt.results["Optimal variables"]["NbWaiters"],
            "RestockQty": opt.results["Optimal variables"]["RestockQty"],
            "ObjectiveFunction": opt.results["Optimal values"]["ObjectiveFunction"],
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

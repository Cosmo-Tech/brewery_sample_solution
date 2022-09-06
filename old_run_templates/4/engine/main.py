import comets as co
import os
from CosmoTech_Acceleration_Library.Accelerators.adx_wrapper import ADXQueriesWrapper


# encoder for the ua
def encoder(parameters):
    return {
        "Model::{Entity}MyBar::@NbWaiters": parameters["NbWaiters"],
        "Model::{Entity}MyBar::@RestockQty": parameters["RestockQty"],
    }


# QuantityOfInterest for the ua
def QuantityOfInterest(simulator):
    outputs = simulator.get_outputs(
        ["Model::{Entity}MyBar::@AverageSatisfaction", "Model::{Entity}MyBar::@Stock"]
    )
    AverageSatisfaction = outputs["Model::{Entity}MyBar::@AverageSatisfaction"]
    stock = outputs["Model::{Entity}MyBar::@Stock"]
    return {"AverageSatisfaction": AverageSatisfaction, "Stock": stock}


def main():
    simulator = co.CosmoInterface(simulator_path="BreweryTutorialSimulation")

    uncertaintytask = co.ModelTask(
        simulator, get_outcomes=QuantityOfInterest, encode=encoder
    )

    sampling = [
        {
            "name": "NbWaiters",
            "sampling": "discreteuniform",
            "parameters": {"low": 1, "high": 5},
        },
        {
            "name": "RestockQty",
            "sampling": "discreteuniform",
            "parameters": {"low": 5, "high": 16},
        },
    ]

    ua = co.UncertaintyAnalysis(
        task=uncertaintytask,
        sampling=sampling,
        n_jobs=6,
        stop_criteria={"max_evaluations": 500},
    )

    ua.run()

    # Reformating the results format
    ua.results["statistics"].reset_index(inplace=True)
    ua.results["statistics"].rename(columns={"index": "KPI"})
    ua.results["statistics"]["SimulationRun"] = str(
        os.environ.get("CSM_SIMULATION_ID", None)
    )

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

    # Sending the results of the UA"
    adx_connector.send_to_adx(
        dict_list=ua.results["statistics"],
        table_name="Uncertainty_Analysis_results",
        drop_by_tag=os.environ["CSM_SIMULATION_ID"],
    )


if __name__ == "__main__":
    main()
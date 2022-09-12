import comets as co
import os
from CosmoTech_Acceleration_Library.Accelerators.adx_wrapper import ADXQueriesWrapper
import shutil
from pathlib import Path
import pandas as pd

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

# retrieving the number of evaluation from the web app
parametersPath = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
parametersFile = parametersPath / "parameters.csv"
df_parameters = pd.read_csv(parametersFile)
nb_simulation = int(df_parameters.iloc[0, 1])
df_bar = pd.read_csv("/pkg/share/Simulation/Resource/CSVSimulationLoaders/Bar.csv")


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
    simulator = co.CosmoInterface(simulator_path="BreweryDemoSimulationNext")

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
        n_jobs=-2,
        stop_criteria={"max_evaluations": nb_simulation},
        save_task_history=True,
    )

    ua.run()

    # Creating a table with the row data for the boxplot in power BI
    row_results = []
    count = 0
    for elements in ua.task_history["outputs"]:
        count += 1
        row_results.append(
            {
                "AverageSatisfaction": elements["AverageSatisfaction"],
                "Stock": elements["Stock"],
                "Label": count,
                "SimulationRun": str(os.environ.get("CSM_SIMULATION_ID", None)),
            }
        )

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

    # Sending the row results of the UA"
    adx_connector.send_to_adx(
        dict_list=row_results,
        table_name="Uncertainty_Analysis_row_results",
        drop_by_tag=os.environ["CSM_SIMULATION_ID"],
    )


if __name__ == "__main__":
    main()

from traceback import FrameSummary
import comets as co
import os
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


def main():
    simulator = co.CosmoInterface(
        simulator_path="BreweryDemoSimulationNext",
        amqp_consumer_address=os.environ.get("CSM_PROBES_MEASURES_TOPIC", None),
        simulation_name=os.environ.get("CSM_SIMULATION_VAR", "Simulation"),
    )

    simulator.initialize()
    simulator.run()
    simulator.terminate()


if __name__ == "__main__":
    main()

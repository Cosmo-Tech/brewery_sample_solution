from pathlib import Path
import pandas as pd
import os


# retrieving the parameter "number of waiters" from the web app
parametersPath = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
parametersFile = parametersPath / "parameters.csv"
df_parameters = pd.read_csv(parametersFile)
nb_waiters = int(df_parameters["value"][1])

# applying this parameter to the csv files from the adt
adt_folder = os.environ.get("CSM_DATASET_ABSOLUTE_PATH", None)
df_bar = pd.read_csv(adt_folder + "/Bar.csv")
df_bar["NbWaiters"][0] = nb_waiters
df_bar.to_csv(adt_folder + "/Bar.csv")

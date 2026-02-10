import os
import generate_dataset

generate_dataset.generate_data(os.environ.get("CSM_DATASET_ABSOLUTE_PATH"))
